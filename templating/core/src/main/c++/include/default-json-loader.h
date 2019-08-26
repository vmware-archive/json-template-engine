// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "json-loader.h"
#include "template-engine-exception.h"
#include <fstream>
#include <iostream>
#include <json.hpp>
#include <memory>
#include <regex>
#include <stack>

namespace jsonteng {

class DefaultJsonLoader : public JsonLoader {
public:
  DefaultJsonLoader(const std::string &root_path, const bool verbose)
      : m_verbose(verbose) {
    m_dir_stack.emplace("root", root_path);
  }

  virtual ~DefaultJsonLoader() {}

  virtual nlohmann::json load(const std::string &json_resource) override {
    const DirData &parent = m_dir_stack.top();
    std::string effective_url = parent.get_effective_url() + json_resource;
    try {
      nlohmann::json json_object =
          nlohmann::json::parse(std::ifstream(effective_url));
      int lastDirIndex = effective_url.find_last_of('/');
      m_dir_stack.emplace(json_resource,
                          effective_url.substr(0, lastDirIndex + 1));
      return json_object;
    } catch (nlohmann::json::parse_error &e) {
      if (m_verbose) {
        std::cout << "Treat " << json_resource << " as JSON value.\n";
      }
      try {
        nlohmann::json json_object = nlohmann::json::parse(json_resource);
        m_dir_stack.emplace(json_resource, "");
        return json_object;
      } catch (nlohmann::json::parse_error &e) {
        if (is_number(json_resource)) {
          m_dir_stack.emplace(json_resource, "");
          return std::stoi(json_resource);
        } else if (is_decimal(json_resource)) {
          m_dir_stack.emplace(json_resource, "");
          return std::stod(json_resource);
        } else {
          m_dir_stack.emplace(json_resource, "");
          return json_resource;
        }
      }
    }
    throw TemplateEngineException(
        std::string("Failed to load JSON resource " + json_resource));
  }

  virtual void unload(const std::string &json_resource) override {
    DirData dir_data = m_dir_stack.top();
    m_dir_stack.pop();
    if (dir_data.get_json_resource() != json_resource) {
      throw TemplateEngineException("JSON resource loading is out of order.");
    }
  };

private:
  class DirData {
  public:
    DirData(const std::string &json_resource, const std::string &effective_url)
        : m_json_resource(json_resource), m_effective_url(effective_url){};

    inline std::string get_json_resource() const { return m_json_resource; };
    inline std::string get_effective_url() const { return m_effective_url; };

  private:
    const std::string m_json_resource;
    const std::string m_effective_url;
  };

  std::stack<DirData> m_dir_stack;
  const bool m_verbose;

  bool is_number(const std::string &s) {
    return std::regex_match(s, std::regex("-?[0-9]+"));
  }

  bool is_decimal(const std::string &s) {
    return std::regex_match(s, std::regex("-?[0-9]+([.][0-9]+)"));
  }
};

} // namespace jsonteng
