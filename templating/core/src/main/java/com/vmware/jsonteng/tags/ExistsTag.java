// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.tags;

import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.ElementResolver;
import com.vmware.jsonteng.TagResolver;
import com.vmware.jsonteng.TemplateEngineException;
import com.vmware.jsonteng.UnresolvableParameterException;

public class ExistsTag extends TagBase {
    static final String name = "exists";

    private final ElementResolver elementResolver;

    public ExistsTag(TagResolver tagResolver) {
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
        try {
            elementResolver.resolve(data, bindingDataList);
        }
        catch (UnresolvableParameterException e) {
            return "1==0";
        }
        return "1==1";
    }
}
