# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

from .tag_base import TagBase
from ..exception import TemplateEngineException


class AtTag(TagBase):
    """
    Return a value at an index or name depending the object.
    """
    name = "at"

    def __init__(self, tag_resolver):
        """
        Construct this tag.
        :param tag_resolver: Tag resolver
        :type tag_resolver: 'TagResolver'
        """
        super().__init__(tag_resolver)
        self._element_resolver = tag_resolver.get_element_resolver()
        self._template_loader = tag_resolver.get_template_loader()

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
        if len(tag_tokens) != 2:
            raise TemplateEngineException(
                "Tag \"{}\" requires 2 parameter. Parameters given {}".
                format(AtTag.name, tag_tokens))
        data = tag_tokens[0]
        key = tag_tokens[1]
        resolved_data = self._element_resolver.resolve(
            data, binding_data_list)
        resolved_key = self._element_resolver.resolve(
            key, binding_data_list)
        if isinstance(resolved_data, list):
            return resolved_data[int(resolved_key)]
        elif isinstance(resolved_data, dict):
            return resolved_data[resolved_key]
        else:
            return TagBase.TAG_NONE
