// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "tags/tag-base.h"
#include "utils.h"

namespace jsonteng {
static const std::string Ipv4HostNetmask_name("ipv4-host-netmask");

class Ipv4HostNetmaskTag : public TagBase {
public:
  Ipv4HostNetmaskTag(const TagResolverIf &tag_resolver)
      : TagBase(tag_resolver, Ipv4HostNetmask_name) {}
  virtual ~Ipv4HostNetmaskTag() {}

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
    int prefix = std::stoi(network_parts[1]);
    int netmask_int = ~((0x1 << (32 - prefix)) - 1);
    return std::to_string((netmask_int & 0xFF000000) >> 24) + "." +
           std::to_string((netmask_int & 0x00FF0000) >> 16) + "." +
           std::to_string((netmask_int & 0x0000FF00) >> 8) + "." +
           std::to_string(netmask_int & 0x000000FF);
  }
};

} // namespace jsonteng
