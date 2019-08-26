// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "json-loader.h"
#include "interfaces.h"
#include "stats.h"
#include "string-resolver.h"
#include "tag-resolver.h"

namespace jsonteng {

class StringResolver;

class ElementResolver : public ElementResolverIf {
public:
  ElementResolver(JsonLoader &template_loader, Stats &stats)
      : m_string_resolver(*this, stats),
        m_tag_resolver(*this, template_loader) {}

  virtual ~ElementResolver() {}

  nlohmann::json
  resolve(const nlohmann::json &element,
          const std::vector<nlohmann::json> &binding_data_list) const override {
    if (element.is_string()) {
      return m_string_resolver.resolve(element, binding_data_list);
    } else if (element.is_number()) {
      return element;
    } else if (element.is_boolean()) {
      return element;
    } else if (element.is_null()) {
      return element;
    } else if (element.is_object()) {
      nlohmann::json new_element = nlohmann::json::object();
      for (auto item : element.items()) {
        auto key = item.key();
        auto value = item.value();
        if (m_tag_resolver.is_key_tag(key)) {
          if (!value.is_array()) {
            throw TemplateEngineException(
                std::string("Value must be a list if name is a tag: ") + key +
                " " + value.dump());
          }
          nlohmann::json tag_temp = nlohmann::json::array();
          tag_temp.push_back(key);
          tag_temp.insert(tag_temp.end(), value.begin(), value.end());
          try {
            nlohmann::json resolved_tuple =
                resolve(tag_temp, binding_data_list);
            if (resolved_tuple.is_object()) {
              new_element.update(resolved_tuple);
            } else {
              throw TemplateEngineException(
                  std::string(
                      "Invalid tag result format for JSON object name tag: ") +
                  key + " " + value.dump() + " => " + resolved_tuple.dump());
            }
          } catch (TagNoneException &ignore) {
          }
        } else {
          try {
            auto new_key = resolve(key, binding_data_list);
            auto new_value = resolve(value, binding_data_list);
            if (new_key.is_string()) {
              new_element.emplace(new_key, new_value);
            }
          } catch (TagNoneException &ignore) {
          }
        }
      }
      return new_element;
    } else if (element.is_array()) {
      if (m_tag_resolver.is_tag(element)) {
        return m_tag_resolver.resolve(element, binding_data_list);
      }
      nlohmann::json new_element = nlohmann::json::array();
      for (auto item : element) {
        try {
          nlohmann::json new_item = resolve(item, binding_data_list);
          new_element.push_back(new_item);
        } catch (TagNoneException &ignore) {
        }
      }
      return new_element;
    }
    throw TemplateEngineException(std::string("Unknwon data type"));
  }

  const std::vector<std::string> get_tag_names() override {
    return m_tag_resolver.get_tag_names();
  }

private:
  StringResolver m_string_resolver;
  TagResolver m_tag_resolver;
};

} // namespace jsonteng