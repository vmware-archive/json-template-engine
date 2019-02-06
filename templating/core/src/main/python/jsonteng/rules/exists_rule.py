# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

from ..exception import UnresolvableParameterException
from .rule_base import RuleBase


class ExistsRule(RuleBase):
    """
    Check if a parameter is set.
    """
    name = "exists"

    def __init__(self, rule_resolver):
        """
        Construct this rule.
        :param rule_resolver: Rule resolver
        :type rule_resolver: 'RuleResolver'
        """
        super().__init__(rule_resolver)
        self._element_resolver = rule_resolver.get_element_resolver()
        self._template_loader = rule_resolver.get_template_loader()

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
        if len(rule_tokens) != 1:
            raise Exception(
                "Rule \"{}\" requires 1 parameter. Parameters given {}".
                format(ExistsRule.name, rule_tokens))
        data = rule_tokens[0]
        try:
            self._element_resolver.resolve(data, binding_data_list)
        except UnresolvableParameterException:
            return "1==0"
        return "1==1"
