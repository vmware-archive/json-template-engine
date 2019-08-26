// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "tag-base.h"

namespace jsonteng {
static const std::string ForEachTag_name("for-each");

class ForEachTag : public TagBase {
public:
  ForEachTag(const TagResolverIf &tag_resolver)
      : TagBase(tag_resolver, ForEachTag_name) {}
  virtual ~ForEachTag() {}

  nlohmann::json
  process(const std::vector<nlohmann::json> &tag_tokens,
          const std::vector<nlohmann::json> &binding_data_list) override {
    if (tag_tokens.size() < 2 || tag_tokens.size() > 3) {
      throw TemplateEngineException(
          std::string("Tag \"") + m_name +
          "\" requires 2 or 3 parameters. Parameters given " +
          tokens_to_string(tag_tokens));
    }
    const ElementResolverIf &element_resolver =
        m_tag_resolver.get_element_resolver();
    JsonLoader &template_loader = m_tag_resolver.get_template_loader();
    nlohmann::json data_list = tag_tokens[0];
    nlohmann::json json_template = tag_tokens[1];
    try {
      json_template =
          element_resolver.resolve(json_template, binding_data_list);
    } catch (TemplateEngineException &ignore) {
    }
    const nlohmann::json template_json =
        template_loader.load(json_template.get<std::string>());
    nlohmann::json resolved_data_list =
        element_resolver.resolve(data_list, binding_data_list);
    nlohmann::json resolved_json = nlohmann::json::array();
    nlohmann::json index_data = nlohmann::json::object();
    for (size_t i = 0; i < resolved_data_list.size(); i++) {
      index_data["_index_"] = i;
      std::vector<nlohmann::json> effective_binding_data_list;
      effective_binding_data_list.push_back(index_data);
      effective_binding_data_list.push_back(resolved_data_list[i]);
      effective_binding_data_list.insert(effective_binding_data_list.end(),
                                         binding_data_list.begin(),
                                         binding_data_list.end());
      if (tag_tokens.size() == 3) {
        nlohmann::json condition_expr = element_resolver.resolve(
            tag_tokens[2], effective_binding_data_list);
        if (!safe_eval(condition_expr)) {
          continue;
        }
      }
      nlohmann::json resolved_template =
          element_resolver.resolve(template_json, effective_binding_data_list);
      resolved_json.push_back(resolved_template);
    }
    template_loader.unload(json_template.get<std::string>());
    return resolved_json;
  }
};

} // namespace jsonteng
