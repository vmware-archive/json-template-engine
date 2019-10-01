// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package tags

import (
	"container/list"
	"fmt"
	"jsonteng/errors"
	intfs "jsonteng/interfaces"
	"net"
	"strconv"
)

type ipv4HostIPTag struct {
	intfs.TagBase
	elementResolver intfs.ElementResolver
}

func (tag *ipv4HostIPTag) init(tagResolver intfs.TagResolver) {
	tag.Name = "ipv4-host-ip"
	tag.TagResolver = tagResolver
	tag.elementResolver = tagResolver.GetElementResolver()
}

func (tag *ipv4HostIPTag) Process(tagTokens []interface{}, bindingDataList *list.List) (interface{}, error) {
	tokenCount := len(tagTokens)
	if tokenCount != 2 {
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Tag \"%s\" requires 2 parameters. Parameters given %v", tag.Name, tagTokens)
		return nil, &errl
	}
	resolvedNetworkObj, err := tag.elementResolver.ResolveElement(tagTokens[0], bindingDataList)
	if err != nil {
		return nil, err
	}
	resolvedNetwork, ok := resolvedNetworkObj.(string)
	if !ok {
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Invalid network %v", resolvedNetworkObj)
		return nil, &errl
	}
	_, ipv4Net, err := net.ParseCIDR(resolvedNetwork)
	if err != nil {
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Invalid network format %v", resolvedNetwork)
		return nil, &errl
	}
	network := ipv4Net.IP
	indexObj, err := tag.elementResolver.ResolveElement(tagTokens[1], bindingDataList)
	if err != nil {
		return nil, err
	}
	var index int64
	switch indexTemp := indexObj.(type) {
	case float64:
		index = int64(indexTemp)
	case string:
		index, err = strconv.ParseInt(indexTemp, 10, 32)
		if err != nil {
			errl := errors.GenericError
			errl.Message = fmt.Sprintf("Invalid address index %v", indexTemp)
			return nil, &errl
		}
	default:
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Unknown address index type %v", indexTemp)
		return nil, &errl
	}
	return net.IPv4(network[0], network[1], network[2], network[3]+byte(index)).String(), nil
}
