// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.tags.TagBase;
import com.vmware.jsonteng.tags.TagMap;

public class TagResolver {
    private static final char TAG_MAKER = '#';
    private static final char LABEL_SEPARATOR = ':';

    private final ElementResolver elementResolver;
    private final JsonLoader templateLoader;
    private final Map<String, TagBase> tagMap;

    TagResolver(ElementResolver elementResolver, JsonLoader templateLoader) throws TemplateEngineException {
        this.elementResolver = elementResolver;
        this.templateLoader = templateLoader;
        tagMap = TagMap.getTagMap(this);
    }

    Object resolve(List<?> tagData, List<Map<String, ?>> bindingDataList) throws TemplateEngineException {
        String tagName = ((String) tagData.get(0)).substring(1);
        int labelIndex = tagName.indexOf(LABEL_SEPARATOR);
        if (labelIndex != -1) {
            tagName = tagName.substring(0, labelIndex);
        }
        if (tagMap.containsKey(tagName)) {
            TagBase tag = tagMap.get(tagName);
            List<?> tagToken = tagData.subList(1, tagData.size());
            return tag.process(tagToken, bindingDataList);
        }
        else {
            throw new TemplateEngineException(String.format("Unknown tag \"%s\".", tagName));
        }
    }

    public ElementResolver getElementResolver() {
        return this.elementResolver;
    }

    public JsonLoader getTemplateLoader() {
        return this.templateLoader;
    }

    static boolean isKeyTag(Object key) {
        return key instanceof String && ((String) key).length() > 1 && ((String) key).charAt(0) == TAG_MAKER;
    }

    static boolean isTag(Object tagData) {
        return tagData instanceof List && ((List) tagData).size() > 0 && ((List) tagData).get(0) instanceof String
               && ((String) ((List) tagData).get(0)).length() > 1
               && ((String) ((List) tagData).get(0)).charAt(0) == TAG_MAKER;
    }
}
