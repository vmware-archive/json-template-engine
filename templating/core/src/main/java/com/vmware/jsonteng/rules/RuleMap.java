// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.rules;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.Map;

import com.vmware.jsonteng.RuleResolver;
import com.vmware.jsonteng.TemplateEngineException;

public class RuleMap {
    private static final Map<String, Class<?>> ruleClassMap;

    static {
        ruleClassMap = new Hashtable<>();

        ruleClassMap.put(AtRule.name, AtRule.class);
        ruleClassMap.put(ExistsRule.name, ExistsRule.class);
        ruleClassMap.put(ForEachRule.name, ForEachRule.class);
        ruleClassMap.put(LenRule.name, LenRule.class);
        ruleClassMap.put(OneOfRule.name, OneOfRule.class);
    }

    public static Map<String, RuleBase> getRuleMap(RuleResolver ruleResolver) throws TemplateEngineException {
        Map<String, RuleBase> ruleMap = new HashMap<>();
        for (Map.Entry<String, Class<?>> entry : ruleClassMap.entrySet()) {
            try {
                Constructor<RuleBase> ctor = (Constructor<RuleBase>) entry.getValue().getConstructor(
                        RuleResolver.class);
                RuleBase object = ctor.newInstance(ruleResolver);
                ruleMap.put(entry.getKey(), object);
            } catch (NoSuchMethodException | InstantiationException |
                    IllegalAccessException | InvocationTargetException e) {
                throw new TemplateEngineException("Failed to add rule " + entry.getKey(), e);
            }
        }
        return ruleMap;
    }

    public static void addRule(String ruleName, Class<?> rule) {
        ruleClassMap.put(ruleName, rule);
    }

    public static String[] getRuleNames() {
        return ruleClassMap.keySet().toArray(new String[0]);
    }
}
