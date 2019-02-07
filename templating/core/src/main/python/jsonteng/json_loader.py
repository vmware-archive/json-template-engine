# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

import sys
import abc
import urllib.request
import codecs
import json
from collections import OrderedDict
from urllib.parse import urljoin
from numbers import (Number)

from .exception import TemplateEngineException


class JsonLoader(object):
    """
    Base class of the template loader.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def load(self, json_resource):
        """
        Load a template for the json_resource.
        :param json_resource: JSON resource
        :type json_resource: 'str'
        :return: Loaded JSON object.
        :rtype: JSON object.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def unload(self, json_resource):
        """
        Some loader may store an internal state. This method is called
        to clean up the internal state if any.
        :param json_resource: Loaded JSON resource.
        :type json_resource: 'str'
        """
        raise NotImplementedError


class DefaultJsonLoader(JsonLoader):
    """
    This loader can be used to load a JSON resource identified by URL and
    file path. It also maintains a directory stack so that nested templates
    can be loaded by relative paths.
    """
    def __init__(self, root_path=None, verbose=False):
        """
        Construct a default loader.
        :param root_path: The root port of a URL or file path.
        :type root_path: 'str'
        :param verbose: Print more info if true.
        :type verbose: 'bool'
        """
        self._verbose = verbose
        self._reader = codecs.getreader("utf-8")
        self._dirstack = list()
        self._dirstack.append(('root', root_path if root_path else ""))

    def load(self, json_resource):
        """
        Load a resource and return JSON object.
        :param json_resource: URL or file path
        :type json_resource: 'str'
        :return: Loaded JSON object
        :rtype: JSON object
        """
        _, parent = self._dirstack[-1]
        effective_url = urljoin(parent, json_resource) \
            if parent else json_resource
        # noinspection PyBroadException
        try:
            if effective_url.startswith("file://"):
                effective_url = effective_url.replace(
                    "+", "/")
            if effective_url.find("://") == -1:
                effective_url = "file://" + effective_url
            with urllib.request.urlopen(effective_url) as fp:
                json_object = json.load(
                    self._reader(fp), object_pairs_hook=OrderedDict)
                self._dirstack.append(
                    (json_resource, effective_url))
        except Exception as e:
            if self._verbose:
                print("Treat {} as JSON value.".format(effective_url),
                      file=sys.stderr)
            try:
                json_object = json.loads(
                    json_resource, object_pairs_hook=OrderedDict)
            except json.JSONDecodeError:
                if type(json_resource) is str or \
                        type(json_resource) is Number:
                    json_object = json_resource
                else:
                    raise TemplateEngineException(
                        "Invalid template {}".format(json_resource))
            self._dirstack.append((json_resource, None))
        return json_object

    def unload(self, json_resource):
        """
        Unload the JSON resource
        :param json_resource: URL or file path
        :type json_resource: 'str'
        """
        source, _ = self._dirstack.pop()
        if source != json_resource:
            raise TemplateEngineException(
                "JSON resource loading is out of order")
