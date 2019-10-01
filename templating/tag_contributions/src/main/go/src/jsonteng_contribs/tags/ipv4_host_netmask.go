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

type ipv4HostNetmaskTag struct {
	intfs.TagBase
	elementResolver intfs.ElementResolver
}

func (tag *ipv4HostNetmaskTag) init(tagResolver intfs.TagResolver) {
	tag.Name = "ipv4-host-netmask"
	tag.TagResolver = tagResolver
	tag.elementResolver = tagResolver.GetElementResolver()
}

func (tag *ipv4HostNetmaskTag) Process(tagTokens []interface{}, bindingDataList *list.List) (interface{}, error) {
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
	netmask := ipv4Net.Mask
	ipForm := net.IPv4(netmask[0], netmask[1], netmask[2], netmask[3])
	return ipForm.String(), nil
}
