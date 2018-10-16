#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
import argparse

# IMPORT THIRD-PARTY LIBRARIES
from rez.utils.graph_utils import view_graph
from rez import build_process_
from rez import build_system
from rez import exceptions
from rez import packages_


def build(path):
    package = packages_.get_developer_package(path)

    # TODO : Consider supporting variants
    opts = argparse.Namespace(
        prefix=None,
        process='local',
        clean=False,
        scripts=False,
        install=True,
        variants=None,
    )

    build_system_ = build_system.create_build_system(
        path,
        package=package,
        buildsys_type=None,
        opts=opts,
        write_build_scripts=opts.scripts,
        verbose=True,
        build_args=[],
        child_build_args=[],
    )

    # create and execute build process
    builder = build_process_.create_build_process(
        opts.process,
        path,
        package=package,
        build_system=build_system_,
        verbose=True,
    )

    try:
        builder.build(
            install_path=opts.prefix,
            clean=opts.clean,
            install=opts.install,
            variants=opts.variants,
        )
    except exceptions.BuildContextResolveError as err:
        LOGGER.exception('Path "%s" failed to build.', path)

        if opts.fail_graph:
            if err.context.graph:
                graph = err.context.graph(as_dot=True)
                view_graph(graph)
            else:
                LOGGER.error('the failed resolve context did not generate a graph.')

        raise
