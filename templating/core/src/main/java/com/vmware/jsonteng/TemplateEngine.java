// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

import com.vmware.jsonteng.tags.TagMap;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TemplateEngine {

    private final Map<String, ?> env;
    private final JsonLoader templateLoader;
    private final ElementResolver elementResolver;
    private Map<String, List<Object>> dupParams;
    private final Stats stats;

    public TemplateEngine() throws TemplateEngineException {
        this(null);
    }

    public TemplateEngine(Map<String, ?> env) throws TemplateEngineException {
        this(env, null, false);
    }

    public TemplateEngine(Map<String, ?> env, JsonLoader templateLoader, boolean verbose)
            throws TemplateEngineException {
        this.env = env;
        if (templateLoader != null) {
            this.templateLoader = templateLoader;
        }
        else {
            this.templateLoader = new DefaultJsonLoader(System.getenv("TEMPLATE_HOME"), verbose);
        }
        dupParams = new HashMap<>();
        stats = new Stats();
        this.elementResolver = new ElementResolver(this.templateLoader, stats);
    }

    public Object resolve(String mainTemplate, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        stats.clear();
        Object mainTemplateJson = templateLoader.load(mainTemplate);
        List<Map<String, ?>> effectiveBindingDataList = new ArrayList<>(bindingDataList);
        if (env != null) {
            effectiveBindingDataList.add(env);
        }
        this.dupParams = Utils.checkDuplicatedBindingData(effectiveBindingDataList);
        Object resolvedJson = elementResolver.resolve(mainTemplateJson, effectiveBindingDataList);
        templateLoader.unload(mainTemplate);
        return Utils.unescapeJson(resolvedJson);
    }

    public Map<String, List<Object>> getDupParams() {
        return dupParams;
    }

    public Map<String, Integer> getStats() {
        return stats.getStats();
    }

    public static void addTags(String[] tags) throws TemplateEngineException {
        for (String tag : tags) {
            try {
                Class<?> clazz = Class.forName(tag);
                Field nameField = clazz.getField("name");
                TagMap.addTag((String) nameField.get(null), clazz);
            } catch (ClassNotFoundException | NoSuchFieldException | IllegalAccessException e) {
                throw new TemplateEngineException("Unable to add tags", e);
            }
        }
    }

    public static String[] listTagNames() {
        return TagMap.getTagNames();
    }
}
