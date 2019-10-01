// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package errors

/*
TemplateEngineError is a type representing jsonteng errors
*/
type TemplateEngineError struct {
	ErrorCode int
	ErrorName string
	Message   string
}

const NO_ERROR = 0
const GENERIC_ERROR = -1
const INVALID_REFERENCE = 1
const UNRESOLVABLE_PARAMETER = 2

var (
	NoError               = TemplateEngineError{NO_ERROR, "NO ERROR", ""}
	GenericError          = TemplateEngineError{GENERIC_ERROR, "UNKNOWN ERROR", ""}
	InvalidReference      = TemplateEngineError{INVALID_REFERENCE, "INVALID REFERENCE", ""}
	UnresolvableParameter = TemplateEngineError{UNRESOLVABLE_PARAMETER, "UNRESOLVABLE_PARAMETER", ""}
)

func (e TemplateEngineError) Error() string {
	return e.Message
}
