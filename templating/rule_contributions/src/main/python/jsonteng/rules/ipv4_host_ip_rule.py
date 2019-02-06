import ipaddress

from jsonteng.exception import TemplateEngineException
from jsonteng.rules.rule_base import RuleBase


class Ipv4HostIpRule(RuleBase):
    """
    Network rule for returning network address, netmask and gateway.
    Gateway is assumed to be the lowest network address.
    """
    name = "ipv4-host-ip"

    def __init__(self, rule_resolver):
        """
        Construct this rule.
        :param rule_resolver: Rule resolver
        :type rule_resolver: 'RuleResolver'
        """
        super().__init__(rule_resolver)
        self._element_resolver = rule_resolver.get_element_resolver()

    def process(self, rule_tokens, binding_data_list):
        """
        Process this rule.
        :param binding_data_list: Binding data used during the processing.
        :type binding_data_list: 'list'
        :param rule_tokens: Rule arguments.
        :type rule_tokens: 'list'
        :return: JSON object
        :rtype: JSON object
        """
        token_count = len(rule_tokens)
        if token_count < 2:
            raise TemplateEngineException(
                "Rule \"{}\" needs at least 2 parameter."
                " Parameters given {}".format(Ipv4HostIpRule.name, rule_tokens))
        network = ipaddress.ip_network(self._element_resolver.resolve(
            rule_tokens[0], binding_data_list))
        index = int(self._element_resolver.resolve(
            rule_tokens[1], binding_data_list))
        return str(ipaddress.ip_address(
            int(ipaddress.ip_address(network.network_address)) + index))
