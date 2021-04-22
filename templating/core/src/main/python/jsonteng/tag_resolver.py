# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

from .exception import TemplateEngineException
from .tags.tag_map import get_tag_map


class TagResolver(object):
    """
    `TagResolver` resolves a template tag.
    """
    # All template tag names start with TAG_MARKER
    TAG_MARKER = '#'
    # Any character from ":" to the end of the tag name string is ignored.
    LABEL_SEPARATOR = ":"

    def __init__(self, element_resolver, template_loader):
        """
        Construct a TagResolver.
        :param element_resolver: ElementResolver for resolving an element
                                 by a tag.
        :param template_loader: TemplateLoader for loading template by a tag.
        """
        self._element_resolver = element_resolver
        self._template_loader = template_loader
        self._tag_map = get_tag_map(self)

    @staticmethod
    def is_key_tag(key):
        return isinstance(key, str) and len(key) > 1 and \
               key[0] == TagResolver.TAG_MARKER

    @staticmethod
    def is_tag(tag_data):
        """
        Check whether a JSON element is a tag.
        :param tag_data: JSON element to be checked.
        :type tag_data: JSON object
        :return: True if it is a tag.
        :rtype: 'bool'
        """
        return isinstance(tag_data, list) and len(tag_data) > 0 and \
               isinstance(tag_data[0], str) and len(tag_data[0]) > 1 and \
               tag_data[0][0] == TagResolver.TAG_MARKER

    def resolve(self, tag_data, binding_data_list):
        """
        Process a JSON element as a tag.
        :param tag_data: Template tag to be processed.
        :type tag_data: JSON element
        :param binding_data_list: binding data list to be used
                                  during the processing.
        :type binding_data_list: 'list'
        :return: Processed tag.
        :rtype: JSON object
        """
        tag_name = tag_data[0][1:]
        # When a tag name is used in a dictionary as a key,
        # an arbitrary label is allowed to be appended to the tag name
        # in the format of ":label" to make the key unique.
        tag_name = tag_name.partition(TagResolver.LABEL_SEPARATOR)[0]
        if tag_name in self._tag_map:
            tag = self._tag_map[tag_name]
            tag_tokens = tag_data[1:]
            return tag.process(tag_tokens, binding_data_list)
        else:
            raise TemplateEngineException("Unknown tag \"{}\".".format(tag_name))

    def get_element_resolver(self):
        """
        Return the element_resolver. Used by tags to get the element resolver.
        :return: Element resolver.
        :rtype: ElementResolver
        """
        return self._element_resolver

    def get_template_loader(self):
        """
        Return the template loader. Used by tags to get the template loader.
        :return: Template loader
        :rtype: TemplateLoader
        """
        return self._template_loader
