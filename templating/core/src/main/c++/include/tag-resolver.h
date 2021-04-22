// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "interfaces.h"
#include "json-loader.h"
#include "tags/tag-base.h"
#include "tags/tag-map.h"

namespace jsonteng {

static const char TAG_MARKER = '#';
static const char LABEL_SEPARATOR = ':';

class TagResolver : public TagResolverIf {
public:
  TagResolver(const ElementResolverIf &element_resolver,
              JsonLoader &template_loader)
      : m_element_resolver(element_resolver),
        m_template_loader(template_loader), m_tag_map(*this) {}

  static bool is_key_tag(const nlohmann::json &key) {
    return key.is_string() && key.get<std::string>().size() > 1 &&
           key.get<std::string>()[0] == TAG_MARKER;
  }

  static bool is_tag(const nlohmann::json &tag_data) {
    return tag_data.is_array() && tag_data.size() > 0 &&
           tag_data[0].is_string() &&
           tag_data[0].get<std::string>()[0] == TAG_MARKER;
  }

  nlohmann::json
  resolve(const nlohmann::json &tag_data,
          const std::vector<nlohmann::json> &binding_data_list) const {
    std::string tag_name = tag_data[0].get<std::string>().substr(1);
    size_t label_index = tag_name.find(LABEL_SEPARATOR);
    if (label_index != std::string::npos) {
      tag_name = tag_name.substr(0, label_index);
    }
    auto tag_map = m_tag_map.get_tag_map();
    if (tag_map.find(tag_name) != tag_map.end()) {
      std::shared_ptr<TagBaseIf> tag = tag_map[tag_name];
      std::vector<nlohmann::json> tag_tokens;
      if (tag_data.size() > 1) {
        tag_tokens = {&tag_data[1], &tag_data[tag_data.size()]};
      }
      return tag->process(tag_tokens, binding_data_list);
    } else {
      throw TemplateEngineException(std::string("Unknown tag \"" + tag_name + "\"."));
    }
  }

  const ElementResolverIf &get_element_resolver() const override {
    return m_element_resolver;
  }

  JsonLoader &get_template_loader() const override { return m_template_loader; }

  const std::vector<std::string> get_tag_names() override {
    return m_tag_map.get_tag_names();
  }

private:
  const ElementResolverIf &m_element_resolver;
  JsonLoader &m_template_loader;
  TagMap m_tag_map;
};

} // namespace jsonteng