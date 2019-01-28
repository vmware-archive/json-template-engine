// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

package com.vmware.jsonteng;

public interface JsonLoader {

    Object load(String jsonResource) throws TemplateEngineException;

    void unload(String jsonResource) throws TemplateEngineException;

}
