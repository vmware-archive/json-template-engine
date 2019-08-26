// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#pragma once

#include <stdexcept>

namespace jsonteng {

class TemplateEngineException : public std::runtime_error {
public:
  TemplateEngineException(const std::string &msg)
      : std::runtime_error::runtime_error(msg) {}

  TemplateEngineException(const char *msg)
      : std::runtime_error::runtime_error(msg) {}
};

class InvalidReferenceException : public TemplateEngineException {
public:
  InvalidReferenceException(const std::string &msg)
      : TemplateEngineException(msg) {}

  InvalidReferenceException(const char *msg) : TemplateEngineException(msg) {}
};

class UnresolvableParameterException : public TemplateEngineException {
public:
  UnresolvableParameterException(const std::string &msg)
      : TemplateEngineException(msg) {}

  UnresolvableParameterException(const char *msg)
      : TemplateEngineException(msg) {}
};

class TagNoneException : public TemplateEngineException {
public:
  TagNoneException()
      : TemplateEngineException("TagNoneException") {}
};

} // namespace jsonteng
