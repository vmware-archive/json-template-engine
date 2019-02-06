// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.rules;

import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.ElementResolver;
import com.vmware.jsonteng.RuleResolver;
import com.vmware.jsonteng.TemplateEngineException;
import com.vmware.jsonteng.UnresolvableParameterException;

public class ExistsRule extends RuleBase {
    static final String name = "exists";

    private final ElementResolver elementResolver;

    public ExistsRule(RuleResolver ruleResolver) {
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
        try {
            elementResolver.resolve(data, bindingDataList);
        }
        catch (UnresolvableParameterException e) {
            return "1==0";
        }
        return "1==1";
    }
}
