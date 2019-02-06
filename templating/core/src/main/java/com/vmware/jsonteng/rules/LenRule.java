// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.rules;

import java.util.Collection;
import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.ElementResolver;
import com.vmware.jsonteng.RuleResolver;
import com.vmware.jsonteng.TemplateEngineException;

public class LenRule extends RuleBase {
    static final String name = "len";

    private final ElementResolver elementResolver;

    public LenRule(RuleResolver ruleResolver) {
        super(ruleResolver);
        elementResolver = ruleResolver.getElementResolver();
    }

    @Override
    public Object process(List<?> ruleTokens, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        int tokenCount = ruleTokens.size();
        if (tokenCount != 1) {
            throw new TemplateEngineException(
                    String.format("Rule \"%s\" requires 1 parameter. Parameters given %s", name, ruleTokens));
        }
        Object data = ruleTokens.get(0);
        Object resolvedData = elementResolver.resolve(data, bindingDataList);
        if (resolvedData != null) {
            return len(resolvedData);
        }
        else {
            return 0;
        }
    }

    private int len(Object data) {
        if (data instanceof Collection) {
            return ((Collection) data).size();
        }
        else if (data instanceof Map) {
            return ((Map) data).size();
        }
        else if (data instanceof String) {
            return ((CharSequence) data).length();
        }
        else {
            return -1;
        }
    }
}
