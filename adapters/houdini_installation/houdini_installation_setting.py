#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An adapter for running a Houdini Rez package.'''

# IMPORT STANDARD LIBRARIES
import tempfile
import os

# IMPORT LOCAL LIBRARIES
from .. import common_setting
from . import helper


class CommonHoudiniSettingAdapter(common_setting.BaseAdapter):

    '''An adapter which is used to set up common settings / aliases for Houdini.'''

    name = 'houdini'

    @staticmethod
    def get_executable_command():
        '''Get the command that is run as the "main" alias.

        Raises:
            EnvironmentError: If the stored version is incorrect.

        Returns:
            str: The found command for Houdini's version.

        '''
        return 'houdini'

    def execute(self):
        '''Add aliases and environment variables to the package on-startup.'''
        super(CommonHoudiniSettingAdapter, self).execute()

        # Note: Aliases and environment variable settings added here will be
        #       added to all Houdini versions in all OSes.

        root = self.env.INSTALL_ROOT.get()

        # houdini_setup file :START:
        # Make sure that Houdini knows where it is installed to
        self.env.HFS = root

        self.env.H = self.env.HFS.get()
        self.env.HB = os.path.join(self.env.H.get(), 'bin')
        self.env.HDSO = os.path.join(self.env.H.get(), 'dsolib')
        self.env.HD = os.path.join(self.env.H.get(), 'demo')
        self.env.HH = os.path.join(self.env.H.get(), 'houdini')
        self.env.HHC = os.path.join(self.env.HH.get(), 'config')
        self.env.HT = os.path.join(self.env.H.get(), 'toolkit')
        self.env.HSB = os.path.join(self.env.HH.get(), 'sbin')

        self.env.TEMP = tempfile.gettempdir()

        # TODO : Need JAVA_HOME
        library = os.getenv('LD_LIBRARY_PATH', '')

        if library:
            self.env.LD_LIBRARY_PATH = (os.pathsep).join([self.env.HDSO.get(), library])

        # TODO : Add PATH stuff from JAVA_HOME

        major, minor, patch = helper.get_version_parts(self.version)

        self.env.HOUDINI_MAJOR_RELEASE = int(major)
        self.env.HOUDINI_MINOR_RELEASE = int(minor)
        self.env.HOUDINI_BUILD_VERSION = int(patch)

        self.env.HOUDINI_VERSION = '.'.join([major, minor, patch])

        # TODO : remove, maybe
        self.env.HOUDINI_BUILD_KERNEL = '2.6.32-573.3.1.el6.x86_64'
        self.env.HOUDINI_BUILD_PLATFORM = 'Red Hat Enterprise Linux Workstation release 6.7 (Santiago)'
        self.env.HOUDINI_BUILD_COMPILER = '4.8.2'
        self.env.HOUDINI_BUILD_LIBC = 'glibc 2.12'

        self.env.HIH = os.path.join(
            os.getenv('HOME', ''),
            'houdini${major}.${minor}'.format(major=major, minor=minor),
        )

        self.env.HIS = self.env.HH.get()
        # houdini_setup file :END:

        self.env.CMAKE_PREFIX_PATH.append(os.path.join(root, 'toolkit', 'cmake'))

        self.env.HOUDINI_MENU_PATH = os.path.join(root, 'houdini')

        self.env.PATH.append(os.path.join(root, 'bin'))
        self.env.PATH.append(os.path.join(root, 'houdini', 'sbin'))

        self.env.PYTHONPATH.append(os.path.join(root, 'houdini', 'python2.7libs'))
        self.env.PYTHONPATH.append(os.path.join(root, 'python', 'lib', 'python2.7', 'site-packages'))
