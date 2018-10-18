#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A module which is used to show progress bars.

Mainly, when packages are installing, these classes and functions help us know
that processes are completing (and not just hanging).

'''

# TODO : Rename this module to 'progresslog'
# IMPORT STANDARD LIBRARIES
from __future__ import division
import math
import io
import os


# Reference: https://stackoverflow.com/questions/3667865/python-tarfile-progress-output
class TarProgressFile(io.FileIO):

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
        super(TarProgressFile, self).__init__(path, *args, **kwargs)
        self._steps = set()
        self._total_size = os.path.getsize(path)
        self._logger = logger

    def read(self, size):
        '''Read the next few bytes of the archive and print the progress.'''
        percent = self.tell() / self._total_size
        tens = int(math.floor(percent * 10)) * 10  # 10, 20, 30 ... 100

        if tens not in self._steps:
            self._steps.add(tens)

            message = 'Overall process: %d of %d'

            if self._logger:
                self._logger(message, self.tell(), self._total_size)
            else:
                print(message % self.tell(), self._total_size)

        return super(TarProgressFile, self).read(size)


class UrllibProgress(object):

    '''A class which prints the progress of downloaded files from urllib.

    Example:
        >>> from six.moves import urllib
        >>> path = "https://www.example.com/download.pdf"
        >>> urllib.request.urlretrieve(
        ...     path,
        ...     '/home/selecaoone/temp/test.tgz',
        ...     reporthook=UrllibProgress().download_progress_hook,
        ... )

    '''

    def __init__(self, logger=None):
        '''Create the instance and store variables for logging and memory.

        Args:
            logger (callable[str, *args]):
                A function that is meant to print or log the progress of this
                instance. If nothing is given, the progress
                will be printed, instead. Default is None.

        '''
        super(UrllibProgress, self).__init__()
        self._steps = set()
        self._logger = logger

    def download_progress_hook(self, count, block, total):
        '''Print out the progress to the user.

        Args:
            count (int): The number of bytes already downloaded.
            block (int): The size of each download block.
            total (int): The full number of bytes to download.

        '''
        percent = count / total
        tens = int(math.floor(percent * 10)) * 10  # 10, 20, 30 ... 100

        if tens not in self._steps:
            self._steps.add(tens)

            message = 'Overall process: %d of %d'

            if self._logger:
                self._logger(message, count, total)
            else:
                print(message % (count, total))
