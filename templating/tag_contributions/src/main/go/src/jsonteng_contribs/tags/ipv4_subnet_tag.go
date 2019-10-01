// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package tags

import (
	"container/list"
	"encoding/binary"
	"fmt"
	"jsonteng/errors"
	intfs "jsonteng/interfaces"
	"net"
	"strconv"
)

type ipv4SubnetTag struct {
	intfs.TagBase
	elementResolver intfs.ElementResolver
}

func (tag *ipv4SubnetTag) init(tagResolver intfs.TagResolver) {
	tag.Name = "ipv4-subnet"
	tag.TagResolver = tagResolver
	tag.elementResolver = tagResolver.GetElementResolver()
}

func (tag *ipv4SubnetTag) Process(tagTokens []interface{}, bindingDataList *list.List) (interface{}, error) {
	tokenCount := len(tagTokens)
	if tokenCount != 3 {
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Tag \"%s\" requires 3 parameters. Parameters given %v", tag.Name, tagTokens)
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
	networkPrefix, _ := ipv4Net.Mask.Size()
	subnetCountObj, err := tag.elementResolver.ResolveElement(tagTokens[1], bindingDataList)
	if err != nil {
		return nil, err
	}
	var subnetCount int64
	switch subnetCountTemp := subnetCountObj.(type) {
	case float64:
		subnetCount = int64(subnetCountTemp)
	case string:
		subnetCount, err = strconv.ParseInt(subnetCountTemp, 10, 32)
		if err != nil {
			errl := errors.GenericError
			errl.Message = fmt.Sprintf("Invalid subnet count format %v", subnetCountTemp)
			return nil, &errl
		}
	default:
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Unknown subnet count type %v", subnetCountTemp)
		return nil, &errl
	}
	subnetIndexObj, err := tag.elementResolver.ResolveElement(tagTokens[2], bindingDataList)
	if err != nil {
		return nil, err
	}
	var subnetIndex int64
	switch subnetIndexTemp := subnetIndexObj.(type) {
	case float64:
		subnetIndex = int64(subnetIndexTemp)
	case string:
		subnetIndex, err = strconv.ParseInt(subnetIndexTemp, 10, 32)
		if err != nil {
			errl := errors.GenericError
			errl.Message = fmt.Sprintf("Invalid subnet index format %v", subnetIndexTemp)
			return nil, &errl
		}
	default:
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Unknown subnet index type %v", subnetIndexTemp)
		return nil, &errl
	}
	base2Exp := 0
	count := subnetCount - 1
	for (count & 0x1) != 0 {
		count = count >> 1
		base2Exp++
	}
	if count != 0 {
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("Subnet count must be multiple of 2s. %v is given", subnetCount)
		return nil, &errl
	}
	subnetPrefix := networkPrefix + base2Exp
	networkBytes := binary.BigEndian.Uint32(network)
	subnetBytes := networkBytes + (uint32(subnetIndex) << uint32(32-subnetPrefix))
	_, subnet, _ := net.ParseCIDR("0.0.0.0/0")
	binary.BigEndian.PutUint32(subnet.IP, subnetBytes)
	subnet.Mask = net.CIDRMask(subnetPrefix, 32)
	return subnet.String(), nil
}
