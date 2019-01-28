// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.rules;

import java.util.List;
import java.util.Map;

public class RuleNone extends RuleBase {

    RuleNone() {
        super(null);
    }

    @Override
    public Object process(List<?> ruleTokens, List<Map<String, ?>> bindingDataList) {
        throw new UnsupportedOperationException();
    }

    @Override
    public boolean equals(Object o) {
        return o instanceof  RuleNone;
    }
}
