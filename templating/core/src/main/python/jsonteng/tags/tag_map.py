# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

from collections import OrderedDict

from .at_tag import AtTag
from .for_each_tag import ForEachTag
from .exists_tag import ExistsTag
from .len_tag import LenTag
from .one_of_tag import OneOfTag


_tag_class_map = {
    AtTag.name: AtTag,
    ExistsTag.name: ExistsTag,
    ForEachTag.name: ForEachTag,
    LenTag.name: LenTag,
    OneOfTag.name: OneOfTag
}


def get_tag_map(tag_resolver):
    """
    Return a tag map of known tags.
    :param tag_resolver: Tag resolved used by tags.
    :type tag_resolver: 'TagResolver'
    :return: A map of tags.
    :rtype: 'dict'
    """
    tag_map = OrderedDict()
    for tag_name, tag in _tag_class_map.items():
        tag_map[tag_name] = tag(tag_resolver)
    return tag_map


def add_tag(tag_name, tag):
    """
    Add a tag to the tag collection.
    :param tag_name: Tag name.
    :type tag_name: 'str'
    :param tag: Tag class.
    :type tag: 'TagBase'
    :return:
    """
    _tag_class_map[tag_name] = tag


def get_tag_names():
    """
    Get all tag names.
    :return: Tag names.
    :rtype: 'list'
    """
    return _tag_class_map.keys()
