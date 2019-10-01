// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package jsonteng

import (
	"container/list"
	"fmt"
	"jsonteng/errors"
	intfs "jsonteng/interfaces"
	"reflect"
)

type elementResolverImpl struct {
	stringResolver stringResolver
	tagResolver    tagResolverPrivate
}

func (elementResolver *elementResolverImpl) init(stringResolver stringResolver, tagResolver tagResolverPrivate) {
	elementResolver.stringResolver = stringResolver
	elementResolver.tagResolver = tagResolver
}

func (elementResolver *elementResolverImpl) ResolveElement(elementAny interface{}, bindingDataList *list.List) (interface{}, error) {
	switch element := elementAny.(type) {
	case string:
		return elementResolver.stringResolver.resolveString(&element, bindingDataList)
	case float64:
		return element, nil
	case bool:
		return element, nil
	case nil:
		return element, nil
	case map[string]interface{}:
		newElement := make(map[string]interface{})
		for key, value := range element {
			if isKeyTag(key) {
				if valueList, ok := value.([]interface{}); ok {
					tagTemp := make([]interface{}, len(valueList)+1)
					tagTemp[0] = key
					copy(tagTemp[1:], valueList)
					resolvedTuple, err := elementResolver.ResolveElement(tagTemp, bindingDataList)
					if err != nil {
						return nil, err
					}
					if resolvedTupleMap, ok := resolvedTuple.(map[string]interface{}); ok {
						newElement = resolvedTupleMap
					} else if reflect.TypeOf(resolvedTuple) != reflect.TypeOf(intfs.TagNone{}) {
						errl := errors.GenericError
						errl.Message = fmt.Sprintf("Invalid tag result format for JSON object name tag: %v %v => %v", key, value, resolvedTupleMap)
						return nil, errl
					}
				} else {
					errl := errors.GenericError
					errl.Message = fmt.Sprintf("Value must be a list if name is a tag: %v %v", key, value)
					return nil, &errl
				}
			} else {
				var newKey interface{}
				var newValue interface{}
				var err error
				if newKey, err = elementResolver.ResolveElement(key, bindingDataList); err != nil {
					return nil, err
				}
				if newValue, err = elementResolver.ResolveElement(value, bindingDataList); err != nil {
					return nil, err
				}
				if newKeyStr, ok := newKey.(string); ok && reflect.TypeOf(newValue) != reflect.TypeOf(intfs.TagNone{}) {
					newElement[newKeyStr] = newValue
				}
			}
		}
		return newElement, nil
	case []interface{}:
		if isTag(element) {
			return elementResolver.tagResolver.resolve(element, bindingDataList)
		}
		newElement := make([]interface{}, len(element))
		var err error
		var newItem interface{}
		count := 0
		for _, item := range element {
			if newItem, err = elementResolver.ResolveElement(item, bindingDataList); err == nil {
				if reflect.TypeOf(newItem) != reflect.TypeOf(intfs.TagNone{}) {
					newElement[count] = newItem
					count++
				}
			} else {
				return nil, err
			}
		}
		return newElement[:count], nil
	default:
		errf := errors.GenericError
		errf.Message = fmt.Sprintf("Unknown data type %T of %v", element, element)
		return nil, &errf
	}
}
