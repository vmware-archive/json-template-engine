// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "tag-base.h"

namespace jsonteng {
static const std::string AtTag_name("at");

class AtTag : public TagBase {
public:
  AtTag(const TagResolverIf &tag_resolver)
      : TagBase(tag_resolver, AtTag_name) {}
  virtual ~AtTag() {}

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
    const nlohmann::json data = tag_tokens[0];
    const nlohmann::json key = tag_tokens[1];
    nlohmann::json resolved_data =
        element_resolver.resolve(data, binding_data_list);
    nlohmann::json resolved_key =
        element_resolver.resolve(key, binding_data_list);
    if (resolved_data.is_array()) {
      return resolved_data[resolved_key.get<int>()];
    } else if (resolved_data.is_object()) {
      return resolved_data[resolved_key.get<std::string>()];
    } else {
      throw TagNoneException();
    }
  }
};

} // namespace jsonteng
