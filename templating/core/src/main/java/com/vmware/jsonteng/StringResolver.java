// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Stack;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.jsonteng.tags.TagNone;

class StringResolver {
    private static final Pattern arrayPattern = Pattern.compile("([a-zA-Z0-9]+)\\[([0-9]+)\\]");

    private final ElementResolver elementResolver;
    private final Stats stats;
    private final ObjectMapper mapper;

    StringResolver(ElementResolver elementResolver, Stats stats) {
        this.elementResolver = elementResolver;
        this.stats = stats;
        mapper = new ObjectMapper();
    }

    Object resolve(String strData, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        int strLen = strData.length();
        Stack<Integer> stack = new Stack<>();
        int i = 0;
        while (i < strLen) {
            char c = strData.charAt(i);
            if (c == '\\') {
                i += 2;
            }
            else if (c == '$') {
                int nextIndex = i + 1;
                if (nextIndex < strLen && strData.charAt(nextIndex) == '{') {
                    stack.push(i);
                    i += 2;
                }
                else {
                    i += 1;
                }
            }
            else if (c == '}') {
                i += 1;
                if (!stack.empty()) {
                    int paramStart = stack.pop();
                    String paramName = strData.substring(paramStart+2, i - 1);
                    Object value = resolveParam(paramName, bindingDataList);
                    String subStrBeforeParam = strData.substring(0, paramStart);
                    String subStrAfterParam = "";
                    if (i < strLen) {
                        subStrAfterParam = strData.substring(i);
                    }
                    if (subStrBeforeParam.length() > 0 || subStrAfterParam.length() > 0) {
                        String newStr;
                        newStr = subStrBeforeParam
                                 + dataToString(elementResolver.resolve(value, bindingDataList))
                                 + subStrAfterParam;
                        strData = newStr;
                        strLen = strData.length();
                        i = paramStart;
                    } else {
                        return elementResolver.resolve(value, bindingDataList);
                    }
                }
            }
            else {
                i += 1;
            }
        }
        if (!stack.empty()) {
            throw new TemplateEngineException(String.format("Mis-formed parameterized string \"%s\".", strData));
        }
        return strData;
    }

    private Object resolveParam(String paramName, List<Map<String,?>> bindingDataList) throws TemplateEngineException {
        Integer[] separatorIndices = StringResolver.collectSeparatorIndices(paramName);
        for (Map<String, ?> bindingData : bindingDataList) {
            try {
                Object value = StringResolver.findParam(paramName, separatorIndices, bindingData);
                if (value != null) {
                    stats.updateStats(paramName);
                    return value;
                }
            }
            catch (InvalidReferenceException ignore) {
            }
        }
        throw new UnresolvableParameterException(String.format("Unable to resolve parameter \"%s\".", paramName));
    }

    @SuppressWarnings("unchecked")
    private static Object findParam(String paramName, Integer[] separatorIndices, Map<String, ?> bindingData)
        throws TemplateEngineException {
        int tokenStart = 0;
        Object nextData = bindingData;
        for (int i = 0; i < separatorIndices.length + 1; i++) {
            if (nextData == null || !(nextData instanceof Map)) {
                throw new InvalidReferenceException("invalid scope");
            }
            String key = paramName.substring(tokenStart);
            try {
                return StringResolver.matchKey(key, (Map<String, ?>) nextData);
            }
            catch (InvalidReferenceException ignore) {
                // ignore
            }
            if (i < separatorIndices.length) {
                String token = paramName.substring(tokenStart, separatorIndices[i]);
                nextData = StringResolver.matchKey(token, (Map<String, ?>) nextData);
                tokenStart = separatorIndices[i] + 1;
            }
        }
        throw new InvalidReferenceException("mismatch binding data");
    }

    private static Object matchKey(String key, Map<String, ?> data) throws TemplateEngineException {
        Matcher m = arrayPattern.matcher(key);
        if (m.matches()) {
            key = m.group(1);
            String indexStr = m.group(2);
            if (indexStr != null) {
                int index = Integer.parseInt(indexStr);
                if (index < 0) {
                    throw new TemplateEngineException(String.format("Parameter index is negative: %s", key));
                }
                if (data.containsKey(key)) {
                    Object value = data.get(key);
                    if (value instanceof List && index < ((List) value).size()) {
                        return ((List) value).get(index);
                    }
                }
                throw new InvalidReferenceException("mismatch binding data");
            }
            throw new TemplateEngineException(String.format("Parameter index missing: %s", key));
        }
        if (data.containsKey(key)) {
            return data.get(key);
        }
        throw new InvalidReferenceException("mismatch binding data");
    }

    private static Integer[] collectSeparatorIndices(String paramName) {
        List<Integer> indices = new ArrayList<>();
        for (int i = 0; i < paramName.length(); i++) {
            char c = paramName.charAt(i);
            if (c == '\\') {
                i += 1;
            }
            else if (c == '.') {
                indices.add(i);
            }
        }
        return indices.toArray(new Integer[0]);
    }

    private String dataToString(Object value) throws TemplateEngineException {
        try {
            String valueStr;
            if (value instanceof String) {
                valueStr = (String) value;
            }
            else {
                valueStr = mapper.writeValueAsString(value);
            }
            return valueStr;
        } catch (JsonProcessingException e) {
            throw new TemplateEngineException("JSON error", e);
        }
    }
}
