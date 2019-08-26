// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "tag-base.h"

namespace jsonteng {
static const std::string LenTag_name("len");

class LenTag : public TagBase {
public:
  LenTag(const TagResolverIf &tag_resolver)
      : TagBase(tag_resolver, LenTag_name) {}
  virtual ~LenTag() {}

  nlohmann::json
  process(const std::vector<nlohmann::json> &tag_tokens,
          const std::vector<nlohmann::json> &binding_data_list) override {
    if (tag_tokens.size() != 1) {
      throw TemplateEngineException(
          std::string("Tag \"") + m_name +
          "\" requires 1 parameter. Parameter given " +
          tokens_to_string(tag_tokens));
    }
    const ElementResolverIf &element_resolver =
        m_tag_resolver.get_element_resolver();
    const nlohmann::json data = tag_tokens[0];
    nlohmann::json resolved_data =
        element_resolver.resolve(data, binding_data_list);
    return len(resolved_data);
  }

private:
  int len(const nlohmann::json &data) {
    if (data.is_structured()) {
      return data.size();
    } else if (data.is_string()) {
      return data.get<std::string>().size();
    } else {
      return -1;
    }
  }
};

} // namespace jsonteng
