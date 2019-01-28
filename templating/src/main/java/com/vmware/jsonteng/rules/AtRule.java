// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.rules;

import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.ElementResolver;
import com.vmware.jsonteng.RuleResolver;
import com.vmware.jsonteng.TemplateEngineException;

public class AtRule extends RuleBase {
    static final String name = "at";

    private final ElementResolver elementResolver;

    public AtRule(RuleResolver ruleResolver) {
        super(ruleResolver);
        elementResolver = ruleResolver.getElementResolver();
    }

    @Override
    public Object process(List<?> ruleTokens, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        int tokenCount = ruleTokens.size();
        if (tokenCount != 2) {
            throw new TemplateEngineException(
                    String.format("Rule \"%s\" requires 2 parameters. Parameters given %s", name, ruleTokens));
        }
        Object data = ruleTokens.get(0);
        Object key = ruleTokens.get(1);
        Object resolvedData = elementResolver.resolve(data, bindingDataList);
        Object resolvedKey = elementResolver.resolve(key, bindingDataList);
        if (resolvedData instanceof List) {
            return ((List) resolvedData).get((int)resolvedKey);
        }
        else if (resolvedData instanceof Map) {
            return ((Map) resolvedData).get(resolvedKey);
        }
        else {
            return RuleBase.RULE_NONE;
        }
    }
}
