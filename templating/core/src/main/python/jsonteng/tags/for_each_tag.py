# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

from ..exception import TemplateEngineException
from .tag_base import TagBase


class ForEachTag(TagBase):
    """
    Apply a list of binding data to a template repeatedly and return the
    resolved templates in a list.
    """
    name = "for-each"

    def __init__(self, tag_resolver):
        """
        Construct this Tag.
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
        if len(tag_tokens) < 2 or len(tag_tokens) > 3:
            raise Exception(
                "Tag \"{}\" requires 2 or 3 parameters."
                " Parameters given {}".
                format(ForEachTag.name, tag_tokens))
        data_list = tag_tokens[0]
        try:
            template = self._element_resolver.resolve(
                tag_tokens[1], binding_data_list)
        except TemplateEngineException:
            # If encounter exception, treat the token as the template.
            # The resolve may need a loop dependent binding data.
            template = tag_tokens[1]
        template_json = self._template_loader.load(template)
        resolved_data_list = self._element_resolver.resolve(
            data_list, binding_data_list)
        resolved_json = list()
        for index, data in enumerate(resolved_data_list):
            binding_data_list.insert(0, data)
            binding_data_list.insert(0, {"_index_": index})
            if len(tag_tokens) == 3:
                condition_expr = self._element_resolver.resolve(
                    tag_tokens[2], binding_data_list)
                if not self.safe_eval(condition_expr):
                    binding_data_list.pop(0)
                    binding_data_list.pop(0)
                    continue
            resolved_template = self._element_resolver.resolve(
                template_json, binding_data_list)
            resolved_json.append(resolved_template)
            binding_data_list.pop(0)
            binding_data_list.pop(0)
        self._template_loader.unload(template)
        return resolved_json
