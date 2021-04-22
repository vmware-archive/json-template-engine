// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "template-engine-exception.h"
#include <json.hpp>

namespace jsonteng {

class Utils {
public:
  static std::string escape_quotes(const std::string &s) {
    std::string escaped;
    size_t start = 0;
    size_t found;
    while ((found = s.find('\"', start)) != std::string::npos) {
      escaped += s.substr(start, found - start) + "\\\"";
      start = found + 1;
    }
    return escaped + s.substr(start, found);
  }

  static const std::vector<std::string> split_string(const std::string &s,
                                                     const char sep) {
    std::vector<std::string> strings;
    std::istringstream iss(s);
    std::string item;
    while (getline(iss, item, sep)) {
      strings.push_back(item);
    }
    return strings;
  }

  static nlohmann::json unescape_json(const nlohmann::json &element) {
    if (element.is_string()) {
      return unescape_string(element);
    } else if (element.is_number()) {
      return element;
    } else if (element.is_boolean()) {
      return element;
    } else if (element.is_null()) {
      return element;
    } else if (element.is_object()) {
      nlohmann::json new_element = nlohmann::json::object();
      for (auto entry : element.items()) {
        nlohmann::json key = entry.key();
        nlohmann::json value = entry.value();
        nlohmann::json new_key = unescape_json(key);
        nlohmann::json new_value = unescape_json(value);
        new_element.emplace(new_key, new_value);
      }
      return new_element;
    } else if (element.is_array()) {
      nlohmann::json new_element = nlohmann::json::array();
      for (auto item : element) {
        nlohmann::json new_item = unescape_json(item);
        new_element.push_back(new_item);
      }
      return new_element;
    } else {
      throw TemplateEngineException(std::string("Unknown data type ") +
                                    element.type_name() + " of " +
                                    element.dump());
    }
  }

  static const std::unordered_map<std::string, std::vector<nlohmann::json>>
  check_duplicated_binding_data(
      std::vector<nlohmann::json> &binding_data_list) {
    std::unordered_map<std::string, std::vector<nlohmann::json>>
        binding_data_map;
    for (auto binding_data : binding_data_list) {
      std::string param_name;
      find_param_terminal(param_name, binding_data, binding_data_map);
    }
    std::unordered_map<std::string, std::vector<nlohmann::json>> dup_map;
    for (auto item : binding_data_map) {
      if (item.second.size() > 1) {
        dup_map.emplace(item.first, item.second);
      }
    }
    return dup_map;
  }

private:
  static nlohmann::json unescape_string(const nlohmann::json &escaped_string) {
    const std::string &orig = escaped_string.get<std::string>();
    std::string builder;
    size_t start = 0;
    size_t index;
    while ((index = orig.find('\\', start)) != std::string::npos) {
      builder += orig.substr(start, index - start) + orig[index+1];
      start = index + 2;
    }
    if (start < orig.size()) {
        builder += orig.substr(start);
    }
    return builder;
  }

  static void find_param_terminal(
      std::string &super_name, nlohmann::json &binding_data,
      std::unordered_map<std::string, std::vector<nlohmann::json>>
          &binding_data_map) {
    for (auto item : binding_data.items()) {
      std::string name = item.key();
      if (!super_name.empty()) {
        name = super_name + "." + name;
      }
      if (item.value().is_object()) {
        find_param_terminal(name, item.value(), binding_data_map);
      } else {
        if (binding_data_map.find(name) == binding_data_map.end()) {
          binding_data_map.emplace(name, std::vector<nlohmann::json>());
        }
        std::vector<nlohmann::json> &values = binding_data_map[name];
        values.push_back(item.value());
      }
    }
  }
};

} // namespace jsonteng