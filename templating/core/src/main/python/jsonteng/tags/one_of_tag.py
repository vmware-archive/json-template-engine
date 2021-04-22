# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0
import json

from ..exception import TemplateEngineException
from .tag_base import TagBase


class OneOfTag(TagBase):
    """
    Select a value from a list of condition/value pairs if the first condition
    is true. If the last element contains value only, return it if all other
    conditions are false.
    """
    name = "one-of"

    def __init__(self, tag_resolver):
        """
        Construct this tag.
        :param tag_resolver: Tag resolver
        :type tag_resolver: 'TagResolver'
        """
        super().__init__(tag_resolver)
        self._element_resolver = tag_resolver.get_element_resolver()

    def process(self, tag_tokens, binding_data_list):
        """
        Process this tag.
        :param tag_tokens: Tag arguments.
        :type tag_tokens: 'list'
        :param binding_data_list: Binding data used during the processing.
        :type binding_data_list: 'list'
        :return: JSON object
        :rtype: JSON object
        """
        token_count = len(tag_tokens)
        if token_count < 1:
            raise TemplateEngineException(
                "Tag \"{}\" requires at least 1 parameter."
                " Parameters given {}".format(OneOfTag.name, tag_tokens))
        for index, item in enumerate(tag_tokens):
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
                        tag_tokens[-1], binding_data_list)
                else:
                    raise TemplateEngineException(
                        "Tag \"{}\" contains an invalid parameter."
                        " {}.".format(OneOfTag.name, json.dumps(item, separators=(',', ':'))))
        return TagBase.TAG_NONE
