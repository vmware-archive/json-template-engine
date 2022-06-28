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

type toboolTag struct {
	intfs.TagBase
	elementResolver intfs.ElementResolver
}

func (tag *toboolTag) init(tagResolver intfs.TagResolver) {
	tag.Name = "to-bool"
	tag.TagResolver = tagResolver
	tag.elementResolver = tagResolver.GetElementResolver()
}

func (tag *toboolTag) Process(tagTokens []interface{}, bindingDataList *list.List) (interface{}, error) {
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
	    value := strings.ToLower(s)
	    if value == "true" {
	        return true, nil
	    } else if value == "false" {
	    	return false, nil
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
