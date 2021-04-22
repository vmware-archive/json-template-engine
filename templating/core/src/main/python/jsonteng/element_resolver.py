# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0
import json
from collections import OrderedDict
from numbers import Number

from .exception import TemplateEngineException
from .tags.tag_base import TagBase
from .tag_resolver import TagResolver
from .string_resolver import StringResolver


class ElementResolver(object):
    """
    `ElementResolver` resolves a JSON element.
    """
    def __init__(self, template_loader, stats):
        """
        Construct a new ElementResolver.
        :param template_loader: TemplateLoader object for loading
                                additional templates
        :type template_loader: 'TemplateLoader'
        :param stats: Stats object collecting stats
        :type stats: 'Stats'
        """
        self._string_resolver = StringResolver(self, stats)
        self._tag_resolver = TagResolver(self, template_loader)

    def resolve(self, element, binding_data_list):
        """
        Resolve one element in a JSON template. The element could be one of
        JSON data types. The resolution is recursive in a depth first manner.
        :param element: A JSON object of one of JSON types.
        :type element: JSON data type
        :param binding_data_list: Binding data list used to expand parameters
                                  in the template element.
        :type binding_data_list: 'list'
        :return: Resolved JSON element.
        :rtype: JSON data type
        """
        if isinstance(element, str):
            return self._string_resolver.resolve(element, binding_data_list)
        elif isinstance(element, Number):
            return element
        elif isinstance(element, bool):
            return element
        elif element is None:
            return element
        elif isinstance(element, dict):
            new_element = OrderedDict()
            for key, value in element.items():
                if TagResolver.is_key_tag(key):
                    if not isinstance(value, list):
                        raise TemplateEngineException(
                            "Value must be a list if name is a tag: \"{}\". Found \"{}\".".
                            format(key, value))
                    tag_temp = [key] + value
                    resolved_tuple = self.resolve(
                        tag_temp, binding_data_list)
                    if isinstance(resolved_tuple, dict):
                        new_element.update(resolved_tuple)
                    elif resolved_tuple is not TagBase.TAG_NONE:
                        raise TemplateEngineException(
                            "Invalid tag result format for JSON"
                            " object name tag: {} {} => {}.".
                            format(json.dumps(key, separators=(',', ':')),
                                   json.dumps(value, separators=(',', ':')),
                                   json.dumps(resolved_tuple, separators=(',', ':'))))
                else:
                    new_key = self.resolve(key, binding_data_list)
                    new_value = self.resolve(value, binding_data_list)
                    if isinstance(new_key, str) and \
                            new_value is not TagBase.TAG_NONE:
                        new_element[new_key] = new_value
            return new_element
        elif isinstance(element, list):
            if TagResolver.is_tag(element):
                return self._tag_resolver.resolve(element, binding_data_list)
            new_element = list()
            for item in element:
                new_item = self.resolve(item, binding_data_list)
                if new_item is not TagBase.TAG_NONE:
                    new_element.append(new_item)
            return new_element
        raise TemplateEngineException(
            "Unknown data type {} of {}".format(type(element), element))
