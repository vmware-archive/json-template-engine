// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package tags

import (
	"container/list"
	"fmt"
	"jsonteng/errors"
	intfs "jsonteng/interfaces"
)

type foreachTag struct {
	intfs.TagBase
	elementResolver intfs.ElementResolver
	templateLoader  intfs.JSONLoader
}

func (tag *foreachTag) init(tagResolver intfs.TagResolver) {
	tag.Name = "for-each"
	tag.TagResolver = tagResolver
	tag.elementResolver = tagResolver.GetElementResolver()
	tag.templateLoader = tagResolver.GetLoader()
}

func (tag *foreachTag) Process(tagTokens []interface{}, bindingDataList *list.List) (interface{}, error) {
	tokenCount := len(tagTokens)
	if tokenCount < 2 || tokenCount > 3 {
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Tag \"%s\" requires 2 or 3 parameters. Parameters given %v", tag.Name, tagTokens)
		return nil, &errl
	}
	dataList := tagTokens[0]
	template := tagTokens[1]
	resolved, errl := tag.elementResolver.ResolveElement(template, bindingDataList)
	if errl == nil {
		template = resolved
	}
	templateString := fmt.Sprintf("%v", template)
	templateJSON, errl := tag.templateLoader.Load(templateString)
	if errl != nil {
		return nil, errl
	}
	resolvedData, errl := tag.elementResolver.ResolveElement(dataList, bindingDataList)
	if errl != nil {
		return nil, errl
	}
	resolvedDataList, ok := resolvedData.([]interface{})
	if !ok {
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Requires a list, given %v", resolvedDataList)
		return nil, &errl
	}
	resolvedJSON := make([]interface{}, len(resolvedDataList))
	indexData := make(map[string]interface{})
	count := 0
	for i, data := range resolvedDataList {
		bindingDataList.PushFront(data)
		indexData["_index_"] = i
		bindingDataList.PushFront(indexData)
		if tokenCount == 3 {
			conditionExpr, errl := tag.elementResolver.ResolveElement(tagTokens[2], bindingDataList)
			if errl != nil {
				return nil, errl
			}
			if result, err := safeEval(conditionExpr); err == nil {
				if !result {
					bindingDataList.Remove(bindingDataList.Front())
					bindingDataList.Remove(bindingDataList.Front())
					continue
				}
			} else {
				return nil, err
			}
		}
		resolvedTemplate, errl := tag.elementResolver.ResolveElement(templateJSON, bindingDataList)
		if errl != nil {
			return nil, errl
		}
		bindingDataList.Remove(bindingDataList.Front())
		bindingDataList.Remove(bindingDataList.Front())
		resolvedJSON[count] = resolvedTemplate
		count++
	}
	tag.templateLoader.Unload(templateString)
	return resolvedJSON[:count], nil
}
