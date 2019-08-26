// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

namespace jsonteng {

class Stats {
public:
  Stats() {}

  void updateStats(const std::string &parameter) {
    if (m_parameter_map.find(parameter) != m_parameter_map.end()) {
      m_parameter_map[parameter] = m_parameter_map[parameter] + 1;
    } else {
      m_parameter_map[parameter] = 1;
    }
  }

  const std::unordered_map<std::string, int> get_stats() {
    return m_parameter_map;
  }

  void clear() {
    m_parameter_map.clear();
  }

private:
  std::unordered_map<std::string, int> m_parameter_map;
};

} // namespace jsonteng