// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.rules;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.ElementResolver;
import com.vmware.jsonteng.JsonLoader;
import com.vmware.jsonteng.RuleResolver;
import com.vmware.jsonteng.TemplateEngineException;

public class ForEachRule extends RuleBase {
    static final String name = "for-each";

    private final ElementResolver elementResolver;
    private final JsonLoader templateLoader;

    public ForEachRule(RuleResolver ruleResolver) {
        super(ruleResolver);
        this.elementResolver = ruleResolver.getElementResolver();
        this.templateLoader = ruleResolver.getTemplateLoader();
    }

    @Override
    @SuppressWarnings("unchecked")
    public Object process(List<?> ruleTokens, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        if (ruleTokens.size() < 2 || ruleTokens.size() > 3) {
            throw new TemplateEngineException(
                    String.format("Rule \"%s\" requires 2 or 3 parameters. Parameters given %s", name, ruleTokens));
        }
        Object dataList = ruleTokens.get(0);
        Object template = ruleTokens.get(1);
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
            Object resolvedTemplate = elementResolver.resolve(templateJson, bindingDataList);
            bindingDataList.remove(0);
            bindingDataList.remove(0);
            resolvedJson.add(resolvedTemplate);
        }
        templateLoader.unload(template.toString());
        return resolvedJson;
    }
}
