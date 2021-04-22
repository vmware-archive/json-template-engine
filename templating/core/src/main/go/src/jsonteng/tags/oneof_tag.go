// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package tags

import (
	"container/list"
	"encoding/json"
	"fmt"
	"jsonteng/errors"
	intfs "jsonteng/interfaces"
)

type oneofTag struct {
	intfs.TagBase
	elementResolver intfs.ElementResolver
}

func (tag *oneofTag) init(tagResolver intfs.TagResolver) {
	tag.Name = "one-of"
	tag.TagResolver = tagResolver
	tag.elementResolver = tagResolver.GetElementResolver()
}

func (tag *oneofTag) Process(tagTokens []interface{}, bindingDataList *list.List) (interface{}, error) {
	tokenCount := len(tagTokens)
	if tokenCount < 1 {
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Tag \"%s\" requires at least 1 parameter. Parameters given %v", tag.Name, tagTokens)
		return nil, &errl
	}
	for i, it := range tagTokens {
		if item, ok := it.([]interface{}); ok && len(item) == 2 {
			condition := item[0]
			value := item[1]
			conditionExpr, err := tag.elementResolver.ResolveElement(condition, bindingDataList)
			if err != nil {
				return nil, err
			}
			if result, err := safeEval(conditionExpr); err == nil {
				if result {
					return tag.elementResolver.ResolveElement(value, bindingDataList)
				}
			} else {
				return nil, err
			}
		} else {
			if i == (tokenCount - 1) {
				if _, ok := it.([]interface{}); !ok {
					return tag.elementResolver.ResolveElement(it, bindingDataList)
				}
			}
			errl := errors.GenericError
			itemStr, _ := json.Marshal(item)
			errl.Message = fmt.Sprintf("Tag \"%s\" contains an invalid parameter. %s.", tag.Name, string(itemStr))
			return nil, &errl
		}
	}
	return intfs.TagNone{}, nil
}
