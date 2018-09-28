#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
import collections
import os


class PrependOrderedDict(collections.OrderedDict):
    def prepend(self, key, value, dict_setitem=dict.__setitem__):
        # Reference: https://stackoverflow.com/questions/16664874
        root = self._OrderedDict__root
        first = root[1]

        if key in self:
            link = self._OrderedDict__map[key]
            link_prev, link_next, _ = link
            link_prev[1] = link_next
            link_next[0] = link_prev
            link[0] = root
            link[1] = first
            root[1] = first[0] = link
        else:
            root[1] = first[0] = self._OrderedDict__map[key] = [root, first, key]
            dict_setitem(self, key, value)


STRATEGIES = PrependOrderedDict()


def get_strategies():
    preference = os.getenv('REZZURECT_STRATEGY_ORDER', '')
    order = []

    if not preference:
        return list(STRATEGIES.items())

    for item in preference.split(','):
        item = item.strip()

        if item:
            order.append(item)

    return [(item_, STRATEGIES[item_]) for item_ in order]


def register_strategy(name, function, priority=False):
    if priority:
        STRATEGIES.prepend(name, function)
    else:
        STRATEGIES[name] = function
