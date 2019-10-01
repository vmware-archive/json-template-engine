// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package jsonteng

import (
	"container/list"
	intfs "jsonteng/interfaces"
	"os"
	"strings"
)

// TemplateEngine is a struct for creating template engine objects.
type TemplateEngine struct {
	env             interface{}
	templateLoader  intfs.JSONLoader
	verbose         bool
	stats           stats
	dupParams       *map[string][]interface{}
	elementResolver intfs.ElementResolver
}

// Init is a function for initializing a TemplateEngine object.
func (templateEngine *TemplateEngine) Init(env interface{}) {
	templateEngine.Init1(env, nil, false)
}

// Init1 is a function for initializing a TemplateEngine object.
func (templateEngine *TemplateEngine) Init1(env interface{}, loader intfs.JSONLoader, verbose bool) {
	templateEngine.env = env
	templateEngine.verbose = verbose
	if loader == nil {
		rootDir := ""
		for _, e := range os.Environ() {
			kv := strings.Split(e, "=")
			if kv[0] == "TEMPLATE_HOME" {
				rootDir = kv[1]
			}
		}
		loader = GetLoader(rootDir, verbose)
	}

	templateEngine.stats.init()
	elementResolver := elementResolverImpl{}

	stringResolver := stringResolverImpl{}
	stringResolver.init(&templateEngine.stats)
	stringResolver.setElementResolver(&elementResolver)

	tagResovler := tagResolverImpl{}
	tagResovler.init(&elementResolver, loader)

	elementResolver.init(&stringResolver, &tagResovler)

	templateEngine.elementResolver = &elementResolver
	templateEngine.templateLoader = loader
}

// Resolve is a function for resolving a JSON template.
func (templateEngine *TemplateEngine) Resolve(mainTemplate string, bindingDataList *list.List) (interface{}, error) {
	templateEngine.stats.init()
	mainTemplateJSON, err := templateEngine.templateLoader.Load(mainTemplate)
	if err != nil {
		return nil, err
	}
	effectiveBindingDataList := list.New()
	effectiveBindingDataList.PushBackList(bindingDataList)
	if templateEngine.env != nil {
		effectiveBindingDataList.PushBack(templateEngine.env)
	}
	templateEngine.dupParams = checkDuplicatedBindingData(effectiveBindingDataList)
	resolvedJSON, err := templateEngine.elementResolver.ResolveElement(mainTemplateJSON, effectiveBindingDataList)
	if err != nil {
		return nil, err
	}
	templateEngine.templateLoader.Unload(mainTemplate)
	return unescapeJSON(resolvedJSON), nil
}

// GetDupParams is a function for detecting duplicated binding data parameters.
func (templateEngine *TemplateEngine) GetDupParams() *map[string][]interface{} {
	return templateEngine.dupParams
}

// GetStats is a function for collecting the frequencies of parameter usages.
func (templateEngine *TemplateEngine) GetStats() map[string]int {
	return templateEngine.stats.getStats()
}
