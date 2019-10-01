// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package main

import (
	"container/list"
	"encoding/json"
	"flag"
	"fmt"
	"jsonteng"
	"strings"
	"time"
)

type cliParams struct {
	bindingDataResources string
	env                  string
	verbose              bool
	stats                bool
	debug                bool
	raw                  bool
}

func (params *cliParams) init() {
	flag.StringVar(&params.bindingDataResources, "binding-data-resources", "",
		"a semi-colon separated list of binding data")
	flag.StringVar(&params.bindingDataResources, "b", "",
		"a semi-colon separated list of binding data (shorthand)")
	flag.StringVar(&params.env, "env", "",
		"global binding data")
	flag.StringVar(&params.env, "e", "",
		"global binding data (shorthand)")
	flag.BoolVar(&params.verbose, "verbose", false,
		"increase output verbosity")
	flag.BoolVar(&params.verbose, "v", false,
		"increase output verbosity (shorthand)")
	flag.BoolVar(&params.stats, "stats", false,
		"show stats")
	flag.BoolVar(&params.verbose, "s", false,
		"show stats (shorthand)")
	flag.BoolVar(&params.debug, "debug", false,
		"show debug info")
	flag.BoolVar(&params.debug, "d", false,
		"show debug info (shorthand)")
	flag.BoolVar(&params.raw, "raw", false,
		"unformatted output")
	flag.BoolVar(&params.raw, "r", false,
		"unformatted output (shorthand)")
}

func main() {
	cliParams := cliParams{}
	cliParams.init()
	flag.Parse()
	if cliParams.bindingDataResources == "" {
		fmt.Println("Must provide a binding data list.")
		return
	}
	loader := jsonteng.GetLoader("", cliParams.verbose)
	bindingDataList := list.New()
	for _, fileName := range strings.Split(cliParams.bindingDataResources, ";") {
		bindingData, err := loader.Load(fileName)
		loader.Unload(fileName)
		if err != nil {
			fmt.Printf("Failed to load %v\n", fileName)
			return
		}
		bindingDataList.PushBack(bindingData)
	}
	var envBinding interface{}
	if cliParams.env != "" {
		eb, err := loader.Load(cliParams.env)
		if err != nil {
			fmt.Printf("Malformed env parameter %v\n", cliParams.env)
		}
		envBinding = eb
		loader.Unload(cliParams.env)
	}
	if flag.NArg() != 1 {
		fmt.Println("One arg only")
		return
	}
	mainTemplate := flag.Arg(0)
	if cliParams.debug {
		fmt.Printf("env data: %v\n", envBinding)
		fmt.Printf("binding data: %v\n", bindingDataList)
		fmt.Printf("main template: %v\n", mainTemplate)
	}

	engine := jsonteng.TemplateEngine{}
	engine.Init(envBinding)

	startTime := time.Now()
	resolvedJson, err := engine.Resolve(mainTemplate, bindingDataList)
	if err != nil {
		fmt.Printf("Failed to resolve the JSON template %s due to %v\n", mainTemplate, err)
	}
	endTime := time.Now()
	if cliParams.verbose {
		for k, _ := range *engine.GetDupParams() {
			fmt.Printf("Warning: Parameter %s has duplicated values\n", k)
		}
		delta := endTime.Sub(startTime)
		fmt.Printf("Resolved JSON in %v ms\n", delta.Nanoseconds()/1000000)
	}
	if cliParams.raw {
		if msgJson, err := json.Marshal(resolvedJson); err == nil {
			fmt.Println(string(msgJson))
		} else {
			fmt.Println("Failed to print resolved JSON. %v", err)
		}
	} else {
		if msgJson, err := json.MarshalIndent(resolvedJson, "", "  "); err == nil {
			fmt.Println(string(msgJson))
		} else {
			fmt.Println("Failed to print resolved JSON. %v", err)
		}
	}
	if cliParams.stats {
		fmt.Println("Parameter usage")
		fmt.Println(json.MarshalIndent(engine.GetStats(), "", "  "))
	}
}
