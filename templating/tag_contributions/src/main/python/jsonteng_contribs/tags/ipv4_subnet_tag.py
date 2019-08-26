# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

import ipaddress

from jsonteng.exception import TemplateEngineException
from jsonteng.tags.tag_base import TagBase


class Ipv4SubnetTag(TagBase):
    """
    Divide a network into N number of subnets. Return i_th of the subnet.
    """
    name = "ipv4-subnet"

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
        if token_count < 3:
            raise TemplateEngineException(
                "Tag \"{}\" requires 3 parameters."
                " Parameters given {}".format(Ipv4SubnetTag.name, tag_tokens))
        network = ipaddress.ip_network(self._element_resolver.resolve(
            tag_tokens[0], binding_data_list))
        subnet_count = int(self._element_resolver.resolve(
            tag_tokens[1], binding_data_list))
        subnet_index = int(self._element_resolver.resolve(
            tag_tokens[2], binding_data_list))
        base2_exp = 0
        count = int(subnet_count) - 1
        while count & 1:
            base2_exp += 1
            count = count >> 1
        if count:
            raise TemplateEngineException(
                "Subnet count must be multiple of 2s."
                " {} is given".format(subnet_count))
        if base2_exp == 0:
            return tag_tokens[0]
        subnet_prefix = network.prefixlen + base2_exp
        subnet_address = ipaddress.ip_address(
            int(network.network_address)
            + (subnet_index << (32 - subnet_prefix)))
        return str(subnet_address) + '/' + str(subnet_prefix)
