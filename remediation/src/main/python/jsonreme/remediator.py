# Copyright 2020 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import argparse
import json
import re
from collections import OrderedDict
from importlib import import_module
from numbers import Number

from .consts import DESCRIPTORS, WS_CURRENT_POINTER, BEFORE, AFTER, \
    PARAMS, PATH, DESCRIPTOR, POINTER_SEPARATOR, WS_OUTPUT, WS_ENV
from .drift import drift_descriptors
from .exception import RemediationEngineException


class JsonRemediator(object):
    """
    The remediator can be used to remediate a system from its current state to
    its desired state. States are described by JSON data. Each element in a JSON
    object represents a scope where an enter or an exit operation can be
    performed. The remediator traverses the desired state JSON and applies
    enter and/or exit remediation function calls. Remediation functions are
    provided by users. They are organized in the JSON format. JSON object keys
    are matched to the desired state JSON following the same scope pattern. The
    value of a remediation JSON element may contain three parts: an enter
    function, an exit function, and a sub state.
    """

    def __init__(self, remediation_descriptors):
        """
        Remediator constructor. The remediation descriptors has two forms. The
        canonical form is
        [
          {
            "path": <JSON pointer>,
            "descriptor": {
              "@enter": <function reference>,
              "@exit": <function reference>,
              "@params": {<static parameters>}
            }
          },
          ...
        ]
        "path" is defined as a JSON pointer (RFC 6901). It can be a regex
        pattern. The pattern is used to match each sub-state of the desired
        state. If there is a match, the corresponding functions of "descriptor"
        are applied at the appropriate points. "@enter" function is applied
        before any sub-state of the processing state is processed. "@exit"
        function is applied after any sub-state of the processing state is
        processed. "@params" is passed to these functions.
        The convenient form is
        {
          "@enter": <function reference>,
          "@exit": <function reference>,
          "@params": {<static parameters>},
          "@descriptors": {<recursive definition>}
        }
        The recursive definition enables the convenient form to mimic the
        structure of the desire state JSON. This form may be useful for
        visualizing descriptors. The convenient form is converted to the
        canonical form before remediation is applied.
        :param remediation_descriptors: The remediation descriptors.
        :type remediation_descriptors: Union[list,dict]
        """
        if isinstance(remediation_descriptors, dict):
            descriptors = list()
            JsonRemediator._convert_to_json_path(
                remediation_descriptors, descriptors, dict())
        elif isinstance(remediation_descriptors, list):
            descriptors = remediation_descriptors
        else:
            raise RemediationEngineException(
                "Unknown data type {} of {}".format(
                    type(remediation_descriptors), remediation_descriptors))
        self._descriptors = JsonRemediator._load_functions(descriptors)
        if self._descriptors is None:
            raise RemediationEngineException("No valid remediation descriptors")

    @staticmethod
    def _convert_to_json_path(descriptor_dict, descriptor_list, path):
        """
        Convert a dict format descriptors to the list format descriptors.
        :param descriptor_dict: The dict format descriptors.
        :type descriptor_dict: dict
        :param descriptor_list: The list format descriptors.
        :type descriptor_list: list
        :param path: A workspace.
        :type path: dict
        """
        descriptor_list.append(
            {
                "path": path,
                "descriptor": descriptor_dict
            })
        descriptors = descriptor_dict.get(DESCRIPTORS)
        if descriptors:
            if isinstance(descriptors, dict):
                for key, value in descriptors.items():
                    JsonRemediator._push_crp(key, path)
                    JsonRemediator._convert_to_json_path(
                        value, descriptor_list, path)
                    JsonRemediator._pop_crp(path)
            elif isinstance(descriptors, list):
                for idx, item in enumerate(descriptors):
                    JsonRemediator._push_crp(idx, path)
                    JsonRemediator._convert_to_json_path(
                        item, descriptor_list, path)
                    JsonRemediator._pop_crp(path)

    def remediate(self, target, companion=None, env=None):
        """
        Apply remediation descriptors to "target".
        :param target: The target JSON.
        :type target: JSON value
        :param companion: The companion JSON.
        :type companion: JSON value
        :param env: The global parameters.
        :type env: dict
        :return: The workspace.
        :rtype: dict
        """
        workspace = dict()
        workspace[WS_CURRENT_POINTER] = ""
        workspace[WS_ENV] = env if env else dict()
        self._remediate(target, companion, workspace)
        return workspace

    def _remediate(self, target, companion, workspace):
        """
        Recursively apply remediation descriptors to the desired state.
        :param target: The target.
        :type target: JSON value
        :param companion: The companion.
        :type companion: JSON value
        :param workspace: The remediation workspace.
        :type workspace: dict
        """
        if target is None:
            return
        if isinstance(target, str) \
                or isinstance(target, Number) \
                or isinstance(target, bool) \
                or target is None:
            descriptors = self._find_descriptors(workspace)
            JsonRemediator._call_func(descriptors, BEFORE,
                                      target, companion, workspace)
            JsonRemediator._call_func(descriptors, AFTER,
                                      target, companion, workspace)
        elif isinstance(target, dict):
            descriptors = self._find_descriptors(workspace)
            JsonRemediator._call_func(descriptors, BEFORE,
                                      target, companion, workspace)
            for key, value in target.items():
                JsonRemediator._push_crp(key, workspace)
                self._remediate(
                    value,
                    companion.get(key) if companion else None,
                    workspace)
                JsonRemediator._pop_crp(workspace)
            JsonRemediator._call_func(descriptors, AFTER,
                                      target, companion, workspace)
        elif isinstance(target, list):
            descriptors = self._find_descriptors(workspace)
            JsonRemediator._call_func(descriptors, BEFORE,
                                      target, companion, workspace)
            for idx, item in enumerate(target):
                JsonRemediator._push_crp(idx, workspace)
                self._remediate(
                    item,
                    companion[idx] if companion and
                                      idx < len(companion) else None,
                    workspace)
                JsonRemediator._pop_crp(workspace)
            JsonRemediator._call_func(descriptors, AFTER,
                                      target, companion, workspace)
        else:
            raise RemediationEngineException(
                "Unknown data type {} of {}".format(type(target),
                                                    target))

    def _find_descriptors(self, workspace):
        """
        Find matching descriptors for the current processing state.
        :param workspace: The workspace.
        :type workspace: dict
        :return: The matching descriptor list.
        :rtype: list
        """
        match_list = list()
        crp = workspace[WS_CURRENT_POINTER]
        for d in self._descriptors:
            if d['path'].match(crp):
                match_list.append(d['descriptor'])
        return match_list

    @staticmethod
    def _call_func(descriptors, func_type, target, companion, workspace):
        """
        Call a function in remediation_descriptor of type "func_type".
        :param descriptors: The remediation descriptor.
        :type descriptors: list
        :param func_type: Function type.
        :type func_type: str
        :param target: The target that the remediation descriptor
                             is applied to.
        :type target: JSON value
        :param companion: The companion that the remediation descriptor
                              is applied to.
        :type companion: JSON value
        :param workspace: The remediation workspace.
        :type workspace: dict
        """
        func_ptr = workspace[WS_CURRENT_POINTER] + "." + func_type
        for d in descriptors:
            func = d.get(func_type) if d else None
            if func:
                ret_key = func_ptr + '$' + func.__module__ + '.' + func.__name__
                if ret_key not in workspace:
                    ret = func(target, companion, d.get(PARAMS),
                               workspace)
                    workspace[ret_key] = ret

    @staticmethod
    def _load_functions(descriptor_list):
        """
        Replace function string names by function objects in descriptors.
        :param descriptor_list: Remediation descriptors.
        :type descriptor_list: list
        :return: Loaded descriptor list.
        :rtype: list
        """
        if descriptor_list is None:
            return None
        loaded_descriptor_list = list()
        for d in descriptor_list:
            path = d[PATH]
            descriptor = d[DESCRIPTOR]
            if BEFORE in descriptor:
                descriptor[BEFORE] = JsonRemediator._get_func(
                    descriptor[BEFORE])
            if AFTER in descriptor:
                descriptor[AFTER] = JsonRemediator._get_func(
                    descriptor[AFTER])
            loaded_descriptor_list.append({
                PATH: re.compile(path),
                DESCRIPTOR: descriptor
            })
        return loaded_descriptor_list

    @staticmethod
    def _get_func(func_path):
        """
        Return a function object based on a function path in the format of
        <full package path>.<function name>. For example, function xyz in a
        package acme.deploy is "acme.deploy.xyz".
        :param func_path: Function path.
        :type func_path: str
        """
        func = None
        if func_path:
            module_path, func_name = func_path.rsplit('.', 1)
            module = import_module(module_path)
            func = getattr(module, func_name)
        return func

    @staticmethod
    def _push_crp(name, workspace):
        """
        Push a segment into the current remediation JSON pointer.
        :param name: The segment name.
        :type name: Union[str,int]
        :param workspace: The workspace.
        :type workspace: dict
        """
        workspace[WS_CURRENT_POINTER] += POINTER_SEPARATOR + str(name)

    @staticmethod
    def _pop_crp(workspace):
        """
        Pop the last segment of the current remediation JSON pointer.
        :param workspace: The workspace.
        :type workspace: dict
        """
        crp = workspace[WS_CURRENT_POINTER]
        if crp:
            workspace[WS_CURRENT_POINTER] = crp[:crp.rfind(POINTER_SEPARATOR)]


