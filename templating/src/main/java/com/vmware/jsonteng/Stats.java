// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

import java.util.HashMap;
import java.util.Map;

class Stats {
    private final Map<String, Integer> parameterMap;

    Stats() {
        parameterMap = new HashMap<>();
    }

    void updateStats(String parameter) {
        if (parameterMap.containsKey(parameter)) {
            parameterMap.put(parameter, parameterMap.get(parameter) + 1);
        }
        else {
            parameterMap.put(parameter, 1);
        }
    }

    Map<String, Integer> getStats() {
        return parameterMap;
    }

    void clear() {
        parameterMap.clear();
    }
}
