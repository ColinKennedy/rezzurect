#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
from __future__ import division
import tarfile
import math
import io
import os


class ProgressFileObject(io.FileIO):
    def __init__(self, path, logger=None, *args, **kwargs):
        super(ProgressFileObject, self).__init__(path, *args, **kwargs)
        self._steps = set()
        self._total_size = os.path.getsize(path)
        self._logger = logger

    def read(self, size):
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


def get_file_progress_class(function):
    class FileProgressFileObject(tarfile.ExFileObject):
        def read(self, size, *args):
            function(self.name, self.position, self.size)
            return super(FileProgressFileObject, self).read(size, *args)

    return FileProgressFileObject


def on_progress(filename, position, total_size, logger=None):
    message = '{filename}: {position} of {total_size}'.format(
        filename=filename, position=position, total_size=total_size)

    if logger:
        logger(message)
    else:
        print(message)
