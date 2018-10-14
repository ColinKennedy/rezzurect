#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A module which is used to show progress bars.

Mainly, when packages are installing, these classes and functions help us know
that processes are completing (and not just hanging).

'''

# IMPORT STANDARD LIBRARIES
from __future__ import division
import math
import io
import os


# Reference: https://stackoverflow.com/questions/3667865/python-tarfile-progress-output
class ProgressFileObject(io.FileIO):

    '''An object which is used in TAR callbacks to log extraction progress.

    This object prints every 10% of the extraction, to avoid being too spammy.

    '''

    def __init__(self, path, logger=None, *args, **kwargs):
        '''Create the object and store the given logger.

        Args:
            path (str):
                The absolute path to the TAR file to extract.
            logger (`logging.Logger` or NoneType, optional):
                Some logger to use to print the progress.
                If no logger is given, the progress messages are printed, instead.
                Default is None.
            *args (tuple):
                Optional args for this object.
            *kwargs (tuple):
                Optional args for this object.

        '''
        super(ProgressFileObject, self).__init__(path, *args, **kwargs)
        self._steps = set()
        self._total_size = os.path.getsize(path)
        self._logger = logger

    def read(self, size):
        '''Read the next few bytes of the archive and print the progress.'''
        percent = self.tell() / self._total_size
        tens = int(math.floor(percent * 10)) * 10  # 10, 20, 30 ... 100

        if tens not in self._steps:
            self._steps.add(tens)

            message = 'Overall process: {value} of {total}'.format(
                value=self.tell(), total=self._total_size)

            if self._logger:
                self._logger(message)
            else:
                print(message)

        return super(ProgressFileObject, self).read(size)
