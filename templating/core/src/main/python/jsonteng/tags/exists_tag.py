# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

from ..exception import UnresolvableParameterException
from .tag_base import TagBase


class ExistsTag(TagBase):
    """
    Check if a parameter is set.
    """
    name = "exists"

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
                format(ExistsTag.name, tag_tokens))
        data = tag_tokens[0]
        try:
            self._element_resolver.resolve(data, binding_data_list)
        except UnresolvableParameterException:
            return "False"
        return "True"
