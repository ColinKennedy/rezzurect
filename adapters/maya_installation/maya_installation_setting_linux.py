#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An adapter for running a Maya Rez package in Linux.'''

# IMPORT STANDARD LIBRARIES
import glob
import os

# IMPORT LOCAL LIBRARIES
from . import maya_installation_setting
from ...utils import config_helper
from . import helper


class LinuxMayaSettingAdapter(maya_installation_setting.CommonMayaSettingAdapter):

    '''An adapter which is used to set up common settings / aliases for Maya.'''

    def get_preinstalled_executables(self):
        '''Get a list of possible pre-installed executable Maya files.

        Raises:
            RuntimeError:
                If we can't get version information from the stored version then
                this function will fail. Normally though, assuming this adapter
                was built correctly, this shouldn't occur.

        Returns:
            str: The absolute path to a Maya executable.

        '''
        return helper.get_preinstalled_linux_executables(self.version)

    def _get_python_site_packages_folder(self):
        '''str: Find the absolute path to the Python version that comes with Maya.'''
        # Note: Throw the path into a garbage environment variable so that we
        #       can expand "{root}" to its actual path
        #
        self.env.__PYTHON_SITE_PACKAGES_FOLDER.set(  # pylint: disable=protected-access
            '{{root}}/install/usr/autodesk/maya{version}/lib/python*/site-packages'.format(
            version=self.version,
        ))

        return list(glob.glob(self.env.__PYTHON_SITE_PACKAGES_FOLDER.value()))[0]  # pylint: disable=protected-access

    def execute(self):
        '''Add aliases and environment variables to the package on-startup.'''
        super(LinuxMayaSettingAdapter, self).execute()

        major = helper.get_version_parts(self.version)

        root = '{{root}}/{install}/usr/autodesk/maya{major}' \
            ''.format(install=config_helper.INSTALL_FOLDER_NAME, major=major)

        self.env.PATH.prepend(root + '/bin')

        self.env.MAYA_VERSION.set(self.version)
        self.env.MAYA_MAJOR_VERSION.set(major)
        self.env.MAYA_LOCATION.set(root)
        self.env.LD_LIBRARY_PATH.append(root + '/lib')

        self.env.PYTHONPATH.append(self._get_python_site_packages_folder())

        # TODO : Finish. Actually, do I actually even need this?
        # self.env.AUTODESK_ADLM_THINCLIENT_ENV.set('{root}/AdlmThinClientCustomEnv.xml')
        # self.env.MAYA_COLOR_MANAGEMENT_POLICY_FILE.set('{root}/MayaNoColorManagement.xml')
