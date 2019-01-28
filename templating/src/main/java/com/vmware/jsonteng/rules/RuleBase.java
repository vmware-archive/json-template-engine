// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng.rules;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.util.List;
import java.util.Map;

import com.vmware.jsonteng.RuleResolver;
import com.vmware.jsonteng.TemplateEngineException;

public abstract class RuleBase {
    protected static final RuleNone RULE_NONE = new RuleNone();

    protected final RuleResolver ruleResolver;

    public RuleBase(RuleResolver ruleResolver) {
        this.ruleResolver = ruleResolver;
    }

    public abstract  Object process(List<?> ruleTokens, List<Map<String,?>> bindingDataList)
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
