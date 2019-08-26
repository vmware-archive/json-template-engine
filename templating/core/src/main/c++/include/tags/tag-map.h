// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "../interfaces.h"
#include "at-tag.h"
#include "contribs/tags/ipv4hostgateway-tag.h"
#include "contribs/tags/ipv4hostip-tag.h"
#include "contribs/tags/ipv4hostnetmask-tag.h"
#include "contribs/tags/ipv4subnet-tag.h"
#include "exists-tag.h"
#include "foreach-tag.h"
#include "len-tag.h"
#include "oneof-tag.h"

namespace jsonteng {

class TagMap {
public:
  TagMap(const TagResolverIf &tag_resolver) {
    m_tag_map.emplace(AtTag_name,
                      std::shared_ptr<TagBase>(new AtTag(tag_resolver)));
    m_tag_map.emplace(ExistsTag_name,
                      std::shared_ptr<TagBase>(new ExistsTag(tag_resolver)));
    m_tag_map.emplace(ForEachTag_name,
                      std::shared_ptr<TagBase>(new ForEachTag(tag_resolver)));
    m_tag_map.emplace(LenTag_name,
                      std::shared_ptr<TagBase>(new LenTag(tag_resolver)));
    m_tag_map.emplace(OneOfTag_name,
                      std::shared_ptr<TagBase>(new OneOfTag(tag_resolver)));
    m_tag_map.emplace(
        Ipv4HostGateway_name,
        std::shared_ptr<TagBase>(new Ipv4HostGatewayTag(tag_resolver)));
    m_tag_map.emplace(
        Ipv4HostIp_name,
        std::shared_ptr<TagBase>(new Ipv4HostIpTag(tag_resolver)));
    m_tag_map.emplace(
        Ipv4HostNetmask_name,
        std::shared_ptr<TagBase>(new Ipv4HostNetmaskTag(tag_resolver)));
    m_tag_map.emplace(Ipv4Subnet_name, std::shared_ptr<TagBase>(
                                           new Ipv4SubnetTag(tag_resolver)));
  }

  virtual ~TagMap() {}

  const std::unordered_map<std::string, std::shared_ptr<TagBaseIf>>
  get_tag_map() const {
    return m_tag_map;
  }

  const std::vector<std::string> get_tag_names() {
    std::vector<std::string> names;
    names.reserve(m_tag_map.size());
    for (auto tag : m_tag_map) {
      names.push_back(tag.first);
    }
    return names;
  }

private:
  std::unordered_map<std::string, std::shared_ptr<TagBaseIf>> m_tag_map;
};

} // namespace jsonteng
