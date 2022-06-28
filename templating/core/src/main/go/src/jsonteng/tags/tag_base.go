// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package tags

import (
	"fmt"
	"io"
	"jsonteng/errors"
	intfs "jsonteng/interfaces"
	extTags "jsonteng_contribs/tags"
	"os/exec"
	"strings"
)

// BuildTagMap builds a map containing intrinsic tags.
func BuildTagMap(tagResolver intfs.TagResolver) *map[string]intfs.TagProcessor {
	tagMap := make(map[string]intfs.TagProcessor)
	atTag := atTag{}
	atTag.init(tagResolver)
	tagMap[atTag.Name] = &atTag
	existsTag := existsTag{}
	existsTag.init(tagResolver)
	tagMap[existsTag.Name] = &existsTag
	foreachTag := foreachTag{}
	foreachTag.init(tagResolver)
	tagMap[foreachTag.Name] = &foreachTag
	lenTag := lenTag{}
	lenTag.init(tagResolver)
	tagMap[lenTag.Name] = &lenTag
	oneofTag := oneofTag{}
	oneofTag.init(tagResolver)
	tagMap[oneofTag.Name] = &oneofTag
	toboolTag := toboolTag{}
	toboolTag.init(tagResolver)
	tagMap[toboolTag.Name] = &toboolTag
	tofloatTag := tofloatTag{}
	tofloatTag.init(tagResolver)
	tagMap[tofloatTag.Name] = &tofloatTag
	tointTag := tointTag{}
	tointTag.init(tagResolver)
	tagMap[tointTag.Name] = &tointTag
	tonullTag := tonullTag{}
	tonullTag.init(tagResolver)
	tagMap[tonullTag.Name] = &tonullTag

	extMap := extTags.BuildTagMap(tagResolver)
	for k, v := range extMap {
		tagMap[k] = v
	}
	return &tagMap
}

func safeEval(exprObj interface{}) (bool, error) {
	expr, ok := exprObj.(string)
	if !ok {
		if expr, ok := exprObj.(bool); ok {
			return expr, nil
		}
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("SafeEval: Invalid expr type. %v", exprObj)
		return false, &errl
	}
	if expr == "True" {
		return false, nil
	} else if expr == "False" {
		return false, nil
	}
	script := fmt.Sprintf("print(eval('%s', {'__builtins__': None}, {}))", expr)
	cmd := exec.Command("python", "-")
	stdin, err := cmd.StdinPipe()
	if err != nil {
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("SafeEval: Expression %v evaluation failed due to stdin pipe closed. %v", exprObj)
		return false, &errl
	}
	go func() {
		defer stdin.Close()
		io.WriteString(stdin, script)
	}()
	result, err := cmd.Output()
	if err != nil {
		errl := errors.GenericError
		errl.Message = fmt.Sprintf("SafeEval: Expression %v evaluation failed. %v", exprObj, err)
		return false, &errl
	}
	resultStr := strings.TrimSpace(string(result))
	if strings.EqualFold(resultStr, "True") {
		return true, nil
	} else if strings.EqualFold(resultStr, "False") {
		return false, nil
	}
	errl := errors.GenericError
	errl.Message = fmt.Sprintf("SafeEval: Expression %v is not valid. %v", exprObj, resultStr)
	return false, &errl
}
