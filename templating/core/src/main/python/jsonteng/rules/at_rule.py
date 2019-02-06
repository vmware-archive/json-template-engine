# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

from .rule_base import RuleBase


class AtRule(RuleBase):
    """
    Return a value at an index or name depending the object.
    """
    name = "at"

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
        if len(rule_tokens) != 2:
            raise Exception(
                "Rule \"{}\" requires 2 parameter. Parameters given {}".
                format(AtRule.name, rule_tokens))
        data = rule_tokens[0]
        key = rule_tokens[1]
        resolved_data = self._element_resolver.resolve(
            data, binding_data_list)
        resolved_key = self._element_resolver.resolve(
            key, binding_data_list)
        if isinstance(resolved_data, list):
            return resolved_data[int(resolved_key)]
        elif isinstance(resolved_data, dict):
            return resolved_data[resolved_key]
        else:
            return RuleBase.RULE_NONE
