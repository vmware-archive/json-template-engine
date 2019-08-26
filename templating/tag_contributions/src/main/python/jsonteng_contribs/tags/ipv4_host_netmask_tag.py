# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

import ipaddress

from jsonteng.exception import TemplateEngineException
from jsonteng.tags.tag_base import TagBase


class Ipv4HostNetmaskTag(TagBase):
    """
    Network tag for returning network address, netmask and gateway.
    Gateway is assumed to be the lowest network address.
    """
    name = "ipv4-host-netmask"

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
                "Tag \"{}\" requires 1 parameter."
                " Parameters given {}".format(Ipv4HostNetmaskTag.name, tag_tokens))
        network = ipaddress.ip_network(self._element_resolver.resolve(
            tag_tokens[0], binding_data_list))
        return str(network.netmask)
