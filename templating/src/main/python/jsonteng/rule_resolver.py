# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

from .exception import TemplateEngineException
from .rules.rule_map import get_rule_map


class RuleResolver(object):
    """
    `RuleResolver` resolves a template rule.
    """
    # All template rule names start with RULE_MARKER
    RULE_MARKER = '#'

    def __init__(self, element_resolver, template_loader):
        """
        Construct a RuleResolver.
        :param element_resolver: ElementResolver for resolving an element
                                 by a rule.
        :param template_loader: TemplateLoader for loading template by a rule.
        """
        self._element_resolver = element_resolver
        self._template_loader = template_loader
        self._rule_map = get_rule_map(self)

    @staticmethod
    def is_key_rule(key):
        return isinstance(key, str) and len(key) > 1 and \
               key[0] == RuleResolver.RULE_MARKER

    @staticmethod
    def is_rule(rule_data):
        """
        Check whether a JSON element is a rule.
        :param rule_data: JSON element to be checked.
        :type rule_data: JSON object
        :return: True if it is a rule.
        :rtype: 'bool'
        """
        return isinstance(rule_data, list) and len(rule_data) > 0 and \
            isinstance(rule_data[0], str) and len(rule_data[0]) > 1 and \
            rule_data[0][0] == RuleResolver.RULE_MARKER

    def resolve(self, rule_data, binding_data_list):
        """
        Process a JSON element as a rule.
        :param rule_data: Template rule to be processed.
        :type rule_data: JSON element
        :param binding_data_list: binding data list to be used
                                  during the processing.
        :type binding_data_list: 'list'
        :return: Processed rule.
        :rtype: JSON object
        """
        rule_name = rule_data[0][1:]
        if rule_name in self._rule_map:
            rule = self._rule_map[rule_name]
            rule_tokens = rule_data[1:]
            return rule.process(rule_tokens, binding_data_list)
        else:
            raise TemplateEngineException("Unknown rule {}".format(rule_name))

    def get_element_resolver(self):
        """
        Return the element_resolver. Used by rules to get the element resolver.
        :return: Element resolver.
        :rtype: ElementResolver
        """
        return self._element_resolver

    def get_template_loader(self):
        """
        Return the template loader. Used by rules to get the template loader.
        :return: Template loader
        :rtype: TemplateLoader
        """
        return self._template_loader
