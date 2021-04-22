// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package jsonteng

import (
	"container/list"
	"encoding/json"
	"fmt"
	"jsonteng/errors"
	intfs "jsonteng/interfaces"
	"regexp"
	"strconv"
)

type stringResolver interface {
	resolveString(strData *string, bindingDataList *list.List) (interface{}, error)
}

type stringResolverImpl struct {
	elementResolver intfs.ElementResolver
	stats           *stats
}

var pattern = regexp.MustCompile("([a-zA-Z0-9]+)\\[([0-9]+)\\]")

func (stringResolver *stringResolverImpl) init(stats *stats) {
	stringResolver.stats = stats
}

func (stringResolver *stringResolverImpl) setElementResolver(elementResolver intfs.ElementResolver) {
	stringResolver.elementResolver = elementResolver
}

func (stringResolver *stringResolverImpl) resolveString(strData *string, bindingDataList *list.List) (interface{}, error) {
	var errl errors.TemplateEngineError
	strLen := len(*strData)
	stack := list.New()
	i := 0
	for i < strLen {
		c := (*strData)[i]
		if c == '\\' {
			i += 2
		} else if c == '$' {
			nextIndex := i + 1
			if nextIndex < strLen && (*strData)[nextIndex] == '{' {
				stack.PushBack(i)
				i += 2
			} else {
				i++
			}
		} else if c == '}' {
			i++
			if stack.Len() > 0 {
				paramStart := stack.Remove(stack.Back()).(int)
				paramName := (*strData)[paramStart+2 : i-1]
				value, err := stringResolver.resolveParam(&paramName, bindingDataList)
				if err != nil {
					return nil, err
				}
				subStrBeforeParam := (*strData)[:paramStart]
				var subStrAfterParam string = ""
				if i < strLen {
					subStrAfterParam = (*strData)[i:]
				}
				if len(subStrBeforeParam) > 0 || len(subStrAfterParam) > 0 {
					substrMid, err := stringResolver.elementResolver.ResolveElement(value, bindingDataList)
					if err != nil {
						return nil, err
					}
					mid, err := dataToString(substrMid)
					if err != nil {
						return nil, err
					}
					newStr := subStrBeforeParam + mid + subStrAfterParam
					strData = &newStr
					strLen = len(*strData)
					i = paramStart
				} else {
					return stringResolver.elementResolver.ResolveElement(value, bindingDataList)
				}
			}
		} else {
			i++
		}
	}
	if stack.Len() > 0 {
		errl = errors.GenericError
		errl.Message = fmt.Sprintf("Mis-formed parameterized string \"%s\".", *strData)
		return nil, &errl
	}
	return *strData, nil
}

func (stringResolver *stringResolverImpl) resolveParam(paramName *string, bindingDataList *list.List) (interface{}, error) {
	separatorIndices := collectSeparatorIndices(paramName)
	for bindingData := bindingDataList.Front(); bindingData != nil; bindingData = bindingData.Next() {
		if value, err := findParam(paramName, separatorIndices, bindingData.Value.(map[string]interface{})); err == nil || err.ErrorCode != errors.INVALID_REFERENCE {
			if value != nil {
				stringResolver.stats.updateStats(paramName)
				return value, nil
			}
		}
	}
	errl := errors.UnresolvableParameter
	errl.Message = fmt.Sprintf("Unable to resolve parameter \"%s\".", *paramName)
	return nil, &errl
}

func findParam(paramName *string, separatorIndices []int, bindingData map[string]interface{}) (interface{}, *errors.TemplateEngineError) {
	tokenStart := 0
	var nextData interface{}
	nextData = bindingData
	var value interface{}
	var err *errors.TemplateEngineError
	for i := 0; i < len(separatorIndices)+1; i++ {
		if _, ok := nextData.(map[string]interface{}); !ok {
			errl := errors.InvalidReference
			errl.Message = fmt.Sprintf("invalid scope")
			return nil, &errl
		}
		key := (*paramName)[tokenStart:]
		if value, err = matchKey(&key, &nextData); err == nil || err.ErrorCode != errors.INVALID_REFERENCE {
			return value, err
		}
		if i < len(separatorIndices) {
			token := (*paramName)[tokenStart:separatorIndices[i]]
			nextData, err = matchKey(&token, &nextData)
			if err != nil && err.ErrorCode != errors.INVALID_REFERENCE {
				return nil, err
			}
			tokenStart = separatorIndices[i] + 1
		}
	}
	errl := errors.InvalidReference
	errl.Message = fmt.Sprintf("mismatch binding data")
	return nil, &errl
}

func matchKey(key *string, data *interface{}) (interface{}, *errors.TemplateEngineError) {
	matches := pattern.FindStringSubmatch(*key)
	if len(matches) == 3 {
		key = &matches[1]
		index, err := strconv.Atoi(matches[2])
		if err != nil || index < 0 {
			errl := errors.GenericError
			errl.Message = fmt.Sprintf("Parameter index is invalid, %s", *key)
			return nil, &errl
		}
		if v, ok := (*data).(map[string]interface{})[*key]; ok {
			if w, ok := v.([]interface{}); ok {
				if index < len(w) {
					return w[index], nil
				}
			}
		}
		errl := errors.InvalidReference
		errl.Message = fmt.Sprintf("mismatch binding data")
		return nil, &errl
	}
	if v, ok := (*data).(map[string]interface{})[*key]; ok {
		return v, nil
	}
	errl := errors.InvalidReference
	errl.Message = fmt.Sprintf("mismatch binding data")
	return nil, &errl
}

func collectSeparatorIndices(paramName *string) []int {
	indices := list.New()
	for i := 0; i < len(*paramName); i++ {
		if (*paramName)[i] == '\\' {
			i++
		} else if (*paramName)[i] == '.' {
			indices.PushBack(i)
		}
	}
	indicesArray := make([]int, indices.Len())
	i := 0
	for index := indices.Front(); index != nil; index = index.Next() {
		indicesArray[i] = index.Value.(int)
		i++
	}
	return indicesArray
}

func dataToString(value interface{}) (string, error) {
	switch v := value.(type) {
	case string:
		return v, nil
	default:
		if s, ok := json.Marshal(v); ok == nil {
			return string(s), nil
		}
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Json error. %v", v)
		return "", &errl
	}
}
