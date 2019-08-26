// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "tag-base.h"

namespace jsonteng {
static const std::string OneOfTag_name("one-of");

class OneOfTag : public TagBase {
public:
  OneOfTag(const TagResolverIf &tag_resolver)
      : TagBase(tag_resolver, OneOfTag_name) {}
  virtual ~OneOfTag() {}

  nlohmann::json
  process(const std::vector<nlohmann::json> &tag_tokens,
          const std::vector<nlohmann::json> &binding_data_list) override {
    if (tag_tokens.size() < 1) {
      throw TemplateEngineException(
          std::string("Tag \"") + m_name +
          "\" requires at least 1 parameter. Parameters given " +
          tokens_to_string(tag_tokens));
    }
    const ElementResolverIf &element_resolver =
        m_tag_resolver.get_element_resolver();
    size_t token_count = tag_tokens.size();
    for (size_t i = 0; i < token_count; i++) {
      nlohmann::json item = tag_tokens[i];
      if (item.is_array() && item.size() == 2) {
        nlohmann::json condition = item[0];
        nlohmann::json value = item[1];
        nlohmann::json condition_expr =
            element_resolver.resolve(condition, binding_data_list);
        bool result = safe_eval(condition_expr.get<std::string>());
        if (result) {
          return element_resolver.resolve(value, binding_data_list);
        }
      } else {
        if (i == (token_count - 1) && !item.is_array()) {
          return element_resolver.resolve(tag_tokens[token_count - 1],
                                          binding_data_list);
        } else {
          throw TemplateEngineException(std::string("Tag \"") + OneOfTag_name +
                                        "\" contains an invalid parameter. " +
                                        item.dump());
        }
      }
    }
    throw TagNoneException();
  }
};

} // namespace jsonteng
