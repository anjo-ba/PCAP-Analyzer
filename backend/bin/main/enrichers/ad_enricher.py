from main.dicts.blacklist_dict import BlacklistDict
from main.enrichers.enricher import Enricher
from main.helpers import string_helper
from main.helpers.ip_helper import IpHelper


class AdEnricher(Enricher):
    def __init__(self, blacklist_domains=None):
        enricher_type = "ad enricher"
        header = "ad_category"
        Enricher.__init__(self, enricher_type, header)

        self.ip_to_category = {}
        self.blacklist_dict = BlacklistDict(blacklist_domains)
        self.domain_to_ad_dict = {}

    def test_domains(self, domains) -> str:
        domain_list = domains.split(",")
        is_ad = False
        for domain in domain_list:
            if domain == "":
                continue

            domain = string_helper.remove_quotations(domain)
            is_ad = is_ad or self.is_ad_domain(domain)

        return "1" if is_ad else "0"

    def is_ad_domain(self, domain) -> bool:
        if domain in self.domain_to_ad_dict:
            return self.domain_to_ad_dict[domain]

        dict_to_test = self.blacklist_dict.blacklist_dict
        is_ad = self.is_domain_in_dict(domain, dict_to_test)

        is_ad = is_ad or dict_to_test == {}
        self.domain_to_ad_dict[domain] = is_ad
        return is_ad

    def is_domain_in_dict(self, domain, dict_to_test) -> bool:
        return_value = False

        if IpHelper.is_ip(domain):
            return return_value

        for domain_part in reversed(domain.split(".")):
            return_value = dict_to_test.get(domain_part, {})
            if isinstance(return_value, dict):
                if return_value == {}:
                    break

                dict_to_test = return_value

            if isinstance(return_value, str):
                return_value = True
                break

        self.domain_to_ad_dict[domain] = return_value
        return return_value
