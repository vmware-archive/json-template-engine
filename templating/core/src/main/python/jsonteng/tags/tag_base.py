# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

import abc

from ..exception import TemplateEngineException


class TagBase(object):
    """
    Base class of tag classes.
    """
    __metaclass__ = abc.ABCMeta
    TAG_NONE = type('TagNone', (), {})()

    def __init__(self, tag_resolver):
        """
        Base tag constructor.
        :param tag_resolver: Rag resolver to be used by the tag.
        """
        self._tag_resolver = tag_resolver

    @abc.abstractmethod
    def process(self, tag_tokens, binding_data_list):
        """
        Process a tag.
        :param tag_tokens: Tag arguments.
        :type tag_tokens: 'list'
        :param binding_data_list: Binding data used during the processing.
        :type binding_data_list: 'list'
        :return: JSON object
        :rtype: JSON object
        """
        raise NotImplementedError

    @staticmethod
    def safe_eval(expr):
        """
        A safe eval that is limited to simple expressions.
        :param expr: A Python boolean expression
        :type expr: 'str'
        :return: result of expression evaluation
        :rtype: 'bool'
        """
        result = eval(expr, {"__builtins__": None}, {})
        if not isinstance(result, bool):
            raise TemplateEngineException(
                "Expression {} is not a boolean type".format(expr))
        return result
