// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@SuppressWarnings("unchecked")
class Utils {
    static Object unescapeJson(Object element) throws TemplateEngineException {
        if (element instanceof String) {
            return unescapeString((String) element);
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
                Object newKey = unescapeJson(key);
                Object newValue = unescapeJson(value);
                newElement.put(newKey, newValue);
            }
            return newElement;
        }
        else if (element instanceof List) {
            List<Object> newElement = new ArrayList<>();
            for (Object item : (List<Object>) element) {
                Object newItem = unescapeJson(item);
                newElement.add(newItem);
            }
            return newElement;
        }
        else {
            throw new TemplateEngineException(
                    String.format("Unknown data type %s of %s.", element.getClass().getCanonicalName(), element));
        }
    }

    private static String unescapeString(String escapedString) {
        StringBuilder builder = new StringBuilder();
        int start = 0;
        int index;
        while ((index = escapedString.indexOf('\\', start)) != -1) {
            builder.append(escapedString, start, index);
            start = index + 1;
        }
        builder.append(escapedString.substring(start));
        return builder.toString();
    }

    static Map<String, List> checkDuplicatedBindingData(List<Map<String,?>> bindingDataList) {
        Map<String, List> bindingDataMap = new HashMap<>();
        for (Map<String, ?> bindingData : bindingDataList) {
            findParamTerminal(null, bindingData, bindingDataMap);
        }
        Map<String, List> dupMap = new HashMap<>();
        for (Map.Entry<String, List> item : bindingDataMap.entrySet()) {
            if (item.getValue().size() > 1) {
                dupMap.put(item.getKey(), item.getValue());
            }
        }
        return dupMap;
    }

    private static void findParamTerminal(
            String superName, Map<String, ?> bindingData, Map<String, List> bindingDataMap) {
        for (Map.Entry<String, ?> item : bindingData.entrySet()) {
            String name = item.getKey();
            if (superName != null) {
                name = superName + '.' + name;
            }
            if (item.getValue() instanceof Map) {
                findParamTerminal(name, (Map<String, ?>) item.getValue(), bindingDataMap);
            }
            else {
                if (!bindingDataMap.containsKey(name)) {
                    bindingDataMap.put(name, new ArrayList<>());
                }
                List<Object> values = bindingDataMap.get(name);
                values.add(item.getValue());
            }
        }
    }
}
