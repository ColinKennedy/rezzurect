#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A module that manages rezzurect and Rez package distribution.'''

# IMPORT STANDARD LIBRARIES
from distutils import dir_util
import functools
import getpass
import logging
import glob
import imp
import os

# IMPORT THIRD-PARTY LIBRARIES
from rez.vendor.version import version as rez_version
from rez import package_maker__ as package_maker
from rez import resolved_context
from rez import exceptions
import rezzurect

# IMPORT LOCAL LIBRARIES
from .utils import multipurpose_helper


_DEFAULT_VALUE = object()
PACKAGE_EXCEPTIONS = (
    # This happens if no versions of a package have been installed yet
    exceptions.PackageFamilyNotFoundError,

    # This happens if a package has at least one installed version but it is
    # not the version that you trying to query in `packages`
    #
    exceptions.PackageNotFoundError,
)
LOGGER = logging.getLogger('rezzurect.manager')


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
    '''int: If the given version is found, send it to the front.

    Sort the other non-matching items alphabetically.

    '''
    base = os.path.basename(item)

    if base == version:
        return 1

    return 2


def get_version_path(root, package, version=''):
    '''Get the absolute path to a package's version-install folder.

    Args:
        root (str):
            The absolute path to where all installed packages live.
        package (str):
            The name of the package to get the version path of.
        version (str, optional):
            The specific version to get the path of. If no version is given,
            the latest version is used, instead. Default: "".

    Returns:
        str: The found path, if any.

    '''
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
    '''Import a Rez package's package.py file as a Python module.

    Args:
        root (str):
            The absolute path to where all installed packages2live.
        package (str):
            The name of the package to get the version path of.
        version (str, optional):
            The specific version to get the path of. If no version is given,
            the latest version is used, instead. Default: "".

    Raises:
        EnvironmentError:
            If the given package has missing or incomplete data.
            This is usually an indicator of a much bigger problem that requires
            intervention of a developer so, instead of returning early, we
            raise an exception instead.

    Returns:
        module or NoneType: The found package.py file, if any.

    '''
    if not version and '-' in package:
        # Note: This section assumes that the package name NEVER contains a "-"
        #       (which, as far as I know, is enforced by Rez everywhere)
        #
        items = package.split('-')
        package = items[0]
        version = '-'.join(items[1:])

    version_path = get_version_path(root, package, version=version)

    if not version_path:
        raise EnvironmentError('No version could be found')

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
    '''Install our predefined Rez package.py file to a separate build folder.

    Args:
        definition (module): The package.py to make a copy to into `build_path`.
        build_path (str): The absolute path to install `definition` to.

    Returns:
        `rez.package_maker__.PackageMaker`: The created package.

    '''
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


def build_package_recursively(root, package, version='', build_path=''):
    '''Build a package by building its required packages recursively.

    Basically the logic goes like this:
        - Evaluate if a package has been built. If it has been built, do nothing.
        - If a package has no requirements, build it.
        - If a package has requirements and that requirement isn't installed,
          then evaluate and build it, too.
        - Repeat until all packages are built.

    Raises:
        RuntimeError:
            If a package was build incorrectly or
            if an attempt to build a package failed.

    '''
    def build_definition(definition, build_path):
        try:
            multipurpose_helper.build(
                os.path.dirname(definition.__file__),
                install_path=build_path,
            )
        except Exception:
            # TODO : Consider deleting the contents of
            #        `os.path.dirname(definition.__file__)`
            #        before erroring out, here
            #
            message = 'Definition "%s" failed to build.'
            LOGGER.exception(message, definition.__file__)
            raise RuntimeError(message % definition.__file__)

    LOGGER.debug('Building package "%s".', package)

    definition = get_package_definition(root, package, version)

    if not definition:
        raise RuntimeError('No definition file could be loaded.')

    pkg = make_package(definition, build_path)
    requirements = pkg.get_package().requires

    for requirement in requirements:
        try:
            resolved_context.ResolvedContext([requirement])
        except PACKAGE_EXCEPTIONS:
            requirement_package, requirement_version = str(requirement).split('-')

            build_package_recursively(
                root, requirement_package, requirement_version, build_path=build_path)

    # Now that all of the requirements are installed, install this package
    build_definition(definition, build_path)


def mirror(attribute, module, package, default=_DEFAULT_VALUE):
    '''Set set an attribute from one object onto another, if needed.

    Args:
        attribute (str): The attribute to mirror.
        module (object): The object which will be used to mirror `attribute`.
        package (object): The object to mirror `attribute` onto.
        default (object, optional):
            A value to use if `attribute` does not exist. If no default is
            specified then `attribute` is not mirrored.

    '''
    try:
        value = getattr(module, attribute)
    except AttributeError:
        if default == _DEFAULT_VALUE:
            return

        value = default

    setattr(package, attribute, value)


def install(package, root, build_path, version=''):
    '''Install a given package into `build_path`.

    Args:
        root (str):
            The absolute path to where all installed packages live.
        build_path (str):
            The absolute path to install the package to.
        version (str, optional):
            The specific version to get the path of. If no version is given,
            the latest version is used, instead. Default: "".

    '''
    package = package.split('-')[0]

    LOGGER.debug('Installing "%s".', package)

    try:
        # Request the specific package-version
        resolved_context.ResolvedContext(['{}-{}'.format(package, version)])
    except PACKAGE_EXCEPTIONS:
        build_package_recursively(root, package, version=version, build_path=build_path)
