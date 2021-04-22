// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.tags;

import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import com.vmware.jsonteng.ElementResolver;
import com.vmware.jsonteng.TagResolver;
import com.vmware.jsonteng.TemplateEngineException;

public class OneOfTag extends TagBase {
    static final String name = "one-of";

    private final ElementResolver elementResolver;
    private final ObjectMapper mapper = new ObjectMapper();

    public OneOfTag(TagResolver tagResolver) {
        super(tagResolver);
        elementResolver = tagResolver.getElementResolver();
    }

    @Override
    public Object process(List<?> tagTokens, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        int tokenCount = tagTokens.size();
        if (tokenCount < 1) {
            throw new TemplateEngineException(
                    String.format("Tag \"%s\" requires at least 1 parameter. Parameters given %s", name, tagTokens));
        }
        for (int i = 0; i < tokenCount; i++) {
            Object item = tagTokens.get(i);
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
                if (i == (tokenCount - 1) && !(item instanceof List)) {
                    return elementResolver.resolve(tagTokens.get(tokenCount - 1), bindingDataList);
                }
                else {
                    String itemStr = item.toString();
                    try {
                        itemStr = mapper.writeValueAsString(item);
                    } catch (JsonProcessingException ex) {}
                    throw new TemplateEngineException(
                            String.format("Tag \"%s\" contains an invalid parameter. %s.", name, itemStr));
                }
            }
        }
        return TagBase.TAG_NONE;
    }
}
