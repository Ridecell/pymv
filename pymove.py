import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rope_vendored'))

import rope.base.project
from rope.base import libutils
from rope.refactor.move import MoveModule


cwd = '.'
src = sys.argv[1]
dest = sys.argv[2]

# cwd = os.path.abspath(cwd)
# src = os.path.join(cwd, src)
# dest = os.path.join(cwd, dest)

print(repr((cwd, src, dest)))

project = rope.base.project.Project(cwd)
resource = libutils.path_to_resource(project, src)
resource2 = libutils.path_to_resource(project, dest, type='folder' if resource.is_folder() else 'file')

mover = MoveModule(project, resource)

print(str(mover.get_changes(resource2).get_description()))

# project.do(mover.get_changes(destination))
