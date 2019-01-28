// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.rules;

import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.ElementResolver;
import com.vmware.jsonteng.RuleResolver;
import com.vmware.jsonteng.TemplateEngineException;

public class OneOfRule extends RuleBase {
    static final String name = "one-of";

    private final ElementResolver elementResolver;

    public OneOfRule(RuleResolver ruleResolver) {
        super(ruleResolver);
        elementResolver = ruleResolver.getElementResolver();
    }

    @Override
    public Object process(List<?> ruleTokens, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        int tokenCount = ruleTokens.size();
        if (tokenCount < 1) {
            throw new TemplateEngineException(
                    String.format("Rule \"%s\" needs at least 1 parameters. Parameters given %s", name, ruleTokens));
        }
        for (int i = 0; i < tokenCount; i++) {
            Object item = ruleTokens.get(i);
            if (item instanceof List && ((List) item).size() == 2) {
                Object condition = ((List) item).get(0);
                Object value = ((List) item).get(1);
                Object conditionExpr = elementResolver.resolve(condition, bindingDataList);
                boolean result = safeEval(conditionExpr);
                if (result) {
                    return elementResolver.resolve(value, bindingDataList);
                }
            }
            else {
                if (i == (tokenCount -1) && !(item instanceof List)) {
                    return elementResolver.resolve(ruleTokens.get(tokenCount - 1), bindingDataList);
                }
                else {
                    throw new TemplateEngineException(
                            String.format("Rule \"%s\" contains an invalid parameter. %s", name, item));
                }
            }
        }
        return RuleBase.RULE_NONE;
    }
}
