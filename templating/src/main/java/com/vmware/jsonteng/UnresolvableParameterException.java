// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

public class UnresolvableParameterException extends TemplateEngineException {
    public UnresolvableParameterException(String message) {
        super(message);
    }

    public UnresolvableParameterException(String message, Exception e) {
        super(message, e);
    }
}
