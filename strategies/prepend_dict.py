#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A custom, OrderedDict which lets you add key/value pairs to its front.'''

# IMPORT STANDARD LIBRARIES
import collections


# Reference: https://stackoverflow.com/questions/16664874
class PrependOrderedDict(collections.OrderedDict):

    '''A custom, OrderedDict which lets you add key/value pairs to its front.'''

    def prepend(self, key, value, dict_setitem=dict.__setitem__):
        '''Add the given key and balue to the beginning of this instance.

        Args:
            key:
                The hashable object which will be used to index `value`.
            value:
                The object to store for `key`.
            dict_setitem (`callable[dict, object, object]`, optional):
                A function that will add the key/value pair.

        '''
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
