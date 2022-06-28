// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.tags;

import com.vmware.jsonteng.ElementResolver;
import com.vmware.jsonteng.TagResolver;
import com.vmware.jsonteng.TemplateEngineException;

import java.util.List;
import java.util.Map;

public class ToBoolTag extends TagBase {
    static final String name = "to-bool";

    private final ElementResolver elementResolver;

    public ToBoolTag(TagResolver tagResolver) {
        super(tagResolver);
        elementResolver = tagResolver.getElementResolver();
    }

    @Override
    public Object process(List<?> tagTokens, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        int tokenCount = tagTokens.size();
        if (tokenCount != 1) {
            throw new TemplateEngineException(
                    String.format("Tag \"%s\" requires 1 parameter. Parameters given %s", name, tagTokens));
        }
        Object data = tagTokens.get(0);
        Object resolvedData = elementResolver.resolve(data, bindingDataList);
        if (resolvedData instanceof String) {
            if ("true".equals(resolvedData.toString().toLowerCase())) {
                return true;
            } else if ("false".equals(resolvedData.toString().toLowerCase())) {
                return false;
            } else {
                throw new TemplateEngineException(
                        String.format("Tag \"%s\" invalid string \"%s\"", name, resolvedData.toString()));
            }
        } else {
            throw new TemplateEngineException(
                    String.format("Tag \"%s\" parameter not a string type %s", name, resolvedData.getClass().toString()));
        }
    }
}
