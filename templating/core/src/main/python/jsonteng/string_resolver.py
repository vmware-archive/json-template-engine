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
                'Mis-formed parameterized string "{}".'.format(str_data))
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
        separator_indices = \
            StringResolver._collect_separator_indices(param_name)
        for binding_data in binding_data_list:
            try:
                value = StringResolver._find_param(
                    param_name, separator_indices, binding_data)
                self._stats.update_stats(param_name)
                return value
            except InvalidReferenceException:
                pass
        raise UnresolvableParameterException(
            'Unable to resolve parameter "{}".'.format(param_name))

    @staticmethod
    def _find_param(param_name, separator_indices, binding_data):
        """
        Find the parameter value in this bindign_data. The result could be
        None which is a valid JSON value null. The parameter is matched
        as a whole string. If the whole string does not match any, the prefix
        of the first dot is used to sub parameter map and the rest of the
        string is matched against the sub parameter map. This process is
        repeated until a value is found. For example, parameter "x.y.z" is
        matched against the binding_data. If the binding contains "x.y.z",
        its value is returned. Else, "x" is used to match a sub parameter map
        in the binding data. If a sub parameter map is found, "y.z" is used to
        match a parameter in the sub parameter map. This process is repeated.
        :param param_name: Param name string.
        :type param_name: 'str'
        :param separator_indices: A list of parameter separator indices.
        :type separator_indices: 'list'
        :param binding_data: Parameter value map.
        :type binding_data: 'dict'
        :return: JSON value
        """
        count = len(separator_indices) + 1
        token_start = 0
        next_data = binding_data
        for i in range(count):
            if next_data is None or not isinstance(next_data, dict):
                raise InvalidReferenceException("invalid scope")
            key = param_name[token_start:]
            try:
                return StringResolver._match_key(key, next_data)
            except InvalidReferenceException:
                pass
            if i < len(separator_indices):
                token = param_name[token_start:separator_indices[i]]
                next_data = StringResolver._match_key(token, next_data)
                token_start = separator_indices[i] + 1
        raise InvalidReferenceException("mismatch binding data")

    @staticmethod
    def _match_key(key, data):
        """
        Find the key in params. If found, returns value.
        :param key: Key to be matched.
        :type key: 'str'
        :param data: Binding data map to be searched.
        :type data: 'dict'
        :return: JSON value
        """
        m = re.search("([a-zA-Z0-9]+)\[([0-9]+)\]", key)
        if m:
            key = m.group(1)
            index = int(m.group(2))
            if index < 0:
                raise TemplateEngineException(
                    "Parameter index is negative: %s".format(key))
            if key in data:
                value = data[key]
                if isinstance(value, list) and index < len(value):
                    return value[index]
            raise InvalidReferenceException("mismatch binding data")

        if key in data:
            return data[key]
        raise InvalidReferenceException("mismatch binding data")

    @staticmethod
    def _collect_separator_indices(param_name):
        """
        Locate all parameter name separators (dots).
        :param param_name: Parameter name.
        :type param_name: 'str'
        :return: A list of parameter separator indices.
        :rtype: 'list'
        """
        indices = list()
        str_len = len(param_name)
        i = 0
        while i < str_len:
            c = param_name[i]
            if c == '\\':
                i += 2
            elif c == '.':
                indices.append(i)
                i += 1
            else:
                i += 1
        return indices
