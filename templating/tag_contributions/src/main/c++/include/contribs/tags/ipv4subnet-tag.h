// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "tags/tag-base.h"
#include "utils.h"

namespace jsonteng {
static const std::string Ipv4Subnet_name("ipv4-subnet");

class Ipv4SubnetTag : public TagBase {
public:
  Ipv4SubnetTag(const TagResolverIf &tag_resolver)
      : TagBase(tag_resolver, Ipv4Subnet_name) {}
  virtual ~Ipv4SubnetTag() {}

  nlohmann::json
  process(const std::vector<nlohmann::json> &tag_tokens,
          const std::vector<nlohmann::json> &binding_data_list) override {
    if (tag_tokens.size() != 3) {
      throw TemplateEngineException(
          std::string("Tag \"") + m_name +
          "\" requires 3 parameters. Parameters given " +
          tokens_to_string(tag_tokens));
    }
    const ElementResolverIf &element_resolver =
        m_tag_resolver.get_element_resolver();
    std::string network =
        element_resolver.resolve(tag_tokens[0], binding_data_list)
            .get<std::string>();
    int subnet_count =
        element_resolver.resolve(tag_tokens[1], binding_data_list).get<int>();
    int subnet_index =
        element_resolver.resolve(tag_tokens[2], binding_data_list).get<int>();
    int base2_exp = 0;
    int count = subnet_count - 1;
    while ((count & 0x1) != 0) {
      count = count >> 1;
      base2_exp += 1;
    }
    if (count != 0) {
      throw TemplateEngineException(
          std::string("Subnet count must be multiple of 2s. ") +
          std::to_string(subnet_count) + " is given");
    }
    if (base2_exp == 0) {
      return network;
    }
    const std::vector<std::string> parts = Utils::split_string(network, '/');
    int prefixlen = std::stoi(parts[1]);
    int subnet_prefix = prefixlen + base2_exp;
    std::vector<std::string> network_address_parts =
        Utils::split_string(parts[0], '.');
    unsigned long network_address =
        (std::stoul(network_address_parts[0]) << 24) +
        (std::stoul(network_address_parts[1]) << 16) +
        (std::stoul(network_address_parts[2]) << 8) +
        std::stoul(network_address_parts[3]);
    unsigned long subnet_address =
        network_address + (subnet_index << (32 - subnet_prefix));
    std::string subnet =
        std::to_string((subnet_address & 0xFF000000) >> 24) + "." +
        std::to_string((subnet_address & 0x00FF0000) >> 16) + "." +
        std::to_string((subnet_address & 0x0000FF00) >> 8) + "." +
        std::to_string(subnet_address & 0x000000FF);
    return subnet + "/" + std::to_string(subnet_prefix);
  }
};

} // namespace jsonteng
