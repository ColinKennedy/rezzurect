#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A module that manages rezzurect and Rez package distribution.'''

# IMPORT STANDARD LIBRARIES
from distutils import dir_util
import subprocess
import functools
import getpass
import glob
import imp
import os
import os

# IMPORT THIRD-PARTY LIBRARIES
from rez.vendor.version import version as rez_version
from rez import package_maker__ as package_maker
from rez import resolved_context
from rez import exceptions
import rezzurect


_DEFAULT_VALUE = object()
PACKAGE_EXCEPTIONS = (
    # This happens if no versions of a package have been installed yet
    exceptions.PackageFamilyNotFoundError,

    # This happens if a package has at least one installed version but it is
    # not the version that you trying to query in `packages`
    #
    exceptions.PackageNotFoundError,
)


def copy_rezzurect_to(path):
    '''Copy rezzurect into the given directory.

    rezzurect needs to be available for import when a package is executed so
    this function should be run (ideally always but only) once on-build.

    Args:
        path (str): The absolute path to a package's python folder.

    '''
    root = os.path.dirname(os.path.realpath(rezzurect.__file__))
    name = os.path.basename(root)  # Should always just be 'rezzurect'

    if not os.path.isdir(path):
        os.makedirs(path)

    destination = os.path.join(path, name)
    dir_util.copy_tree(root, destination)


def sort_by_version(version, item):
    base = os.path.basename(item)

    if base == version:
        return 1

    return 2


def get_version_path(root, package, version=''):
    if not version and '-' in package:
        package, version = package.split('-')

    path = os.path.join(root, package)

    versions = [path_ for path_ in glob.glob(os.path.join(path, '*'))
                if os.path.isdir(path_)]
    versions = sorted(versions, key=functools.partial(sort_by_version, version))

    try:
        return versions[0]
    except IndexError:
        return ''


def get_package_definition(root, package, version=''):
    if not version and '-' in package:
        # Note: This section assumes that the package name NEVER contains a "-"
        #       (which, as far as I know, is enforced by Rez everywhere)
        #
        items = package.split('-')
        package = items[0]
        version = '-'.join(items[1:])

    version_path = get_version_path(root, package, version=version)

    if not version_path:
        raise EnvironmentError(('No version could be found'))

    package_path = os.path.join(version_path, 'package.py')

    if not os.path.isfile(package_path):
        raise EnvironmentError('Package path "{package_path}" does not exist.'
                               ''.format(package_path=package_path))

    try:
        return imp.load_source(
            'rez_{package}_definition'.format(package=package),
            package_path,
        )
    except ImportError:
        return


def make_package(definition, build_path):
    with package_maker.make_package(definition.name, build_path, skip_existing=True) as pkg:
        mirror('authors', definition, pkg, default=[getpass.getuser()])
        mirror('commands', definition, pkg)
        mirror('description', definition, pkg)
        mirror('help', definition, pkg, default='')
        mirror('name', definition, pkg)
        mirror('requires', definition, pkg, default=[])
        mirror('timestamp', definition, pkg)
        mirror('tools', definition, pkg)
        # mirror('uuid', definition, pkg, default=str(uuid.uuid4()))
        pkg.version = rez_version.Version(definition.version)

    return pkg


def build_package(definition, root):
    root = os.path.dirname(definition.__file__)
    commands = [
        'cd "{root}" && rez-build --install'.format(root=root),
    ]

    process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (_, stderr) = process.communicate()

    return stderr


def build_package_recursively(root, package, version='', build_path=''):
    definition = get_package_definition(root, package, version)

    if not definition:
        raise RuntimeError('No definition file could be loaded.')

    pkg = make_package(definition, build_path)
    requirements = pkg.get_package().requires

    if not requirements:
        stderr = build_package(definition, build_path)

        if not stderr:
            return

        raise RuntimeError('Definition "{definition}" failed to build. Stderr "{stderr}"'
                           ''.format(definition=definition.__file__, stderr=stderr))

    for requirement in requirements:
        try:
            resolved_context.ResolvedContext([requirement])
        except PACKAGE_EXCEPTIONS:
            build_package_recursively(root, str(requirement), build_path=build_path)


def mirror(attribute, module, package, default=_DEFAULT_VALUE):
    try:
        value = getattr(module, attribute)
    except AttributeError:
        if default == _DEFAULT_VALUE:
            return

        value = default

    setattr(package, attribute, value)


def install(package, root, build_path, version=''):
    package = package.split('-')[0]

    try:
        # Request the specific package-version
        resolved_context.ResolvedContext(['{}-{}'.format(package, version)])
    except PACKAGE_EXCEPTIONS:
        build_package_recursively(root, package, version=version, build_path=build_path)


if __name__ == '__main__':
    main()
