// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package tags

import (
	intfs "jsonteng/interfaces"
)

// BuildTagMap is a function for building external tags.
func BuildTagMap(tagResolver intfs.TagResolver) (tagMap map[string]intfs.TagProcessor) {
	tagMap = make(map[string]intfs.TagProcessor)
	ipv4HostGatewayTag := ipv4HostGatewayTag{}
	ipv4HostGatewayTag.init(tagResolver)
	tagMap[ipv4HostGatewayTag.Name] = &ipv4HostGatewayTag
	ipv4HostIPTag := ipv4HostIPTag{}
	ipv4HostIPTag.init(tagResolver)
	tagMap[ipv4HostIPTag.Name] = &ipv4HostIPTag
	ipv4HostNetmaskTag := ipv4HostNetmaskTag{}
	ipv4HostNetmaskTag.init(tagResolver)
	tagMap[ipv4HostNetmaskTag.Name] = &ipv4HostNetmaskTag
	ipv4SubnetTag := ipv4SubnetTag{}
	ipv4SubnetTag.init(tagResolver)
	tagMap[ipv4SubnetTag.Name] = &ipv4SubnetTag
	return
}
