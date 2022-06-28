// Copyright 2022 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package tags

import (
	"container/list"
	"fmt"
	"strings"
	"jsonteng/errors"
	intfs "jsonteng/interfaces"
)

type tonullTag struct {
	intfs.TagBase
	elementResolver intfs.ElementResolver
}

func (tag *tonullTag) init(tagResolver intfs.TagResolver) {
	tag.Name = "to-null"
	tag.TagResolver = tagResolver
	tag.elementResolver = tagResolver.GetElementResolver()
}

func (tag *tonullTag) Process(tagTokens []interface{}, bindingDataList *list.List) (interface{}, error) {
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
	if s, ok := resolvedData.(string); ok {
	    if strings.ToLower(s) == "null" {
	        return nil, nil
	    } else {
            errk := errors.GenericError
            errk.Message = fmt.Sprintf("Tag \"%s\" invalid string \"%v\"", tag.Name, resolvedData)
            return nil, errk
	    }
	} else {
	    errm := errors.GenericError
	    errm.Message = fmt.Sprintf("Tag \"%s\" parameter not a string type %T", tag.Name, resolvedData)
	    return nil, errm
	}
}
