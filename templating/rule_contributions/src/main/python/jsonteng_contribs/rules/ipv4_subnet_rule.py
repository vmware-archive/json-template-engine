# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

import ipaddress

from jsonteng.exception import TemplateEngineException
from jsonteng.rules.rule_base import RuleBase


class Ipv4SubnetRule(RuleBase):
    """
    Divide a network into N number of subnets. Return i_th of the subnet.
    """
    name = "ipv4-subnet"

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
        :param rule_tokens: Rule arguments.
        :type rule_tokens: 'list'
        :param binding_data_list: Binding data used during the processing.
        :type binding_data_list: 'list'
        :return: JSON object
        :rtype: JSON object
        """
        token_count = len(rule_tokens)
        if token_count < 3:
            raise TemplateEngineException(
                "Rule \"{}\" needs at least 3 parameter."
                " Parameters given {}".format(Ipv4SubnetRule.name, rule_tokens))
        network = ipaddress.ip_network(self._element_resolver.resolve(
            rule_tokens[0], binding_data_list))
        subnet_count = int(self._element_resolver.resolve(
            rule_tokens[1], binding_data_list))
        subnet_index = int(self._element_resolver.resolve(
            rule_tokens[2], binding_data_list))
        base2_exp = 0
        count = int(subnet_count) - 1
        while count & 1:
            base2_exp += 1
            count = count >> 1
        if count:
            raise TemplateEngineException(
                "Subnet count must be multiple of 2s."
                " {} is given".format(subnet_count))
        if base2_exp == 0:
            return rule_tokens[0]
        subnet_prefix = network.prefixlen + base2_exp
        subnet_address = ipaddress.ip_address(
            int(network.network_address)
            + (subnet_index << (32 - subnet_prefix)))
        return str(subnet_address) + '/' + str(subnet_prefix)
