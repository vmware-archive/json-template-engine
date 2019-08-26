// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "default-json-loader.h"
#include "element-resolver.h"
#include "stats.h"
#include "tags/tag-base.h"
#include "utils.h"

namespace jsonteng {

class TemplateEngine {
public:
  TemplateEngine() : TemplateEngine(nullptr) {}

  TemplateEngine(const nlohmann::json &env)
      : TemplateEngine(env, nullptr, false) {}

  TemplateEngine(const nlohmann::json &env,
                 std::shared_ptr<JsonLoader> template_loader, bool verbose)
      : m_env(env) {
    if (template_loader != nullptr) {
      m_template_loader = template_loader;
    } else {
      char *root_path = std::getenv("TEMPLATE_HOME");
      m_template_loader = std::shared_ptr<JsonLoader>(new DefaultJsonLoader(
          root_path == nullptr ? "" : root_path, verbose));
    }
    m_element_resolver = std::unique_ptr<ElementResolverIf>(
        new ElementResolver(*m_template_loader, m_stats));
  }

  nlohmann::json resolve(const std::string &main_template,
                         const std::vector<nlohmann::json> &binding_data_list) {
    m_stats.clear();
    nlohmann::json main_template_json = m_template_loader->load(main_template);
    std::vector<nlohmann::json> effective_binding_data_list(binding_data_list);
    effective_binding_data_list.push_back(m_env);
    m_dup_params =
        Utils::check_duplicated_binding_data(effective_binding_data_list);
    nlohmann::json resolved_json = m_element_resolver->resolve(
        main_template_json, effective_binding_data_list);
    m_template_loader->unload(main_template);
    return Utils::unescape_json(resolved_json);
  }

  const std::unordered_map<std::string, std::vector<nlohmann::json>>
  get_duplicated_parameters() {
    return m_dup_params;
  }

  const std::unordered_map<std::string, int> get_stats() {
    return m_stats.get_stats();
  }

  const std::vector<std::string> list_tag_names() {
    return m_element_resolver->get_tag_names();
  }

private:
  const nlohmann::json &m_env;
  std::shared_ptr<JsonLoader> m_template_loader;
  std::unordered_map<std::string, std::vector<nlohmann::json>> m_dup_params;
  Stats m_stats;
  std::unique_ptr<ElementResolverIf> m_element_resolver;
};

} // namespace jsonteng