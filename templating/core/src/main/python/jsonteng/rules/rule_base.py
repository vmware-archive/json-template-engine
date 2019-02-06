# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

import abc

from ..exception import TemplateEngineException


class RuleBase(object):
    """
    Base class of rule classes.
    """
    __metaclass__ = abc.ABCMeta
    RULE_NONE = type('RuleNone', (), {})()

    def __init__(self, rule_resolver):
        """
        Base rule constructor.
        :param rule_resolver: Rule resolver to be used by the rule.
        """
        self._rule_resolver = rule_resolver

    @abc.abstractmethod
    def process(self, rule_tokens, binding_data_list):
        """
        Process a rule.
        :param rule_tokens: Rule arguments.
        :type rule_tokens: 'list'
        :param binding_data_list: Binding data used during the processing.
        :type binding_data_list: 'list'
        :return: JSON object
        :rtype: JSON object
        """
        raise NotImplementedError

    @staticmethod
    def safe_eval(expr):
        """
        A safe eval that is limited to simple expressions.
        :param expr: A Python boolean expression
        :type expr: 'str'
        :return: result of expression evaluation
        :rtype: 'bool'
        """
        result = eval(expr, {"__builtins__": None}, {})
        if not isinstance(result, bool):
            raise TemplateEngineException(
                "Expression {} is not a boolean type".format(expr))
        return result
