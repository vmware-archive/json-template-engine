// Copyright 2021 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

import org.junit.Test;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.assertThrows;


public class TemplateEngineTests {
    private String runTest(String[] inputParams) {
        PrintStream stdout = System.out;
        ByteArrayOutputStream stringOut = new ByteArrayOutputStream();
        System.setOut(new PrintStream(stringOut));
        TemplateEngine.main(inputParams);
        System.out.flush();
        System.setOut(stdout);
        return stringOut.toString();
    }

    @Test
    public void testResolveDict() {
        String jsonStr = runTest(new String[] {"-r", "-b", "{\"x\": 1}", "{\"y\": \"abc\\\\defx$\\$${x}\"}"});
        assertEquals("testResolveDict","\"{\\\"y\\\": \\\"abc\\\\defx$$1\\\"}\"\n", jsonStr);
    }

    @Test
    public void testResolveListValue() {
        String jsonStr = runTest(new String[] {"-r", "-b", "{\"x\": [1, 2]}", "{\"y\": \"${x[1]}\"}"});
        assertEquals("testResolveListValue", "{\"y\":2}\n", jsonStr);
    }

    @Test
    public void testMisformedParam() {
        assertThrows("testMisformedParam", TemplateEngineException.class,
                () -> TemplateEngine.main(new String[] {"-r", "-b",
                "{\"x\": [1, 2]}", "{\"y\": \"${x[1]\"}"}));
    }

    @Test
    public void testMissingParam() {
        assertThrows("testMissingParam", TemplateEngineException.class,
                () -> TemplateEngine.main(new String[] {"-r", "-b",
                "{\"x\": [1, 2]}", "{\"y\": \"${x1}\"}"}));
    }

    @Test
    public void testResolveEmptyParam() {
        assertThrows("testResolveEmptyParam", TemplateEngineException.class,
                () -> TemplateEngine.main(new String[] {"-r", "-b",
                "{\"x\": [1, 2]}", "{\"y\": \"${}\"}"}));
    }

    @Test
    public void testResolveTooManyParam() {
        assertThrows("testMissingParam", TemplateEngineException.class,
                () -> TemplateEngine.main(new String[] {"-r", "-b",
                "{\"x\": [1, 2]}", "{\"y\": \"${x.x1}\"}"}));
    }

    @Test
    public void testResolveBoolValue() {
        String jsonStr = runTest(new String[] {"-r", "-b", "{\"x\": true}", "{\"y\": \"${x}\"}"});
        assertEquals("testResolveBoolValue", "{\"y\":true}\n", jsonStr);
    }

    @Test
    public void testCli() {
        String jsonStr = runTest(new String[] {"-v", "-s", "-d", "-r", "-b", "{\"x\": 1}", "{\"y\": \"${x}\"}"});
        assertEquals("testCli", 126, jsonStr.length());
    }

    @Test
    public void testDuplicateParam() {
        String jsonStr = runTest(new String[] {"-v", "-r", "-b", "{\"x\": 1};{\"x\": 2}", "{\"y\": \"${x}\"}"});
        assertNotEquals("testDuplicateParam", -1, jsonStr.indexOf("duplicate"));
    }

    @Test
    public void testKeyRule() {
        String template = "{\"#one-of\":[[\"1==2\",\"false\"],[\"2==2\", {\"a\":\"lower\"}]]}";
        String jsonStr = runTest(new String[] {"-r", "-b", "{\"list\":[{\"z\":\"100\"},{\"z\":\"200\"}]}", template});
        assertEquals("testKeyRule", "{\"a\":\"lower\"}\n", jsonStr);
    }

    @Test
    public void testKeyRuleInvalid() {
        String template = "{\"#one-of\":\"lower\"}";
        assertThrows("testKeyRuleInvalid", TemplateEngineException.class,
                () -> TemplateEngine.main(new String[]
                        {"-r", "-b", "{\"list\":[{\"z\":\"100\"}, {\"z\":\"200\"}]}", template}));
    }

    @Test
    public void testKeyRuleInvalidResult() {
        String template = "{\"#one-of\":[[\"1==2\",\"false\"],[\"2==2\", \"lower\"]]}";
        assertThrows("testKeyRuleInvalid", TemplateEngineException.class,
                () -> TemplateEngine.main(new String[] {"-r", "-b",
                "{\"list\":[{\"z\":\"100\"},{\"z\":\"20\"}]}",
                template}));
    }

    @Test
    public void testUnknownRule() {
        String template = "{\"x\":[\"#xxyyzz\",\"${list}\",\"{\\\"y\\\":\\\"${z}\\\"}\"]}";
        assertThrows("testUnknownRule", TemplateEngineException.class,
                () -> TemplateEngine.main(new String[]
                        {"-r", "-b", "{\"list\":[{\"z\":\"100\"}, {\"z\":\"200\"}]}", template}));
    }

    @Test
    public void testForeach() {
        String template = "{\"x\":[\"#for-each\",\"${list}\",\"{\\\"y\\\":\\\"${z}\\\"}\"]}";
        String jsonStr = runTest(new String[] {"-r", "-b", "{\"list\":[{\"z\":\"100\"},{\"z\":\"200\"}]}", template});
        assertEquals("testForeach", "{\"x\":[{\"y\":\"100\"},{\"y\":\"200\"}]}\n", jsonStr);
    }

    @Test
    public void testOneof() {
        String template = "{\"x\": [\"#one-of\",[\"1 == 2\",\"false\"], [\"2==2\",\"true\"]]}";
        String jsonStr = runTest(new String[] {"-r", "-b", "{\"list\":[{\"z\":\"100\"},{\"z\":\"200\"}]}", template});
        assertEquals("testOneof", "{\"x\":\"true\"}\n", jsonStr);
    }

    @Test
    public void testOneofDefault() {
        String template = "{\"x\": [\"#one-of\",[\"1 == 2\",\"false\"], \"default\"]}";
        String jsonStr = runTest(new String[] {"-r", "-b", "{\"list\":[{\"z\":\"100\"},{\"z\":\"200\"}]}", template});
        assertEquals("testOneofDefault", "{\"x\":\"default\"}\n", jsonStr);
    }

    @Test
    public void testOneofInvalidType() {
        String template = "{\"x\": [\"#one-of\",[\"1 == 2\",\"false\"], [\"invalid default\"]]}";
        assertThrows("testOneofInvalidType", TemplateEngineException.class,
                () -> TemplateEngine.main(new String[] {"-r", "-b",
                "{\"list\":[{\"z\":\"100\"},{\"z\":\"20\"}]}",
                template}));
    }

}
