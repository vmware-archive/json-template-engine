// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package tags

import (
	"container/list"
	"fmt"
	"jsonteng/errors"
	intfs "jsonteng/interfaces"
)

type atTag struct {
	intfs.TagBase
	elementResolver intfs.ElementResolver
}

func (tag *atTag) init(tagResolver intfs.TagResolver) {
	tag.Name = "at"
	tag.TagResolver = tagResolver
	tag.elementResolver = tagResolver.GetElementResolver()
}

func (tag *atTag) Process(tagTokens []interface{}, bindingDataList *list.List) (interface{}, error) {
	tokenCount := len(tagTokens)
	if tokenCount != 2 {
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Tag \"%s\" requires 2 parameters. Parameters given %v", tag.Name, tagTokens)
		return nil, &errl
	}
	data := tagTokens[0]
	key := tagTokens[1]
	resolvedData, errl := tag.elementResolver.ResolveElement(data, bindingDataList)
	if errl != nil {
		return nil, errl
	}
	resolvedKey, errl := tag.elementResolver.ResolveElement(key, bindingDataList)
	if errl != nil {
		return nil, errl
	}
	if resolvedList, ok := resolvedData.([]interface{}); ok {
		return resolvedList[int(resolvedKey.(float64))], nil
	} else if resolvedMap, ok := resolvedData.(map[string]interface{}); ok {
		return resolvedMap[resolvedKey.(string)], nil
	} else {
		return intfs.TagNone{}, nil
	}
}
