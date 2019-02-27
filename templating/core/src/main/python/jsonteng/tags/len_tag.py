# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

from .tag_base import TagBase


class LenTag(TagBase):
    """
    Return the length of an object. The value depends on the object type.
    """
    name = "len"

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
        if len(tag_tokens) != 1:
            raise Exception(
                "Tag \"{}\" requires 1 parameter. Parameters given {}".
                format(LenTag.name, tag_tokens))
        data = tag_tokens[0]
        resolved_data = self._element_resolver.resolve(data, binding_data_list)
        if resolved_data is not None:
            return len(resolved_data)
        else:
            return 0
