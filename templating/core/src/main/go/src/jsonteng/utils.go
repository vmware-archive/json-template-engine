// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package jsonteng

import (
	"container/list"
	"strings"
)

func unescapeJSON(elementAny interface{}) interface{} {
	switch element := elementAny.(type) {
	case string:
		return unescapeString(&element)
	case float64:
		return element
	case bool:
		return element
	case nil:
		return element
	case map[string]interface{}:
		newElement := make(map[string]interface{})
		for k, v := range element {
			newKey := unescapeJSON(k)
			newValue := unescapeJSON(v)
			newElement[newKey.(string)] = newValue
		}
		return newElement
	case []interface{}:
		newElement := make([]interface{}, len(element))
		for index, item := range element {
			newItem := unescapeJSON(item)
			newElement[index] = newItem
		}
		return newElement
	default:
		return nil
	}
}

func unescapeString(escapedString *string) string {
	unescaped := ""
	start := 0
	for index := strings.IndexByte(*escapedString, '\\'); index != -1; index = strings.IndexByte((*escapedString)[start:], '\\') {
		unescaped = unescaped + (*escapedString)[start:index]
		start = index + 1
	}
	unescaped = unescaped + (*escapedString)[start:]
	return unescaped
}

func checkDuplicatedBindingData(bindingDataList *list.List) *map[string][]interface{} {
	bindingDataMap := make(map[string]list.List)
	for bindingData := bindingDataList.Front(); bindingData != nil; bindingData = bindingData.Next() {
		data := bindingData.Value.(map[string]interface{})
		findParamTerminal("", &data, &bindingDataMap)
	}
	dupMap := make(map[string][]interface{})
	for k, v := range bindingDataMap {
		if v.Len() > 1 {
			d := make([]interface{}, v.Len())
			for e := v.Front(); e != nil; e = e.Next() {
				d[len(d)] = e.Value
			}
			dupMap[k] = d
		}
	}
	return &dupMap
}

func findParamTerminal(superName string, bindingData *map[string]interface{}, bindingDataMap *map[string]list.List) {
	for name, v := range *bindingData {
		if len(superName) == 0 {
			name = superName + "." + name
		}
		switch value := v.(type) {
		case map[string]interface{}:
			findParamTerminal(name, &value, bindingDataMap)
		default:
			l := (*bindingDataMap)[name]
			l.PushFront(value)
		}
	}
}
