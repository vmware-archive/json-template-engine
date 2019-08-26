// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.tags;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.ElementResolver;
import com.vmware.jsonteng.JsonLoader;
import com.vmware.jsonteng.TagResolver;
import com.vmware.jsonteng.TemplateEngineException;

public class ForEachTag extends TagBase {
    static final String name = "for-each";

    private final ElementResolver elementResolver;
    private final JsonLoader templateLoader;

    public ForEachTag(TagResolver tagResolver) {
        super(tagResolver);
        this.elementResolver = tagResolver.getElementResolver();
        this.templateLoader = tagResolver.getTemplateLoader();
    }

    @Override
    @SuppressWarnings("unchecked")
    public Object process(List<?> tagTokens, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        if (tagTokens.size() < 2 || tagTokens.size() > 3) {
            throw new TemplateEngineException(
                    String.format("Tag \"%s\" requires 2 or 3 parameters. Parameters given %s", name, tagTokens));
        }
        Object dataList = tagTokens.get(0);
        Object template = tagTokens.get(1);
        try {
            template = elementResolver.resolve(template, bindingDataList);
        } catch (TemplateEngineException ignore) {
        }
        Object templateJson = templateLoader.load(template.toString());
        List<?> resolvedDataList = (List) elementResolver.resolve(dataList, bindingDataList);
        List<Object> resolvedJson = new ArrayList<>();
        Map<String, Integer> indexData = new HashMap<>();
        for (int i = 0; i < resolvedDataList.size(); i++) {
            Map<String, ?> data = (Map) resolvedDataList.get(i);
            bindingDataList.add(0, data);
            indexData.put("_index_", i);
            bindingDataList.add(0, indexData);
            if (tagTokens.size() == 3) {
                Object conditionExpr = elementResolver.resolve(tagTokens.get(2), bindingDataList);
                if (!safeEval(conditionExpr)) {
                    bindingDataList.remove(0);
                    bindingDataList.remove(0);
                    continue;
                }
            }
            Object resolvedTemplate = elementResolver.resolve(templateJson, bindingDataList);
            bindingDataList.remove(0);
            bindingDataList.remove(0);
            resolvedJson.add(resolvedTemplate);
        }
        templateLoader.unload(template.toString());
        return resolvedJson;
    }
}
