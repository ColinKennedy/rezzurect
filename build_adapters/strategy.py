#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
import copy


STRATEGIES = []


def get_strategies():
    return copy.copy(STRATEGIES)


def register_strategy(name, function, priority=False):
    if priority:
        STRATEGIES.insert(0, (name, function))
    else:
        STRATEGIES.append((name, function))
