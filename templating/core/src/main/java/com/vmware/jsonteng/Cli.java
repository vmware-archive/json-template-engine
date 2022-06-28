// Copyright 2022 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import org.apache.commons.cli.*;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Map;

public class Cli {
    @SuppressWarnings("unchecked")
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
            try {
                bindingData = (Map<String, ?>) loader.load(fileName);
                loader.unload(fileName);
            } catch (TemplateEngineException e) {
                System.out.println(e.getMessage());
                System.exit(1);
            }
            bindingDataList.add(bindingData);
        }
        Map<String, ?> envBinding = null;
        try {
            if (cmd.hasOption("env")) {
                String envString = cmd.getOptionValue("env");
                envBinding = (Map<String, ?>) loader.load(envString);
                loader.unload(envString);
            }
        } catch (TemplateEngineException e) {
            e.printStackTrace();
        }

        List<String> args = cmd.getArgList();
        if (args.size() != 1) {
            System.out.println("One arg only");
            System.exit(1);
        }
        String mainTemplate = args.get(0);

        if (cmd.hasOption("debug")) {
            System.out.printf("env data: %s%n", envBinding);
            System.out.printf("binding data: %s%n", bindingDataList);
            System.out.printf("main template: %s%n", mainTemplate);
        }

        if (cmd.hasOption("tags")) {
            String[] tags = cmd.getOptionValue("tags").split(",");
            try {
                TemplateEngine.addTags(tags);
            } catch (TemplateEngineException e) {
                e.printStackTrace();
                System.exit(1);
            }
        }

        TemplateEngine engine = null;
        try {
            engine = new TemplateEngine(envBinding);
        } catch (TemplateEngineException e) {
            e.printStackTrace();
            System.exit(1);
        }
        long startTime = new Date().getTime();
        Object resolvedJson = null;
        try {
            resolvedJson = engine.resolve(mainTemplate, bindingDataList);
        } catch (TemplateEngineException e) {
            System.out.println(e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
        long endTime = new Date().getTime();
        if (cmd.hasOption("verbose")) {
            for (String dupParam: engine.getDupParams().keySet()) {
                System.out.printf("Warning: Parameter %s has duplicated values%n", dupParam);
            }
            long delta = endTime - startTime;
            System.out.printf("Resolved JSON in %d ms%n", delta);
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
