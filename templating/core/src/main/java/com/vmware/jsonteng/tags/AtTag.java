// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.tags;

import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.ElementResolver;
import com.vmware.jsonteng.TagResolver;
import com.vmware.jsonteng.TemplateEngineException;

public class AtTag extends TagBase {
    static final String name = "at";

    private final ElementResolver elementResolver;

    public AtTag(TagResolver tagResolver) {
        super(tagResolver);
        elementResolver = tagResolver.getElementResolver();
    }

    @Override
    public Object process(List<?> tagTokens, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        int tokenCount = tagTokens.size();
        if (tokenCount != 2) {
            throw new TemplateEngineException(
                    String.format("Tag \"%s\" requires 2 parameters. Parameters given %s", name, tagTokens));
        }
        Object data = tagTokens.get(0);
        Object key = tagTokens.get(1);
        Object resolvedData = elementResolver.resolve(data, bindingDataList);
        Object resolvedKey = elementResolver.resolve(key, bindingDataList);
        if (resolvedData instanceof List) {
            return ((List) resolvedData).get((int)resolvedKey);
        }
        else if (resolvedData instanceof Map) {
            return ((Map) resolvedData).get(resolvedKey);
        }
        else {
            return TagBase.TAG_NONE;
        }
    }
}