def main(args=None):
    """
    CLI version of the remediation engine.
    """
    parser = argparse.ArgumentParser(
        description='JSON remediation engine.')
    parser.add_argument('-r', '--remediation-descriptors', required=False,
                        help="Remediation descriptors in the form of a list of "
                             "a dictionary.")
    parser.add_argument('-c', '--companion', required=False,
                        help="Companion JSON.")
    parser.add_argument('-e', '--env', required=False,
                        help="Global parameter JSON file.")
    parser.add_argument('-d', '--drift', required=False,
                        help="show drifts between the target and "
                             "the companion",
                        action="store_true")
    parser.add_argument('target')
    params = parser.parse_args(args=args)
    descriptors = None
    if params.remediation_descriptors:
        with open(params.remediation_descriptors, "r") as fp:
            descriptors = json.load(fp, object_pairs_hook=OrderedDict)
    with open(params.target, "r") as fp:
        target = json.load(fp)
    companion = None
    if params.companion:
        with open(params.companion, "r") as fp:
            companion = json.load(fp)
    if params.env:
        with open(params.env, "r") as fp:
            env = json.load(fp)
    else:
        env = dict()
    if not companion and params.drift:
        print("Must provide a companion to detect drifts.")
    if params.drift:
        if descriptors:
            print("Drift detection ignores supplied remediation descriptors.")
        descriptors = drift_descriptors
    if not descriptors:
        print("Remediation descriptors must be provided.")
    remediator = JsonRemediator(descriptors)
    workspace = remediator.remediate(target, companion, env)
    if not params.drift:
        print(workspace.get(WS_OUTPUT))


if __name__ == "__main__":
    main()
