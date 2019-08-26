// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include <json.hpp>

namespace jsonteng {

class JsonLoader {
public:
  virtual nlohmann::json
  load(const std::string &json_resource) = 0;

  virtual void unload(const std::string &json_resource) = 0;
};

} // namespace jsonteng