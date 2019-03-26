from rope.base import (pyobjects, codeanalyze, exceptions, pynames,
                       taskhandle, evaluate, worder, libutils)
from rope.base.change import ChangeSet, ChangeContents, MoveResource
from rope.refactor import importutils, rename, occurrences, sourceutils, \
    functionutils

from rope.refactor.move import _MoveTools


class MoveModule(object):
    """For moving modules and packages"""

    def __init__(self, project, resource):
        self.project = project
        if not resource.is_folder() and resource.name == '__init__.py':
            resource = resource.parent
        if resource.is_folder() and not resource.has_child('__init__.py'):
            raise exceptions.RefactoringError(
                'Cannot move non-package folder.')
        dummy_pymodule = libutils.get_string_module(self.project, '')
        self.old_pyname = pynames.ImportedModule(dummy_pymodule,
                                                 resource=resource)
        self.source = self.old_pyname.get_object().get_resource()
        if self.source.is_folder():
            self.old_name = self.source.name
        else:
            self.old_name = self.source.name[:-3]
        self.tools = _MoveTools(self.project, self.source,
                                self.old_pyname, self.old_name)
        self.import_tools = self.tools.import_tools

    def get_changes(self, dest, resources=None,
                    task_handle=taskhandle.NullTaskHandle()):
        if resources is None:
            resources = self.project.get_python_files()
        if dest is None:
        #if dest is None or not dest.is_folder():
            raise exceptions.RefactoringError(
                'Move destination for modules should be packages.')
        return self._calculate_changes(dest, resources, task_handle)

    def _calculate_changes(self, dest, resources, task_handle):
        changes = ChangeSet('Moving module <%s>' % self.old_name)
        job_set = task_handle.create_jobset('Collecting changes',
                                            len(resources))
        for module in resources:
            job_set.started_job(module.path)
            if module == self.source:
                self._change_moving_module(changes, dest)
            else:
                source = self._change_occurrences_in_module(dest,
                                                            resource=module)
                if source is not None:
                    changes.add_change(ChangeContents(module, source))
            job_set.finished_job()
        if self.project == self.source.project:
            changes.add_change(MoveResource(self.source, dest.path))
        return changes

    def _new_modname(self, dest):
        destname = libutils.modname(dest)
        if destname:
            if dest.is_folder():
                return destname + '.' + self.old_name
            return destname
        return self.old_name

    def _new_import(self, dest):
        return importutils.NormalImport([(self._new_modname(dest), None)])

    def _change_moving_module(self, changes, dest):
        if not self.source.is_folder():
            pymodule = self.project.get_pymodule(self.source)
            source = self.import_tools.relatives_to_absolutes(pymodule)
            pymodule = self.tools.new_pymodule(pymodule, source)
            source = self._change_occurrences_in_module(dest, pymodule)
            source = self.tools.new_source(pymodule, source)
            if source != self.source.read():
                changes.add_change(ChangeContents(self.source, source))

    def _change_occurrences_in_module(self, dest, pymodule=None,
                                      resource=None):
        if not self.tools.occurs_in_module(pymodule=pymodule,
                                           resource=resource):
            return
        if pymodule is None:
            pymodule = self.project.get_pymodule(resource)
        new_name = self._new_modname(dest)
        module_imports = importutils.get_module_imports(self.project, pymodule)
        changed = False
        source = None
        if libutils.modname(dest):
            changed = self._change_import_statements(dest, new_name,
                                                     module_imports)
            if changed:
                source = module_imports.get_changed_source()
                source = self.tools.new_source(pymodule, source)
                pymodule = self.tools.new_pymodule(pymodule, source)

        new_import = self._new_import(dest)
        source = self.tools.rename_in_module(
            new_name, imports=True, pymodule=pymodule,
            resource=resource if not changed else None)
        should_import = self.tools.occurs_in_module(
            pymodule=pymodule, resource=resource, imports=False)
        pymodule = self.tools.new_pymodule(pymodule, source)
        source = self.tools.remove_old_imports(pymodule)
        if should_import:
            pymodule = self.tools.new_pymodule(pymodule, source)
            source = self.tools.add_imports(pymodule, [new_import])
        source = self.tools.new_source(pymodule, source)
        if source is not None and source != pymodule.resource.read():
            return source
        return None

    def _change_import_statements(self, dest, new_name, module_imports):
        moving_module = self.source
        parent_module = moving_module.parent

        changed = False
        for import_stmt in module_imports.imports:
            if not any(name_and_alias[0] == self.old_name
                       for name_and_alias in
                       import_stmt.import_info.names_and_aliases) and \
               not any(name_and_alias[0] == libutils.modname(self.source)
                       for name_and_alias in
                       import_stmt.import_info.names_and_aliases):
                continue

            # Case 1: Look for normal imports of the moving module.
            if isinstance(import_stmt.import_info, importutils.NormalImport):
                continue

            # Case 2: The moving module is from-imported.
            changed = self._handle_moving_in_from_import_stmt(
                dest, import_stmt, module_imports, parent_module) or changed

            # Case 3: Names are imported from the moving module.
            context = importutils.importinfo.ImportContext(self.project, None)
            if not import_stmt.import_info.is_empty() and \
               import_stmt.import_info.get_imported_resource(context) == \
                    moving_module:
                import_stmt.import_info = importutils.FromImport(
                    new_name, import_stmt.import_info.level,
                    import_stmt.import_info.names_and_aliases)
                changed = True

        return changed

    def _handle_moving_in_from_import_stmt(self, dest, import_stmt,
                                           module_imports, parent_module):
        changed = False
        context = importutils.importinfo.ImportContext(self.project, None)
        if import_stmt.import_info.get_imported_resource(context) == \
                parent_module:
            imports = import_stmt.import_info.names_and_aliases
            new_imports = []
            for name, alias in imports:
                # The moving module was imported.
                if name == self.old_name:
                    changed = True
                    new_import = importutils.FromImport(
                        libutils.modname(dest), 0,
                        [(self.old_name, alias)])
                    module_imports.add_import(new_import)
                else:
                    new_imports.append((name, alias))

            # Update the imports if the imported names were changed.
            if new_imports != imports:
                changed = True
                if new_imports:
                    import_stmt.import_info = importutils.FromImport(
                        import_stmt.import_info.module_name,
                        import_stmt.import_info.level,
                        new_imports)
                else:
                    import_stmt.empty_import()
        return changed
