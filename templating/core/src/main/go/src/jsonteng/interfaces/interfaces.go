// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package interfaces

import (
	"container/list"
)

// JSONLoader is an interface for loading and unloading JSON objects in the form of a file or a string.
type JSONLoader interface {
	Load(jsonResource string) (jsonObject interface{}, err error)
	Unload(jsonResource string) error
}

// ElementResolver is an interface for element resolving functions.
type ElementResolver interface {
	ResolveElement(elementAny interface{}, bindingDataList *list.List) (interface{}, error)
}

// TagProcessor is an interface for tag processing functions.
type TagProcessor interface {
	Process(tagTokens []interface{}, bindingDataList *list.List) (interface{}, error)
}

// TagResolver is an interface for tag resolving functions.
type TagResolver interface {
	GetElementResolver() ElementResolver
	GetLoader() JSONLoader
}

// TagBase is struct for defining a tag type.
type TagBase struct {
	Name        string
	TagResolver TagResolver
}

// TagNone is a special tag type representing a resolved tag to be ignored.
type TagNone struct{}
