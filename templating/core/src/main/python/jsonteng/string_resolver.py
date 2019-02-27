# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

import re

from .exception import InvalidReferenceException, TemplateEngineException, \
    UnresolvableParameterException
from .tags.tag_base import TagBase


class StringResolver(object):
    """
    Resolve a string by parameter expansions.
    """
    def __init__(self, element_resolver, stats):
        """
        Constructs a new string resolver.
        :param element_resolver: Element resolver
        :type element_resolver: 'ElementResolver'
        :param stats: Stats object for stats collection.
        :type stats: 'Stats'
        """
        self._element_resolver = element_resolver
        self._stats = stats

    def resolve(self, str_data, binding_data_list):
        """
        Resolve a string by parameter expansions.
        :param str_data: String to be resolved.
        :type str_data: 'str'
        :param binding_data_list: Binding data list
        :type binding_data_list: 'list'
        :return: JSON values
        """
        str_len = len(str_data)
        stack = list()
        i = 0
        while i < str_len:
            c = str_data[i]
            if c == '\\':
                # skip escaped char
                i += 2
            elif c == '$':
                # find a param start marker "${"
                next_index = i + 1
                if next_index < str_len and str_data[next_index] == '{':
                    # save the param start position
                    stack.append(i)
                    i += 2
                else:
                    i += 1
            elif c == '}':
                i += 1
                if stack:
                    # get param name.
                    param_start = stack.pop()
                    param_name = str_data[param_start+2:i-1]
                    # resolve the param.
                    value = self._resolve_param(param_name, binding_data_list)
                    # update string.
                    if value is not TagBase.TAG_NONE:
                        sub_str_before_param = str_data[:param_start]
                        sub_str_after_param = str_data[i:] \
                            if i < str_len else ""
                        if sub_str_before_param or sub_str_after_param:
                            # if the value is only part of the original
                            # string, treat it as a string and reprocess
                            new_str = sub_str_before_param + \
                                      str(self._element_resolver.resolve(
                                          value, binding_data_list)) + \
                                      sub_str_after_param
                            str_data = new_str
                            str_len = len(str_data)
                            i = param_start
                        else:
                            # if the value replaces the whole string,
                            # return the value
                            return self._element_resolver.resolve(
                                value, binding_data_list)
            else:
                i += 1
        if stack:
            raise TemplateEngineException(
                "Mis-formed parameterized string. {}".format(str_data))
        return str_data

    def _resolve_param(self, param_name, binding_data_list):
        """
        Resove a parameter by returning its value found in binding_data_list.
        :param param_name: Parameter name.
        :type param_name: 'str'
        :param binding_data_list: Binding data list.
        :type binding_data_list: 'list'
        :return: JSON value
        :rtype: JSON object
        """
        param_tokens = param_name.split('.')
        if len(param_tokens) < 1:
            raise TemplateEngineException(
                "Invalid parameter reference {}.".format(param_name))
        for binding_data in binding_data_list:
            try:
                value = StringResolver._find_param(param_tokens, binding_data)
                self._stats.update_stats(param_name)
                return value
            except InvalidReferenceException:
                pass
        raise UnresolvableParameterException(
            "Unable to resolve parameter {}.".format(param_name))

    @staticmethod
    def _find_param(param_tokens, binding_data):
        """
        Find the parameter value in this bindign_data. The result could be
        None which is a valid JSON value null.
        :param param_tokens: A list of parameter tokens.
        :type param_tokens: 'list'
        :param binding_data: Parameter value map.
        :type binding_data: 'dict'
        :return: JSON value
        """
        next_data = binding_data
        for token in param_tokens:
            index = -1
            m = re.search("([a-zA-Z0-9]+)\[([0-9]+)\]", token)
            if m:
                token = m.group(1)
                index = int(m.group(2))

            if next_data is None:
                raise InvalidReferenceException("invalid scope")
            if token in next_data:
                next_data = next_data[token]
            else:
                raise InvalidReferenceException("mismatch binding data")
            if index >= 0 and isinstance(next_data, list):
                if index >= len(next_data):
                    return None
                next_data = next_data[index]
        return next_data
