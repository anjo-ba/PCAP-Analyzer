import json
from typing import Union, List, Dict, Set
from urllib import request
from urllib.error import HTTPError
from urllib.request import urlopen

from main.enrichers.enricher import Enricher
from main.helpers import string_helper
from main.helpers.combine_helper import CombineHelper
from main.helpers.file import file_read_helper


class ThreatInfoEnricher(Enricher):
    def __init__(self):
        header = "threat_category"
        enricher_type = "threat enricher"
        Enricher.__init__(self, enricher_type, header)

        self.threat_dict = {"": ""}
        self.threat_type_dict = {
            "": "",
            "THREAT_TYPE_UNSPECIFIED": "1",
            "MALWARE": "2",
            "SOCIAL_ENGINEERING": "3",
            "UNWANTED_SOFTWARE": "4",
            "POTENTIALLY_HARMFUL_APPLICATION": "5"
        }
        self.api_key = self.get_api_key()
        self.is_api_key_correct = True

    @staticmethod
    def get_api_key() -> str:
        config_name = "traffic-analyzer.conf"
        key = "safe_browsing_api_key"
        return file_read_helper.get_config_value(config_name, key)

    def test_urls_threats(self, urls) -> str:
        url_array = urls.split(",")
        url_array = list(map(string_helper.remove_quotations, url_array))

        if all(url == "" for url in url_array):
            return '""'

        filtered_urls = list(filter(lambda url: url not in self.threat_dict, url_array))
        for url in filtered_urls:
            self.threat_dict[url] = ""

        self.get_urls_threat_infomation(filtered_urls)
        matched_threat_types = self.reduce_threat_information(url_array)
        threat_numbers = list(map(self.get_threat_number, matched_threat_types))
        return CombineHelper.join_with_quotes(threat_numbers)

    def get_urls_threat_infomation(self, urls) -> None:
        if self.is_api_key_correct and urls and self.api_key != "":
            req = request.Request("https://safebrowsing.googleapis.com/v4/threatMatches:find?key=" + self.api_key)
            req_data = self.generate_request_data(urls)
            req.add_header('Content-Type', 'application/json')
            try:
                response = urlopen(req, json.dumps(req_data).encode("utf-8")).read()
                response_dict = json.loads(response.decode("utf-8"))
                self.update_threat_dict(response_dict)
            except HTTPError:
                self.is_api_key_correct = False

    @staticmethod
    def generate_request_data(filtered_urls) -> Dict["str", Dict[str, Union[List[str], str]]]:
        url_entries = ThreatInfoEnricher.get_url_entries(filtered_urls)
        return {
            "threatInfo": {
                "threatTypes": ["THREAT_TYPE_UNSPECIFIED", "MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE",
                                "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": url_entries
            }
        }

    @staticmethod
    def get_url_entries(filtered_urls) -> List[Dict[str, str]]:
        return list(map(lambda url: {"url": url}, filtered_urls))

    def update_threat_dict(self, response_dict) -> None:
        if response_dict == {}:
            return

        for match in response_dict["matches"]:
            url = match["threat"]["url"]
            threat_type = match["threatType"]
            self.threat_dict[url] = threat_type

    def reduce_threat_information(self, urls) -> Set[str]:
        reduced_list = set()
        for url in urls:
            if url != "" and url in self.threat_dict:
                for threat_type in self.threat_dict[url].split(","):
                    reduced_list.add(threat_type)

        return reduced_list

    def get_threat_number(self, threat_string_entry) -> str:
        return self.threat_type_dict[threat_string_entry]
