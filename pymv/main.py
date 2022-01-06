import argparse
import glob
import os
import re
import sys

import rope.base.project
from rope.base import libutils
from rope.refactor.move import MoveModule, create_move


class ExtraMoveChanges(object):
    """
    ExtraMoveChanges is all the hack code to extend past rope's weaknesses when doing a move without editing rope too
    much. It is not a proper rope.base.change.ChangeSet, just vaguely follows some of the rope changeset conventions.
    """

    def __init__(self, new_resource):
        self._destination_file = None
        self._stack = []
        if not new_resource.exists():
            if new_resource.is_folder():
                parent = new_resource
            else:
                parent = new_resource.parent

            while not parent.exists():
                self._stack.insert(0, parent)
                parent = parent.parent

    def get_description(self):
        desc = []
        for s in self._stack:
            desc.append('\ncreate module {}\n'.format(os.path.dirname(s.real_path)))
        if self._destination_file:
            desc.append('\ncreate file {}\n'.format(self._destination_file.real_path))
        return desc if desc else ''

    def execute(self):
        for s in self._stack:
            s.create()
            s.create_file('__init__.py')
        if self._destination_file and not self._destination_file.exists():
            self._destination_file.create()

    def add_destination_file(self, new_resource):
        self._destination_file = new_resource

    def cleanup(self):
        if self._destination_file:
            os.unlink(self._destination_file.real_path)
        for s in reversed(self._stack):
            os.unlink(os.path.join(s.real_path, '__init__.py'))
            os.rmdir(s.real_path)


def get_extra_changes(new_resource):
    return ExtraMoveChanges(new_resource)


def move(project_dir, src, dest, scoped_name=None, dry_run=False):
    [os.unlink(p) for p in  glob.glob('**/*.pyc')]
    project = rope.base.project.Project(project_dir)
    resource = libutils.path_to_resource(project, src)
    resource2 = libutils.path_to_resource(project, dest, type='folder' if resource.is_folder() else 'file')
    extra_changeset = get_extra_changes(resource2)

    if scoped_name:
        if resource.is_folder():
            raise RuntimeError('If global scoped provided, resource must be a file')
        offset = re.search(f'\\b{scoped_name}\\b', resource.read()).span()[0]
        # TODO: Get the offset from the AST, don't try to parse python with regex
        extra_changeset.add_destination_file(resource2)
        extra_changeset.execute()
        mover = create_move(project, resource, offset)  # Uses MoveGlobal
    else:
        if resource2.exists():
            raise RuntimeError(f'Destination {"folder" if resource2.is_folder() else "file"} already exists. Aborting.')
        extra_changeset.execute()
        mover = MoveModule(project, resource)

    rope_changeset = mover.get_changes(resource2)
    if dry_run:
        print(str(rope_changeset.get_description()))
        print(str(extra_changeset.get_description()))
        extra_changeset.cleanup()
    else:
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
