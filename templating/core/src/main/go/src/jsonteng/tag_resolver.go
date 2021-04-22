// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package jsonteng

import (
	"container/list"
	"fmt"
	"jsonteng/errors"
	intfs "jsonteng/interfaces"
	"jsonteng/tags"
	"strings"
)

type tagResolverPrivate interface {
	intfs.TagResolver
	resolve(tagData []interface{}, bindingDataList *list.List) (interface{}, error)
}

type tagResolverImpl struct {
	elementResolver intfs.ElementResolver
	templateLoader  intfs.JSONLoader
	tagMap          *map[string]intfs.TagProcessor
}

const tagMaker = '#'
const labelSeparator = ':'

func (tagResolver *tagResolverImpl) init(elementResolver intfs.ElementResolver, loader intfs.JSONLoader) {
	tagResolver.elementResolver = elementResolver
	tagResolver.templateLoader = loader
	tagResolver.tagMap = tags.BuildTagMap(tagResolver)
}

func (tagResolver *tagResolverImpl) resolve(tagData []interface{}, bindingDataList *list.List) (interface{}, error) {
	tagName := tagData[0].(string)[1:]
	labelIndex := strings.IndexByte(tagName, labelSeparator)
	if labelIndex != -1 {
		tagName = tagName[0:labelIndex]
	}
	if tag, ok := (*tagResolver.tagMap)[tagName]; ok {
		tagToken := tagData[1:]
		return tag.Process(tagToken, bindingDataList)
	}
	errl := errors.GenericError
	errl.Message = fmt.Sprintf("Unknown tag \"%v\".", tagName)
	return nil, &errl
}

func (tagResolver *tagResolverImpl) GetElementResolver() intfs.ElementResolver {
	return tagResolver.elementResolver
}

func (tagResolver *tagResolverImpl) GetLoader() intfs.JSONLoader {
	return tagResolver.templateLoader
}

func isKeyTag(key interface{}) bool {
	if k, ok := key.(string); ok && len(k) > 1 {
		return k[0] == tagMaker
	}
	return false
}

func isTag(tagData interface{}) bool {
	if t, ok := tagData.([]interface{}); ok && len(t) > 0 {
		if s, ok := t[0].(string); ok && len(s) > 1 {
			return s[0] == tagMaker
		}
	}
	return false
}
