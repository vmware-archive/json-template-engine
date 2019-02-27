// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.tags;

import java.util.Collection;
import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.ElementResolver;
import com.vmware.jsonteng.TagResolver;
import com.vmware.jsonteng.TemplateEngineException;

public class LenTag extends TagBase {
    static final String name = "len";

    private final ElementResolver elementResolver;

    public LenTag(TagResolver tagResolver) {
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
        if (resolvedData != null) {
            return len(resolvedData);
        }
        else {
            return 0;
        }
    }

    private int len(Object data) {
        if (data instanceof Collection) {
            return ((Collection) data).size();
        }
        else if (data instanceof Map) {
            return ((Map) data).size();
        }
        else if (data instanceof String) {
            return ((CharSequence) data).length();
        }
        else {
            return -1;
        }
    }
}
