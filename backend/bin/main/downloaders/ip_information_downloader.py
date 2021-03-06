import json
import socket
import time
from typing import Dict

import requests
from ratelimit import limits, sleep_and_retry

from main.helpers.dns_helper import DnsHelper
from main.helpers.ip_address_helper import IpAddressHelper


class IpInformationDownloader(object):
    def __init__(self) -> None:
        self.ip_information = {}
        self.dns_helper = DnsHelper()

    def get_dst_src_information(self, dst_src: Dict[str, str]) -> Dict[str, str]:
        dst = dst_src["dst"]
        src = dst_src["src"]
        self.get_ip_information(dst)
        self.get_ip_information(src)
        return {
            "dst": self.ip_information[dst],
            "src": self.ip_information[src]
        }

    def get_ip_information(self, ip_address: str) -> None:
        if ip_address in self.ip_information:
            return

        if ip_address == "" or not IpAddressHelper.is_global_ip(ip_address):
            self.ip_information[ip_address] = self.get_private_ip_data(ip_address)
            return

        self.ip_information[ip_address] = self.get_ip_data(ip_address)

    @sleep_and_retry
    @limits(calls=3, period=1)
    def get_ip_data(self, ip_addr: str, counter=0) -> Dict[str, str]:
        try:
            search_url = "https://tools.keycdn.com/geo.json?host={}".format(ip_addr)
            response = requests.get(search_url, timeout=5)
            if response.status_code == 200:
                response_json = json.loads(response.content.decode("utf-8"))
                geo_data = response_json["data"]["geo"]
                return self.extract_data(geo_data, ip_addr)

        except (socket.gaierror, requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout):
            if counter < 5:
                time.sleep(2)
                return self.get_ip_data(ip_addr, counter + 1)

        return self.get_private_ip_data(ip_addr)

    @staticmethod
    def extract_data(geo_data: Dict[str, str], ip_addr: str) -> Dict[str, str]:
        return {
            "ip_address": ip_addr,
            "rdns": geo_data["rdns"],
            "asn": geo_data["asn"],
            "isp": geo_data["isp"],
            "latitude": geo_data["latitude"],
            "longitude": geo_data["longitude"],
        }

    def get_private_ip_data(self, ip_address: str) -> Dict[str, str]:
        fqdn = ip_address
        if ip_address != "" and IpAddressHelper.is_private_ip(ip_address):
            fqdn = self.dns_helper.get_fqdn(ip_address)

        return {
            "ip_address": ip_address,
            "rdns": fqdn,
            "asn": "",
            "isp": "",
            "latitude": "",
            "longitude": ""
        }
