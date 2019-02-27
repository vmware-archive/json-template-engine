// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.tags;

import java.util.List;
import java.util.Map;

public class TagNone extends TagBase {

    TagNone() {
        super(null);
    }

    @Override
    public Object process(List<?> tagTokens, List<Map<String, ?>> bindingDataList) {
        throw new UnsupportedOperationException();
    }

    @Override
    public boolean equals(Object o) {
        return o instanceof  TagNone;
    }
}
