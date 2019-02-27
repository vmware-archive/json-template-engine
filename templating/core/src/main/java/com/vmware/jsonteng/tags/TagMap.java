// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.tags;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.Map;

import com.vmware.jsonteng.TagResolver;
import com.vmware.jsonteng.TemplateEngineException;

public class TagMap {
    private static final Map<String, Class<?>> tagClassMap;

    static {
        tagClassMap = new Hashtable<>();

        tagClassMap.put(AtTag.name, AtTag.class);
        tagClassMap.put(ExistsTag.name, ExistsTag.class);
        tagClassMap.put(ForEachTag.name, ForEachTag.class);
        tagClassMap.put(LenTag.name, LenTag.class);
        tagClassMap.put(OneOfTag.name, OneOfTag.class);
    }

    @SuppressWarnings("unchecked")
    public static Map<String, TagBase> getTagMap(TagResolver tagResolver) throws TemplateEngineException {
        Map<String, TagBase> tagMap = new HashMap<>();
        for (Map.Entry<String, Class<?>> entry : tagClassMap.entrySet()) {
            try {
                Constructor<TagBase> ctor = (Constructor<TagBase>) entry.getValue().getConstructor(
                        TagResolver.class);
                TagBase object = ctor.newInstance(tagResolver);
                tagMap.put(entry.getKey(), object);
            } catch (NoSuchMethodException | InstantiationException |
                    IllegalAccessException | InvocationTargetException e) {
                throw new TemplateEngineException("Failed to add tag " + entry.getKey(), e);
            }
        }
        return tagMap;
    }

    public static void addTag(String tagName, Class<?> tag) {
        tagClassMap.put(tagName, tag);
    }

    public static String[] getTagNames() {
        return tagClassMap.keySet().toArray(new String[0]);
    }
}
