# Copyright 2020 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

class RemediationEngineException(Exception):
    """
    Exception class for template engine exceptions.
    """
    pass

class InvalidReferenceException(RemediationEngineException):
    """
    Exception class for invalid parameter reference.
    """
    pass

class UnresolvableParameterException(RemediationEngineException):
    """
    Exception class for unresolvable parameters.
    """
    pass
