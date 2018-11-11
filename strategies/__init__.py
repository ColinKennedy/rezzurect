#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Add `urllib.parse` to `six` so that it works for Python 2 and Python 3.'''

# IMPORT LOCAL LIBRARIES
from ..vendors import six


six.add_move(six.MovedModule('urlparse', 'urlparse', 'urllib.parse'))
