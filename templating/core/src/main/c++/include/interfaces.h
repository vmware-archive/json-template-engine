// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include "json-loader.h"
#include <json.hpp>

namespace jsonteng {

class TagBaseIf {
public:
  virtual nlohmann::json
  process(const std::vector<nlohmann::json> &tag_tokens,
          const std::vector<nlohmann::json> &binding_data_list) = 0;

  virtual const std::string get_name() = 0;

  virtual ~TagBaseIf() {}
};

class ElementResolverIf {
public:
  virtual nlohmann::json
  resolve(const nlohmann::json &element,
          const std::vector<nlohmann::json> &binding_data_list) const = 0;

  virtual const std::vector<std::string> get_tag_names() = 0;

  virtual ~ElementResolverIf() {}
};

class TagResolverIf {
public:
  virtual const ElementResolverIf &get_element_resolver() const = 0;

  virtual JsonLoader &get_template_loader() const = 0;

  virtual const std::vector<std::string> get_tag_names() = 0;

  virtual ~TagResolverIf() {}
};

} // namespace jsonteng