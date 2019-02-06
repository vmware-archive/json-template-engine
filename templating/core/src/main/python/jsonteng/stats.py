# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

from collections import OrderedDict


class Stats(object):
    """
    `Stats` collects stats for how many times a parameter is expanded.
    """
    def __init__(self):
        """
        Construct Stats.
        """
        self._parameter_map = OrderedDict()

    def update_stats(self, parameter):
        """
        Updated the counter of the parameter usage
        :param parameter:
        :return:
        """
        if parameter in self._parameter_map:
            self._parameter_map[parameter] += 1
        else:
            self._parameter_map[parameter] = 1

    def get_stats(self):
        """
        Get the stats object
        :return: Stats object
        :rtype: 'Stats'
        """
        return self._parameter_map

    def clear(self):
        """
        Reset the stats counters.
        """
        self._parameter_map.clear()
