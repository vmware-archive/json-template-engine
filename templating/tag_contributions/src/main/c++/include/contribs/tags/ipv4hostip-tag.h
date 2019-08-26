// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "tags/tag-base.h"
#include "utils.h"

namespace jsonteng {
static const std::string Ipv4HostIp_name("ipv4-host-ip");

class Ipv4HostIpTag : public TagBase {
public:
  Ipv4HostIpTag(const TagResolverIf &tag_resolver)
      : TagBase(tag_resolver, Ipv4HostIp_name) {}
  virtual ~Ipv4HostIpTag() {}

  nlohmann::json
  process(const std::vector<nlohmann::json> &tag_tokens,
          const std::vector<nlohmann::json> &binding_data_list) override {
    if (tag_tokens.size() != 2) {
      throw TemplateEngineException(
          std::string("Tag \"") + m_name +
          "\" requires 2 parameters. Parameters given " +
          tokens_to_string(tag_tokens));
    }
    const ElementResolverIf &element_resolver =
        m_tag_resolver.get_element_resolver();
    std::vector<std::string> network_parts = Utils::split_string(
        element_resolver.resolve(tag_tokens[0], binding_data_list)
            .get<std::string>(),
        '/');
    std::vector<std::string> network_address_parts =
        Utils::split_string(network_parts[0], '.');
    int index =
        element_resolver.resolve(tag_tokens[1], binding_data_list).get<int>();
    unsigned long network_address =
        (std::stoul(network_address_parts[0]) << 24) +
        (std::stoul(network_address_parts[1]) << 16) +
        (std::stoul(network_address_parts[2]) << 8) +
        std::stoul(network_address_parts[3]);
    unsigned long host_address = network_address + index;

    return std::to_string((host_address & 0xFF000000) >> 24) + "." +
           std::to_string((host_address & 0x00FF0000) >> 16) + "." +
           std::to_string((host_address & 0x0000FF00) >> 8) + "." +
           std::to_string(host_address & 0x000000FF);
  }
};

} // namespace jsonteng
