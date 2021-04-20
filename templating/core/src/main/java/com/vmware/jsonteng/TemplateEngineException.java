// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

public class TemplateEngineException extends RuntimeException {
    public TemplateEngineException(String message) {
        super(message);
    }

    public TemplateEngineException(String message, Exception e) {
        super(message, e);
    }
}
