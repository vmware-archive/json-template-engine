// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.vmware.jsonteng.tags.TagMap;

public class TemplateEngine {

    private final Map<String, ?> env;
    private final JsonLoader templateLoader;
    private final ElementResolver elementResolver;
    private Map<String, List> dupParams;
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

    public Map<String, List> getDupParams() {
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

    private static void cli(String[] argv) {
        Options options = new Options();
        options.addOption(Option.builder("b").longOpt("binding-data-resources").hasArgs().numberOfArgs(1)
                                  .required().desc("a semi-colon separated list of binding data").build())
                .addOption(Option.builder("e").longOpt("env").hasArg().numberOfArgs(1).required(false).
                        desc("global binding data").build())
                .addOption(Option.builder("v").longOpt("verbose").required(false).
                        desc("increase output verbosity").build())
                .addOption(Option.builder("s").longOpt("stats").required(false).desc("show stats").build())
                .addOption(Option.builder("d").longOpt("debug").required(false).
                        desc("show debug info").build())
                .addOption(Option.builder("r").longOpt("raw").required(false)
                                   .desc("unformatted output").build())
                .addOption(Option.builder("t").longOpt("tags").required(false).hasArg().numberOfArgs(1)
                                   .desc("common separated tag list").build());
        CommandLineParser parser = new DefaultParser();
        HelpFormatter formatter = new HelpFormatter();
        CommandLine cmd = null;

        try {
            cmd = parser.parse(options, argv);
        } catch (ParseException e) {
            System.out.println(e.getMessage());
            formatter.printHelp("jsonteng", options);

            System.exit(1);
        }
        String bindingFileList = cmd.getOptionValue("binding-data-resources");
        List<Map<String, ?>> bindingDataList = new ArrayList<>();
        JsonLoader loader = new DefaultJsonLoader(null, cmd.hasOption("verbose"));
        for (String fileName : bindingFileList.split(";")) {
            Map<String, ?> bindingData = null;
            bindingData = (Map<String, ?>) loader.load(fileName);
            loader.unload(fileName);
            bindingDataList.add(bindingData);
        }
        Map<String, ?> envBinding = null;
        if (cmd.hasOption("env")) {
            String envString = cmd.getOptionValue("env");
            envBinding = (Map<String, ?>) loader.load(envString);
            loader.unload(envString);
        }

        List<String> args = cmd.getArgList();
        if (args.size() != 1) {
            System.out.println("One arg only");
            System.exit(1);
        }
        String mainTemplate = args.get(0);

        if (cmd.hasOption("debug")) {
            System.out.println(String.format("env data: %s", envBinding));
            System.out.println(String.format("binding data: %s", bindingDataList));
            System.out.println(String.format("main template: %s", mainTemplate));
        }

        if (cmd.hasOption("tags")) {
            String[] tags = cmd.getOptionValue("tags").split(",");
            TemplateEngine.addTags(tags);
        }

        TemplateEngine engine = null;
        engine = new TemplateEngine(envBinding);
        long startTime = new Date().getTime();
        Object resolvedJson = null;
        resolvedJson = engine.resolve(mainTemplate, bindingDataList);
        long endTime = new Date().getTime();
        if (cmd.hasOption("verbose")) {
            for (String dupParam: engine.getDupParams().keySet()) {
                System.out.println(String.format("Warning: Parameter %s has duplicated values", dupParam));
            }
            long delta = endTime - startTime;
            System.out.println(String.format("Resolved JSON in %d ms", delta));
        }
        ObjectMapper mapper = new ObjectMapper();
        if (!cmd.hasOption("raw")) {
            mapper.enable(SerializationFeature.INDENT_OUTPUT);
        }
        try {
            System.out.println(mapper.writeValueAsString(resolvedJson));
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        }
        if (cmd.hasOption("stats")) {
            System.out.println("Parameter usage");
            Map<String, Integer> stats = engine.getStats();
            mapper.enable(SerializationFeature.INDENT_OUTPUT);
            try {
                System.out.println(mapper.writeValueAsString(stats));
            } catch (JsonProcessingException e) {
                e.printStackTrace();
            }
        }
    }

    public static void main(String[] argv) {
        cli(argv);
    }
}
