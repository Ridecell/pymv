#!/usr/bin/env python2
import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rope_vendored'))

import rope.base.project
from rope.base import libutils
from rope.refactor.move import MoveModule


PROJECT_DIR = '.'


def move(project, src, dest, dry_run=False):
    project = rope.base.project.Project(PROJECT_DIR)
    resource = libutils.path_to_resource(project, src)
    resource2 = libutils.path_to_resource(project, dest, type='folder' if resource.is_folder() else 'file')

    mover = MoveModule(project, resource)

    changeset = mover.get_changes(resource2)
    if dry_run:
        print(str(changeset.get_description()))
    else:
        project.do(changeset)


def main():
    arg_parser = argparse.ArgumentParser(description='Move python files and folders, automatically updating import '
                                                     'statements in dependent files.')
    arg_parser.add_argument('source_path', type=str)
    arg_parser.add_argument('destination_path', type=str)
    arg_parser.add_argument('--dry-run', action='store_true', dest='dry_run')
    args = arg_parser.parse_args(sys.argv[1:])

    # project_dir = os.path.abspath(PROJECT_DIR)
    # source_path = os.path.join(PROJECT_DIR, args.source_path)
    # destination_path = os.path.join(PROJECT_DIR, args.destination_path)

    move(PROJECT_DIR, args.source_path, args.destination_path, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
