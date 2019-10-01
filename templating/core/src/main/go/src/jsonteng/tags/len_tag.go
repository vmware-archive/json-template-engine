// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package tags

import (
	"container/list"
	"fmt"
	"jsonteng/errors"
	intfs "jsonteng/interfaces"
)

type lenTag struct {
	intfs.TagBase
	elementResolver intfs.ElementResolver
}

func (tag *lenTag) init(tagResolver intfs.TagResolver) {
	tag.Name = "len"
	tag.TagResolver = tagResolver
	tag.elementResolver = tagResolver.GetElementResolver()
}

func (tag *lenTag) Process(tagTokens []interface{}, bindingDataList *list.List) (interface{}, error) {
	tokenCount := len(tagTokens)
	if tokenCount != 1 {
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Tag \"%s\" requires 1 parameter. Parameters given %v", tag.Name, tagTokens)
		return nil, &errl
	}
	data := tagTokens[0]
	resolvedData, err := tag.elementResolver.ResolveElement(data, bindingDataList)
	if err != nil {
		return nil, err
	}
	return length(resolvedData), nil
}

func length(data interface{}) int {
	switch d := data.(type) {
	case map[string]interface{}:
		return len(d)
	case []interface{}:
		return len(d)
	default:
		return -1
	}
}
