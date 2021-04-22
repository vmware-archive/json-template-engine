// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import com.vmware.jsonteng.tags.TagNone;

public class ElementResolver {
    private final StringResolver stringResolver;
    private final TagResolver tagResolver;
    private final ObjectMapper mapper = new ObjectMapper();


    ElementResolver(JsonLoader templateLoader, Stats stats) throws TemplateEngineException {
        stringResolver = new StringResolver(this, stats);
        tagResolver = new TagResolver(this, templateLoader);
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
                if (TagResolver.isKeyTag(key)) {
                    if (!(value instanceof List)) {
                        throw new TemplateEngineException(
                                String.format("Value must be a list if name is a tag: \"%s\". Found \"%s\".", key, value));
                    }
                    List<Object> tagTemp = new ArrayList<>();
                    tagTemp.add(key);
                    tagTemp.addAll((List) value);
                    Object resolvedTuple = resolve(tagTemp, bindingDataList);
                    if (resolvedTuple instanceof Map) {
                        newElement.putAll((Map) resolvedTuple);
                    }
                    else if (!(resolvedTuple instanceof TagNone)) {
                        String keyStr = key.toString();
                        String valueStr = value.toString();
                        String resolvedTupleStr = resolvedTuple.toString();
                        try {
                            keyStr = mapper.writeValueAsString(key);
                            valueStr = mapper.writeValueAsString(value);
                            resolvedTupleStr = mapper.writeValueAsString(resolvedTuple);
                        } catch (JsonProcessingException ex) {}
                        throw new TemplateEngineException(
                                String.format("Invalid tag result format for JSON object name tag: %s %s => %s.",
                                              keyStr, valueStr, resolvedTupleStr));
                    }
                }
                else {
                    Object newKey = resolve(key, bindingDataList);
                    Object newValue = resolve(value, bindingDataList);
                    if (newKey instanceof String && !(newValue instanceof TagNone)) {
                        newElement.put(newKey, newValue);
                    }
                }
            }
            return newElement;
        }
        else if (element instanceof List) {
            if (TagResolver.isTag(element)) {
                return tagResolver.resolve((List) element, bindingDataList);
            }
            List<Object> newElement = new ArrayList<>();
            for (Object item : (List) element) {
                Object newItem = resolve(item, bindingDataList);
                if (!(newItem instanceof TagNone)) {
                    newElement.add(newItem);
                }
            }
            return newElement;
        }
        throw new TemplateEngineException(
                String.format("Unknown data type %s of %s", element.getClass().getCanonicalName(), element));
    }
}
