# Copyright 2020 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from numbers import Number

from .consts import WS_CURRENT_POINTER, PATH, DESCRIPTOR, BEFORE


def driff_enter(target, companion, params, workspace):
    """
    Drift detection enter function.
    :param target: The target.
    :type target: JSON value
    :param companion: The companion.
    :type companion: JSON value
    :param params: The descriptor parameters.
    :type params: dict
    :param workspace: The remediation workspace.
    :type workspace: dict
    """
    if isinstance(target, str) \
            or isinstance(target, Number) \
            or isinstance(target, bool) \
            or target is None:
        if companion != target:
            print("Drift: path({}), target({}), companion({})".
                  format(workspace[WS_CURRENT_POINTER],
                         target, companion))


drift_descriptors = [
    {
        PATH: ".+",
        DESCRIPTOR: {
            BEFORE: "jsonreme.drift.driff_enter"
        }
    }
]
