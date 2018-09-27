#!/usr/bin/env python
# -*- coding: utf-8 -*-


# IMPORT STANDARD LIBRARIES
import subprocess
import functools
import platform
import os

# IMPORT LOCAL LIBRARIES
from . import common


def get_git_command(
        base_url,
        system=platform.system(),
        distribution='-'.join(platform.dist()),
        architecture=common.get_architecture(),
    ):
    def _get_git_command(url):
        raise NotImplementedError('Need to write this')

    def _null(urls):
        raise RuntimeError('Urls "{urls}" were not reachable.'.format(urls=', '.join(urls)))

    chain = [
        [system, distribution, architecture],
        [system, architecture],
        [system],
    ]

    config_url = os.getenv('REZZURECT_GIT_REMOTE_BASE_URL', '')

    if config_url:
        base_url = config_url
    else:
        base_url, ending = common.split_url(base_url)

    urls = []
    for option in chain:
        url = '{base_url}-{option}{ending}'.format(
            base_url=base_url, option='-'.join(option), ending=ending)

        if common.is_url_reachable(url):
            return functools.partial(_get_git_command, url)

        urls.append(url)

    return functools.partial(_null, urls)


def get_git_root_url(root):
    if not os.path.isdir(root):
        return ''

    command = 'git -C "{root}" config --get remote.origin.url'.format(root=root)

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    stdout, stderr = process.communicate()
    stdout = stdout.strip()

    if not stderr and stdout:
        return stdout

    return ''
