// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "tags/tag-base.h"
#include "utils.h"

namespace jsonteng {
static const std::string Ipv4HostGateway_name("ipv4-host-gateway");

class Ipv4HostGatewayTag : public TagBase {
public:
  Ipv4HostGatewayTag(const TagResolverIf &tag_resolver)
      : TagBase(tag_resolver, Ipv4HostGateway_name) {}
  virtual ~Ipv4HostGatewayTag() {}

  nlohmann::json
  process(const std::vector<nlohmann::json> &tag_tokens,
          const std::vector<nlohmann::json> &binding_data_list) override {
    if (tag_tokens.size() != 1) {
      throw TemplateEngineException(
          std::string("Tag \"") + m_name +
          "\" requires 1 parameter. Parameters given " +
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
    unsigned long network_address =
        (std::stoul(network_address_parts[0]) << 24) +
        (std::stoul(network_address_parts[1]) << 16) +
        (std::stoul(network_address_parts[2]) << 8) +
        std::stoul(network_address_parts[3]);
    unsigned long gateway_address = network_address + 1;

    return std::to_string((gateway_address & 0xFF000000) >> 24) + "." +
           std::to_string((gateway_address & 0x00FF0000) >> 16) + "." +
           std::to_string((gateway_address & 0x0000FF00) >> 8) + "." +
           std::to_string(gateway_address & 0x000000FF);
  }
};

} // namespace jsonteng
