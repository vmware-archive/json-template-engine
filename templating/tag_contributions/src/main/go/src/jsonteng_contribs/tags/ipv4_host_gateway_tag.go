// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package tags

import (
	"container/list"
	"fmt"
	"jsonteng/errors"
	intfs "jsonteng/interfaces"
	"net"
)

type ipv4HostGatewayTag struct {
	intfs.TagBase
	elementResolver intfs.ElementResolver
}

func (tag *ipv4HostGatewayTag) init(tagResolver intfs.TagResolver) {
	tag.Name = "ipv4-host-gateway"
	tag.TagResolver = tagResolver
	tag.elementResolver = tagResolver.GetElementResolver()
}

func (tag *ipv4HostGatewayTag) Process(tagTokens []interface{}, bindingDataList *list.List) (interface{}, error) {
	tokenCount := len(tagTokens)
	if tokenCount != 1 {
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Tag \"%s\" requires 1 parameter. Parameters given %v", tag.Name, tagTokens)
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
	return net.IPv4(network[0], network[1], network[2], network[3]+1).String(), nil
}
