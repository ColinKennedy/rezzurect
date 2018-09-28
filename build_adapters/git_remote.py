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
    def _get_git_command(url, path, silent=False):
        # '''Clone the given git url to the given folder path.

        # Args:
        #     url (str):
        #         Some git URL that the user has access to.
        #     path (str):
        #         The absolute path to a folder on-disk where url will be cloned into.
        #     silent (`bool`, optional):
        #         If True, do not print anything and just clone the repository.
        #         If False, print out the percent completion to the user during cloning.
        #         Default is False.

        # Raises:

        # '''
        # TODO : I have to do something about empty folders. The function fails
        # if there are any files in `path` when this process runs.
        #
        process = subprocess.Popen(
            ['git', 'clone', '--progress', url, path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        # TODO : Also, it looks like sometimes line prints tons of empty newlines.
        #        Figure out how to prevent that.
        if silent:
            # Read the un-buffered output so that the user can see the git clone happening
            fd = process.stdout.fileno()
            while process.returncode is None:
                line = os.read(fd, 1000)   # Read a bit of data
                print(line)

    def _null(urls):
        '''Raise an error with these URLs.'''
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
    '''Check if the URL is a git repository.

    Args:
        url (str):
            Some git url, such as root@192.168.0.0:/srv/git/whatever.git or
            https://www.github.com/username/reponame.git or any other git syntax.

    Returns:
        bool: If the url is reachable.

    '''
    process = subprocess.Popen(
        'git ls-remote {url}'.format(url=url),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    stdout, stderr = process.communicate()

    return not stderr and stdout


def get_git_root_url(root):
    '''Find the URL for the git repo at the given file path.

    Args:
        root (str): The absolute path to a directory on-disk.

    Returns:
        str: The found git remote URL, if any.

    '''
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
