// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package jsonteng

import (
	"container/list"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"jsonteng/errors"
	intfs "jsonteng/interfaces"
	"net/http"
	"strconv"
	"strings"
)

type jsonLoaderImpl struct {
	loadImpl   func(jsonResource string) (jsonObject interface{}, err error)
	unloadImpl func(jsonResource string) error
}

func (l jsonLoaderImpl) Load(jsonResource string) (jsonObject interface{}, err error) {
	return l.loadImpl(jsonResource)
}

func (l jsonLoaderImpl) Unload(jsonResource string) error {
	return l.unloadImpl(jsonResource)
}

type dirStackElement struct {
	resource string
	path     string
}

// GetLoader is a factory function for generating default JSON loader.
func GetLoader(rootPath string, verbose bool) intfs.JSONLoader {
	dirstack := list.New()
	dirstack.PushBack(dirStackElement{"root", rootPath})

	return jsonLoaderImpl{
		loadImpl: func(jsonResource string) (jsonObject interface{}, err error) {
			currentDir := dirstack.Back().Value.(dirStackElement).path
			effectiveURL := currentDir + jsonResource
			var jsonBytes []byte
			if strings.Contains(effectiveURL, "://") {
				resp, err := http.Get(effectiveURL)
				if err == nil {
					jsonBytes, err = ioutil.ReadAll(resp.Body)
					resp.Body.Close()
				}
			} else {
				jsonBytes, err = ioutil.ReadFile(effectiveURL)
			}
			if err == nil {
				err = json.Unmarshal(jsonBytes, &jsonObject)
				if err != nil {
					return nil, err
				}
				lastDirIndex := strings.LastIndex(effectiveURL, "/")
				if lastDirIndex != -1 {
					dirstack.PushBack(dirStackElement{jsonResource, effectiveURL[:lastDirIndex+1]})
				}
				return jsonObject, nil
			}
			err = json.Unmarshal([]byte(jsonResource), &jsonObject)
			dirstack.PushBack(dirStackElement{jsonResource, currentDir})
			if err != nil {
				if verbose {
					fmt.Printf("Treat %s as JSON value\n", jsonResource)
				}
				i, err := strconv.ParseInt(jsonResource, 10, 64)
				if err == nil {
					return i, nil
				}
				f, err := strconv.ParseFloat(jsonResource, 64)
				if err == nil {
					return f, nil
				}
				b, err := strconv.ParseBool(jsonResource)
				if err == nil {
					return b, nil
				}
				return jsonResource, nil
			}
			return jsonObject, nil
		},
		unloadImpl: func(jsonResource string) error {
			if dirstack.Remove(dirstack.Back()).(dirStackElement).resource != jsonResource {
				err := errors.GenericError
				err.Message = "JSON resource loading is out of order."
				return &err
			}
			return nil
		}}
}
