// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.rules.RuleNone;

public class ElementResolver {
    private final StringResolver stringResolver;
    private final RuleResolver ruleResolver;

    ElementResolver(JsonLoader templateLoader, Stats stats) throws TemplateEngineException {
        stringResolver = new StringResolver(this, stats);
        ruleResolver = new RuleResolver(this, templateLoader);
    }

    @SuppressWarnings("unchecked")
    public Object resolve(Object element, List<Map<String,?>> bindingDataList) throws TemplateEngineException {
        if (element instanceof String) {
            return stringResolver.resolve((String) element, bindingDataList);
        }
        else if (element instanceof Number) {
            return element;
        }
        else if (element instanceof Boolean) {
            return element;
        }
        else if (element == null) {
            return null;
        }
        else if (element instanceof Map) {
            Map<Object, Object> newElement = new HashMap<>();
            for (Map.Entry entry : ((Map<Object, Object>) element).entrySet()) {
                Object key = entry.getKey();
                Object value = entry.getValue();
                if (RuleResolver.isKeyRule(key)) {
                    if (!(value instanceof List)) {
                        throw new TemplateEngineException(
                                String.format("Value must be a list if name is a rule: %s %s", key, value));
                    }
                    List<Object> ruleTemp = new ArrayList<>();
                    ruleTemp.add(key);
                    ruleTemp.addAll((List) value);
                    Object resolvedTuple = resolve(ruleTemp, bindingDataList);
                    if (resolvedTuple instanceof Map) {
                        newElement.putAll((Map) resolvedTuple);
                    }
                    else if (!(resolvedTuple instanceof RuleNone)) {
                        throw new TemplateEngineException(
                                String.format("Invalid rule result format for JSON object name rule: %s %s => %s",
                                              key, value, resolvedTuple));
                    }
                }
                else {
                    Object newKey = resolve(key, bindingDataList);
                    Object newValue = resolve(value, bindingDataList);
                    if (newKey instanceof String && !(newValue instanceof RuleNone)) {
                        newElement.put(newKey, newValue);
                    }
                }
            }
            return newElement;
        }
        else if (element instanceof List) {
            if (RuleResolver.isRule(element)) {
                return ruleResolver.resolve((List) element, bindingDataList);
            }
            List<Object> newElement = new ArrayList<>();
            for (Object item : (List) element) {
                Object newItem = resolve(item, bindingDataList);
                if (!(newItem instanceof RuleNone)) {
                    newElement.add(newItem);
                }
            }
            return newElement;
        }
        throw new TemplateEngineException(
                String.format("Unknown data type %s of %s", element.getClass().getCanonicalName(), element));
    }
}
