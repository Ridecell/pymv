#!/usr/bin/env python2
"""
pymv is currently built on top of python "rope" library. However, rope has been determined to be an abandoned project
that is especially weak at Python3 support. pymv in its current state is therefore just a weak POC. The suggestion next
step for this project is to upgrade it to use the maintained python parser pybaron and re-implement all the move logic
from Rope.
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rope_vendored'))

import rope.base.project
from rope.base import libutils
from rope.refactor.move import MoveModule, create_move


class ExtraMoveChanges(object):
    """
    ExtraMoveChanges is all the hack code to extend past rope's weaknesses when doing a move without editing rope too
    much. It is not a proper rope.base.change.ChangeSet, just vaguely follows some of the rope changeset conventions.
    """

    def __init__(self, new_resource):
        desired_dir = os.path.dirname(new_resource.real_path)
        if os.path.exists(desired_dir):
            self._dir_to_create = None
        else:
            self._dir_to_create = desired_dir

    def get_description(self):
        if self._dir_to_create:
            return '\ncreate directory {}\n'.format(os.path.relpath(self._dir_to_create))
        return ''

    def execute(self):
        if self._dir_to_create:
            os.makedirs(self._dir_to_create)



def get_extra_changes(new_resource):
    return ExtraMoveChanges(new_resource)


def move(project_dir, src, dest, scoped_name=None, dry_run=False):
    project = rope.base.project.Project(project_dir)
    resource = libutils.path_to_resource(project, src)
    resource2 = libutils.path_to_resource(project, dest, type='folder' if resource.is_folder() else 'file')

    if scoped_name:
        offset = resource.read().index('%s' % scoped_name)
        mover = create_move(project, resource, offset)  # Uses GlobalMove
    else:
        mover = MoveModule(project, resource)

    rope_changeset = mover.get_changes(resource2)
    extra_changeset = get_extra_changes(resource2)
    if dry_run:
        print(str(rope_changeset.get_description()))
        print(str(extra_changeset.get_description()))
    else:
        extra_changeset.execute()
        project.do(rope_changeset)


def main():
    arg_parser = argparse.ArgumentParser(description='Move python files and folders, automatically updating import '
                                                     'statements in dependent files.')
    arg_parser.add_argument('source_path', type=str)
    arg_parser.add_argument('destination_path', type=str)
    arg_parser.add_argument('scoped_global_variable', type=str, nargs='?', default=None,
                            help='Provide a Global variable/class/function name in source file to move to destination.'
                                 ' Allows for greater granularity when moving overscoped modules that need to be split '
                                 'into 2 (or more) modules')
    arg_parser.add_argument('--dry-run', action='store_true', dest='dry_run')
    arg_parser.add_argument('--project-root-directory', type=str, default='.', dest='project_dir',
                            help='Root directory of the python project in which the files are being moved. This defines'
                                 ' the scope for which to search for affected import statements.')
    args = arg_parser.parse_args(sys.argv[1:])

    if args.project_dir != '.':
        raise NotImplementedError('Support for a --project-root-directory other than the current working directory '
                                  '(specified as ".") is pending.')
        # Something doesn't work correctly with a different root directory, no idea why. It's not relative to the other
        # path arguments.

    move(args.project_dir, args.source_path, args.destination_path, scoped_name=args.scoped_global_variable,
         dry_run=args.dry_run)


if __name__ == '__main__':
    main()
