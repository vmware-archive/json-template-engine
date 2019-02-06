# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

from collections import OrderedDict

from .at_rule import AtRule
from .for_each_rule import ForEachRule
from .exists_rule import ExistsRule
from .len_rule import LenRule
from .one_of_rule import OneOfRule


_rule_class_map = {
    AtRule.name: AtRule,
    ExistsRule.name: ExistsRule,
    ForEachRule.name: ForEachRule,
    LenRule.name: LenRule,
    OneOfRule.name: OneOfRule
}


def get_rule_map(rule_resolver):
    """
    Return a rule map of known rules.
    :param rule_resolver: Rule resolved used by rules.
    :type rule_resolver: 'RuleResolver'
    :return: A map of rules.
    :rtype: 'dict'
    """
    rule_map = OrderedDict()
    for rule_name, rule in _rule_class_map.items():
        rule_map[rule_name] = rule(rule_resolver)
    return rule_map


def add_rule(rule_name, rule):
    """
    Add a rule to the rule collection.
    :param rule_name: Rule name.
    :type rule_name: 'str'
    :param rule: Rule class.
    :type rule: 'RuleBase'
    :return:
    """
    _rule_class_map[rule_name] = rule


def get_rule_names():
    """
    Get all rule names.
    :return: Rule names.
    :rtype: 'list'
    """
    return _rule_class_map.keys()
