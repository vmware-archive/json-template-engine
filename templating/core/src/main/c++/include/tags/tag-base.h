// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "../interfaces.h"
#include "../utils.h"
#include "template-engine-exception.h"

namespace jsonteng {

class TagBase : public TagBaseIf {
public:
  TagBase(const TagResolverIf &tag_resolver, const std::string &name)
      : m_tag_resolver(tag_resolver), m_name(name) {}
  virtual ~TagBase() {}

  virtual nlohmann::json
  process(const std::vector<nlohmann::json> &tag_tokens,
          const std::vector<nlohmann::json> &binding_data_list) = 0;

  const std::string get_name() { return m_name; }

protected:
  const TagResolverIf &m_tag_resolver;
  const std::string m_name;

  bool safe_eval(const std::string &expr) {
    if (expr == "True") {
      return true;
    } else if (expr == "False") {
      return false;
    }
    std::string script =
        std::string("print(eval('") + expr + "', {'__builtins__': None}, {}))";
    std::string cmd = std::string("python -c \"") + Utils::escape_quotes(script) + "\"";
    std::string result;
    std::array<char, 128> buffer;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(
        popen(cmd.c_str(), "r"), pclose);
    if (!pipe) {
      throw TemplateEngineException(std::string("Failed to evaluate ") + expr);
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
      result += buffer.data();
    }
    // trim the result
    while (!result.empty() && std::isspace(result.back())) result.pop_back();
    std::reverse(result.begin(), result.end());
    while (!result.empty() && std::isspace(result.back())) result.pop_back();
    std::reverse(result.begin(), result.end());
    return result == "True";
  }

  std::string tokens_to_string(const std::vector<nlohmann::json> &tokens) {
    std::string result;
    if (tokens.size() < 1) {
      return result;
    }
    size_t i = 0;
    result = tokens[0].dump();
    for (i = 1; i < tokens.size(); i++) {
      result += ", " + tokens[i].dump();
    }
    return result;
  }
};

} // namespace jsonteng