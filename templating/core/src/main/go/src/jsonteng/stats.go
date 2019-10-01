// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package jsonteng

type stats struct {
	parameterMap map[string]int
}

func (stats *stats) init() {
	stats.parameterMap = make(map[string]int)
}

func (stats *stats) updateStats(parameter *string) {
	var parameterCount int
	var ok bool
	if parameterCount, ok = stats.parameterMap[*parameter]; !ok {
		parameterCount = 0
	}
	stats.parameterMap[*parameter] = parameterCount + 1
}

func (stats *stats) getStats() map[string]int {
	return stats.parameterMap
}
