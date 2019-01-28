# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

from ..exception import TemplateEngineException
from .rule_base import RuleBase


class OneOfRule(RuleBase):
    """
    Select a value from a list of condition/value pairs if the first condition
    is true. If the last element contains value only, return it if all other
    conditions are false.
    """
    name = "one-of"

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
        if token_count < 1:
            raise TemplateEngineException(
                "Rule \"{}\" needs at least 1 parameter."
                " Parameters given {}".format(OneOfRule.name, rule_tokens))
        for index, item in enumerate(rule_tokens):
            if isinstance(item, list) and len(item) == 2:
                condition = item[0]
                value = item[1]
                condition_expr = self._element_resolver.resolve(
                    condition, binding_data_list)
                if self.safe_eval(condition_expr):
                    return self._element_resolver.resolve(
                        value, binding_data_list)
            else:
                if index == (token_count - 1) and not isinstance(item, list):
                    return self._element_resolver.resolve(
                        rule_tokens[-1], binding_data_list)
                else:
                    raise TemplateEngineException(
                        "Rule \"one-of\" contains an invalid parameter."
                        " {}".format(item))
        return RuleBase.RULE_NONE
