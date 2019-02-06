# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

from ..exception import TemplateEngineException
from .rule_base import RuleBase


class ForEachRule(RuleBase):
    """
    Apply a list of binding data to a template repeatedly and return the
    resolved templates in a list.
    """
    name = "for-each"

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
        if len(rule_tokens) < 2 or len(rule_tokens) > 3:
            raise Exception(
                "Rule \"{}\" requires 2 or 3 parameters."
                " Parameters given {}".
                format(ForEachRule.name, rule_tokens))
        data_list = rule_tokens[0]
        try:
            template = self._element_resolver.resolve(
                rule_tokens[1], binding_data_list)
        except TemplateEngineException:
            # If encounter exception, treat the token as the template.
            # The resolve may need a loop dependent binding data.
            template = rule_tokens[1]
        template_json = self._template_loader.load(template)
        resolved_data_list = self._element_resolver.resolve(
            data_list, binding_data_list)
        resolved_json = list()
        for index, data in enumerate(resolved_data_list):
            binding_data_list.insert(0, data)
            binding_data_list.insert(0, {"_index_": index})
            if len(rule_tokens) == 3:
                condition_expr = self._element_resolver.resolve(
                    rule_tokens[2], binding_data_list)
                if not self.safe_eval(condition_expr):
                    binding_data_list.pop(0)
                    binding_data_list.pop(0)
                    continue
            resolved_template = self._element_resolver.resolve(
                template_json, binding_data_list)
            resolved_json.append(resolved_template)
            binding_data_list.pop(0)
            binding_data_list.pop(0)
        self._template_loader.unload(template)
        return resolved_json
