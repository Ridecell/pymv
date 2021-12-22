import textwrap
import unittest

from main import ImportGraph, ImportStatement, parse_directory


class ImportStatement:

    def __init__(self, import_base, import_name, import_alias):
        self.import_base = import_base
        self.import_name = import_name
        self.import_alias = import_alias


class TestParseDirectory(unittest.TestCase):

    def test_example_minimal_program(self):
        self.assertDictEqual(
            parse_directory('fixtures/example_simple'), {
                '/file_1.py': textwrap.dedent('''
                    from file_2 import testf

                    print(repr(testf()))
                '''),
                '/file_2.py': textwrap.dedent('''
                    import numpy as np

                    testf(nm.zeros((2,3)))
                ''')
            }
        )


# class TestParseAndExportdirectoryRoundtrips(unittest.TestCase):

#     def test_roundtrip(self):
#         import_graph = ImportGraph.from_files(files)
#         files_regenerated = import_graph.to_files()
#         self.assertDictEqual(files, files_regenerated)


# class TestImportGraphRoundtrips(unittest.TestCase):

#     def test_roundtrip(self):
#         import_graph = ImportGraph.from_files(files)
#         files_regenerated = import_graph.to_files()
#         self.assertDictEqual(files, files_regenerated)


class TestImportGraph(unittest.TestCase):

    def test_reference(self):
        files = {
            '/file_1.py': textwrap.dedent('''
                from file_2 import testf

                print(repr(testf()))
            '''),
            '/file_2.py': textwrap.dedent('''
                import numpy as np

                testf(nm.zeros((2,3)))
            ''')
        }
        import_graph = ImportGraph.from_files(files)
        files_regenerated = import_graph.to_files()
        self.assertDictEqual(files, files_regenerated)
