#!/usr/bin/env python
# -*- coding: utf-8 -*-


# IMPORT STANDARD LIBRARIES
import subprocess
import functools
import platform
import os

# IMPORT LOCAL LIBRARIES
from .. import common


def get_git_command(
        base_url,
        path='',
        system=platform.system(),
        distribution='-'.join(platform.dist()),
        architecture=common.get_architecture(),
    ):
    def _get_git_command(url, path):
        process = subprocess.Popen(
            ['git', 'clone', '--progress', url, path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        # Read the un-buffered output so that the user can see the git clone happening
        fd = process.stdout.fileno()
        while process.returncode is None:
            line = os.read(fd, 1000)   # Read a bit of data
            print(line)

    def _null(urls):
        raise RuntimeError('Urls "{urls}" were not reachable.'.format(urls=', '.join(urls)))

    chain = [
        [system, distribution, architecture],
        [system, architecture],
        [system],
    ]

    # TODO : Maybe add this environment information back in
    # config_url = os.getenv('REZZURECT_GIT_REMOTE_BASE_URL', '')

    # if config_url:
    #     base_url = config_url
    # else:
    #     base_url, ending = common.split_url(base_url)

    base_url, ending = common.split_url(base_url)

    urls = []
    for option in chain:
        url = '{base_url}-{option}{ending}'.format(
            base_url=base_url,
            option='-'.join([str(item) for item in option]),
            ending=ending,
        )

        if is_git_remote_reachable(url):
            return functools.partial(_get_git_command, url, path)

        urls.append(url)

    return functools.partial(_null, urls)


def is_git_remote_reachable(url):
    process = subprocess.Popen(
        'git ls-remote {url}'.format(url=url),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    stdout, stderr = process.communicate()

    return not stderr and stdout


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
