// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

public class InvalidReferenceException extends TemplateEngineException {
    public InvalidReferenceException(String message) {
        super(message);
    }

    public InvalidReferenceException(String message, Exception e) {
        super(message, e);
    }
}
