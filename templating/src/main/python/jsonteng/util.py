# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

from collections import OrderedDict
from numbers import Number

from .exception import TemplateEngineException


def unescape_json(element):
    """
    Remove escape character '\' in a JSON object.
    :param element: JSON object
    :type element: JSON object
    :return: unescaped JSON object
    :rtype: JSON object
    """
    if isinstance(element, str):
        return unescape_string(element)
    elif isinstance(element, Number):
        return element
    elif isinstance(element, bool):
        return element
    elif element is None:
        return element
    elif isinstance(element, dict):
        new_element = OrderedDict()
        for key, value in element.items():
            new_key = unescape_json(key)
            new_value = unescape_json(value)
            new_element[new_key] = new_value
        return new_element
    elif isinstance(element, list):
        new_element = list()
        for index, item in enumerate(element):
            new_item = unescape_json(item)
            new_element.append(new_item)
        return new_element
    raise TemplateEngineException(
        "Unknown data type {} of {}.".format(type(element), element))


def unescape_string(escaped_string):
    """
    Remove escape character in a string.
    :param escaped_string: String to be unescaped.
    :type escaped_string: 'str'
    :return: Unescaped string.
    :rtype: 'str'
    """
    modified_string = escaped_string
    str_len = len(modified_string)
    i = 0
    while i < str_len:
        c = modified_string[i]
        if c == '\\':
            # skip escaped char
            new_str = modified_string[:i]
            i += 1
            if i < str_len:
                new_str += modified_string[i:]
            modified_string = new_str
            str_len = len(modified_string)
        i += 1
    return modified_string


def check_duplicated_binding_data(binding_data_list):
    """
    Check duplicated parameters in binding data list.
    :param binding_data_list: Binding data list to be checked.
    :type binding_data_list: 'list'
    :return: A dictionary with key of duplicated parameters and value of
             duplicated assignments.
    :rtype: 'dict'
    """
    def _find_param_terminal(super_name, sub_binding_data, data_map):
        for item in sub_binding_data.items():
            name = item[0]
            if super_name:
                name = super_name + '.' + name
            if isinstance(item[1], dict):
                _find_param_terminal(name, item[1], data_map)
            else:
                if name not in data_map:
                    data_map[name] = list()
                param_values = data_map[name]
                param_values.append(item[1])

    binding_data_map = OrderedDict()
    for binding_data in binding_data_list:
        _find_param_terminal(None, binding_data, binding_data_map)
    dup_map = OrderedDict()
    for param, values in binding_data_map.items():
        if len(values) > 1:
            dup_map[param] = values
    return dup_map
