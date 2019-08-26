// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "interfaces.h"
#include "stats.h"
#include "template-engine-exception.h"
#include <regex>

namespace jsonteng {

std::regex ARRAY_PATTERN("([a-zA-Z0-9]+)\\[([0-9]+)\\]");

class ElementResolver;

class StringResolver {
public:
  StringResolver(const ElementResolverIf &element_resolver, Stats &stats)
      : m_element_resolver(element_resolver), m_stats(stats) {}

  nlohmann::json
  resolve(const std::string &str,
          const std::vector<nlohmann::json> &binding_data_list) const {
    std::string str_data(str);
    int str_len = str_data.size();
    std::stack<int> stack;
    int i = 0;
    while (i < str_len) {
      char c = str_data[i];
      if (c == '\\') {
        i += 2;
      } else if (c == '$') {
        int next_index = i + 1;
        if (next_index < str_len && str_data[next_index] == '{') {
          stack.emplace(i);
          i += 2;
        } else {
          i += 1;
        }
      } else if (c == '}') {
        i += 1;
        if (!stack.empty()) {
          int param_start = stack.top();
          stack.pop();
          const std::string param_name =
              str_data.substr(param_start + 2, i - param_start - 3);
          nlohmann::json value = resolve_param(param_name, binding_data_list);
          std::string substr_before_param = str_data.substr(0, param_start);
          std::string substr_after_param = "";
          if (i < str_len) {
            substr_after_param = str_data.substr(i);
          }
          if (substr_before_param.size() > 0 || substr_after_param.size() > 0) {
            std::string new_str;
            new_str = substr_before_param +
                      data_to_string(m_element_resolver.resolve(
                          value, binding_data_list)) +
                      substr_after_param;
            str_data = new_str;
            str_len = str_data.size();
            i = param_start;
          } else {
            return m_element_resolver.resolve(value, binding_data_list);
          }
        }
      } else {
        i += 1;
      }
    }
    if (!stack.empty()) {
      throw TemplateEngineException(
          std::string("Mis-formed parameterized string. " + str_data));
    }
    return str_data;
  }

private:
  const ElementResolverIf &m_element_resolver;
  Stats &m_stats;

  nlohmann::json
  resolve_param(const std::string &param_name,
                const std::vector<nlohmann::json> &binding_data_list) const {
    std::vector<int> separator_indices = collect_separator_indices(param_name);
    for (auto binding_data : binding_data_list) {
      try {
        nlohmann::json value =
            find_param(param_name, separator_indices, binding_data);
        m_stats.updateStats(param_name);
        return value;
      } catch (InvalidReferenceException &ignore) {
      }
    }
    throw UnresolvableParameterException(
        std::string("Unable to resolve parameter " + param_name));
  }

  static nlohmann::json find_param(const std::string &param_name,
                                   const std::vector<int> &separator_indices,
                                   const nlohmann::json &binding_data) {
    size_t token_start = 0;
    nlohmann::json next_data = binding_data;
    for (size_t i = 0; i < separator_indices.size() + 1; i++) {
      if (!next_data.is_object()) {
        throw InvalidReferenceException("invalid scope");
      }
      std::string key = param_name.substr(token_start);
      try {
        return match_key(key, next_data);
      } catch (InvalidReferenceException &ignore) {
        // ignore
      }
      if (i < separator_indices.size()) {
        std::string token = param_name.substr(
            token_start,
            separator_indices[i] - (i == 0 ? 0 : (separator_indices[i - 1]  + 1)));
        next_data = match_key(token, next_data);
        token_start = separator_indices[i] + 1;
      }
    }
    throw InvalidReferenceException("mismatch binding data");
  }

  static nlohmann::json match_key(const std::string &key,
                                  const nlohmann::json &data) {
    std::smatch match_result;
    if (std::regex_match(key, match_result, ARRAY_PATTERN)) {
      std::string actual_key = match_result[1];
      std::string index_str = match_result[2];
      if (!index_str.empty()) {
        int index = std::stoi(index_str);
        if (index < 0) {
          throw TemplateEngineException(
              std::string("Parameter index is negative: ") + key);
        }
        if (data.contains(actual_key)) {
          auto value = data[actual_key];
          if (value.is_array() && (size_t)index < value.size()) {
            return value[index];
          }
        }
        throw InvalidReferenceException("mismatch binding data");
      }
      throw TemplateEngineException(std::string("Parameter index missing: ") +
                                    key);
    }
    if (data.contains(key)) {
      return data[key];
    }
    throw InvalidReferenceException("mismatch binding data");
  }

  static std::vector<int>
  collect_separator_indices(const std::string &param_name) {
    std::vector<int> indices;
    for (size_t i = 0; i < param_name.size(); i++) {
      char c = param_name[i];
      if (c == '\\') {
        i += 1;
      } else if (c == '.') {
        indices.push_back(i);
      }
    }
    return indices;
  }

  static std::string data_to_string(const nlohmann::json &value) {
    std::string value_str;
    if (value.is_string()) {
      value_str = value.get<std::string>();
    } else {
      value_str = value.dump();
    }
    return value_str;
  }
};

} // namespace jsonteng