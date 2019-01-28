// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.rules.RuleBase;
import com.vmware.jsonteng.rules.RuleMap;

public class RuleResolver {
    private static final char RULE_MAKER= '#';

    private final ElementResolver elementResolver;
    private final JsonLoader templateLoader;
    private final Map<String, RuleBase> ruleMap;

    RuleResolver(ElementResolver elementResolver, JsonLoader templateLoader) throws TemplateEngineException {
        this.elementResolver = elementResolver;
        this.templateLoader = templateLoader;
        ruleMap = RuleMap.getRuleMap(this);
    }

    Object resolve(List<?> ruleData, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        String ruleName = ((String) ruleData.get(0)).substring(1);
        if (ruleMap.containsKey(ruleName)) {
            RuleBase rule = ruleMap.get(ruleName);
            List<?> ruleToken = ruleData.subList(1, ruleData.size());
            return rule.process(ruleToken, bindingDataList);
        }
        else {
            throw new TemplateEngineException(String.format("Unknown rule %s", ruleName));
        }
    }

    public ElementResolver getElementResolver() {
        return this.elementResolver;
    }

    public JsonLoader getTemplateLoader() {
        return this.templateLoader;
    }

    static boolean isKeyRule(Object key) {
        return key instanceof String && ((String) key).length() > 1 && ((String) key).charAt(0) == RULE_MAKER;
    }

    static boolean isRule(Object ruleData) {
        return ruleData instanceof List && ((List) ruleData).size() > 0 && ((List) ruleData).get(0) instanceof String
               && ((String) ((List) ruleData).get(0)).length() > 1
               && ((String) ((List) ruleData).get(0)).charAt(0) == RULE_MAKER;
    }
}
