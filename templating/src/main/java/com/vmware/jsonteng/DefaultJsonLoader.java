// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

import java.io.IOException;
import java.net.URL;
import java.util.Map;
import java.util.Stack;

import com.fasterxml.jackson.databind.ObjectMapper;

public class DefaultJsonLoader implements JsonLoader {
    private final Stack<DirData> dirStack;
    private final ObjectMapper objectMapper;

    DefaultJsonLoader(String rootPath) {
        this.dirStack = new Stack<>();
        this.objectMapper = new ObjectMapper();
        if (rootPath == null) {
            rootPath = "";
        }
        dirStack.push(new DirData("root", rootPath));
    }

    @Override
    public Object load(String jsonResource) throws TemplateEngineException {
        final DirData parent = dirStack.peek();
        String effectiveURL = parent.effectiveURL + jsonResource;
        if (!effectiveURL.contains("://")) {
            effectiveURL = "file://" + effectiveURL;
        }
        Object jsonObject;
        try {
            final URL url = new URL(effectiveURL);
            jsonObject = objectMapper.readValue(url, Map.class);
            int lastDirIndex = effectiveURL.lastIndexOf('/');
            dirStack.push(new DirData(jsonResource, effectiveURL.substring(0, lastDirIndex+1)));
        } catch (IOException e) {
            try {
                jsonObject = objectMapper.readValue((String) jsonResource, Map.class);
            } catch (IOException e1) {
                throw new TemplateEngineException(String.format("Invalid template %s", jsonResource));
            }
            dirStack.push(new DirData(jsonResource, null));
        }
        return jsonObject;
    }

    @Override
    public void unload(String jsonResource) throws TemplateEngineException {
        final DirData dirData = dirStack.pop();
        if (dirData.jsonResource != jsonResource) {
            throw new TemplateEngineException("JSON resource loading is out of order.");
        }
    }

    private class DirData {
        private Object jsonResource;
        private String effectiveURL;

        DirData(Object jsonResource, String effectiveURL) {
            this.jsonResource = jsonResource;
            this.effectiveURL = effectiveURL;
        }
    }
}
