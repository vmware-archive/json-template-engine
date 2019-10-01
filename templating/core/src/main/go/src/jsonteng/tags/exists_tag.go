// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package tags

import (
	"container/list"
	"fmt"
	"jsonteng/errors"
	intfs "jsonteng/interfaces"
)

type existsTag struct {
	intfs.TagBase
	elementResolver intfs.ElementResolver
}

func (tag *existsTag) init(tagResolver intfs.TagResolver) {
	tag.Name = "exists"
	tag.TagResolver = tagResolver
	tag.elementResolver = tagResolver.GetElementResolver()
}

func (tag *existsTag) Process(tagTokens []interface{}, bindingDataList *list.List) (interface{}, error) {
	tokenCount := len(tagTokens)
	if tokenCount != 1 {
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Tag \"%s\" requires 1 parameter. Parameters given %v", tag.Name, tagTokens)
		return nil, &errl
	}
	data := tagTokens[0]
	_, err := tag.elementResolver.ResolveElement(data, bindingDataList)
	if err != nil {
		if terr, ok := err.(*errors.TemplateEngineError); ok {
			if terr.ErrorCode == errors.UNRESOLVABLE_PARAMETER {
				return false, nil
			}
		}
		return nil, err
	}
	return true, nil
}
