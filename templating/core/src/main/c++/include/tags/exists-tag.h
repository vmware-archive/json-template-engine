// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "tag-base.h"

namespace jsonteng {
static const std::string ExistsTag_name("exists");

class ExistsTag : public TagBase {
public:
  ExistsTag(const TagResolverIf &tag_resolver)
      : TagBase(tag_resolver, ExistsTag_name) {}
  virtual ~ExistsTag() {}

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
    const nlohmann::json data = tag_tokens[0];
    try {
      element_resolver.resolve(data, binding_data_list);
    } catch (UnresolvableParameterException &e) {
      return "False";
    }
    return "True";
  }
};

} // namespace jsonteng
