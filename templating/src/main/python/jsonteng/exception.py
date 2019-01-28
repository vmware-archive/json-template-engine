# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

class TemplateEngineException(Exception):
    """
    Exception class for template engine exceptions.
    """
    pass

class InvalidReferenceException(TemplateEngineException):
    """
    Exception class for invalid parameter reference.
    """
    pass

class UnresolvableParameterException(TemplateEngineException):
    """
    Exception class for unresolvable parameters.
    """
    pass
