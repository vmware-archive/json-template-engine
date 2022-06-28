// Copyright 2022 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include <algorithm>
#include <string>
#include "tag-base.h"

namespace jsonteng {
static const std::string ToBoolTag_name("to-bool");

class ToBoolTag : public TagBase {
public:
  ToBoolTag(const TagResolverIf &tag_resolver)
      : TagBase(tag_resolver, ToBoolTag_name) {}
  virtual ~ToBoolTag() {}

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
    if (resolved_data.is_string()) {
      std::string value = resolved_data;
      std::transform(value.begin(), value.end(), value.begin(), ::tolower);
      if (value.compare("true") == 0) {
        return true;
      } else if (value.compare("false") == 0) {
        return false;
      } else {
        throw TemplateEngineException(
            std::string("Tag \"") + m_name +
            "\" invalid string " +
            resolved_data.dump());
      }
    } else {
      throw TemplateEngineException(
          std::string("Tag \"") + m_name +
          "\" parameter not a string type " +
          resolved_data.dump());
    }
  }
};

} // namespace jsonteng
