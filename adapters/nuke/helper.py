#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Any information that is used between one or more adapter modules.'''

# IMPORT STANDARD LIBRARIES
import re


VERSION_PARSER = re.compile(r'(?P<major>\d+).(?P<minor>\d+)v(?P<patch>\d+)')
