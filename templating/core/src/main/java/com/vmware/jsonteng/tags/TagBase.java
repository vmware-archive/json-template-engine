// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.tags;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.TagResolver;
import com.vmware.jsonteng.TemplateEngineException;

public abstract class TagBase {
    protected static final TagNone TAG_NONE = new TagNone();

    protected final TagResolver tagResolver;

    public TagBase(TagResolver tagResolver) {
        this.tagResolver = tagResolver;
    }

    public abstract  Object process(List<?> tagTokens, List<Map<String,?>> bindingDataList)
            throws TemplateEngineException;

    protected boolean safeEval(Object expr) throws TemplateEngineException {
        try {
            String script = String.format("print(eval('%s', {'__builtins__': None}, {}))", expr);
            Process p = Runtime.getRuntime().exec("python -");
            try (BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(p.getOutputStream()))) {
                writer.write(script);
            }
            p.waitFor();
            if (p.exitValue() != 0) {
                StringBuilder errorMsg = new StringBuilder();
                BufferedReader errorReader = new BufferedReader(new InputStreamReader(p.getErrorStream()));
                String line;
                while ((line = errorReader.readLine()) != null) {
                    errorMsg.append(line);
                }
                if ("True".equalsIgnoreCase(expr.toString())) {
                    return true;
                }
                else if ("False".equalsIgnoreCase(expr.toString())) {
                    return false;
                }
                throw new TemplateEngineException(String.format("Expression %s is not valid. %s",
                                                                expr, errorMsg.toString()));
            }
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()))) {
                String result = reader.readLine();
                return "True".equals(result);
            }
        } catch (IOException | InterruptedException e) {
            throw new TemplateEngineException(String.format("Expression %s evaluation failed", expr));
        }
    }
}
