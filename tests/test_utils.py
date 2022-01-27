from ..src.main import sanitize_string, generate_path
import unittest


class TestSanitizeFunction(unittest.TestCase):
    def test_sanitize_string(self):
        self.assertEqual('bonjour ca va', sanitize_string('"bonjour ca va"'))
        # missing end quote
        self.assertEqual('bonjour ca va"', sanitize_string('bonjour ca va"'))
        self.assertEqual('"bonjour ca va', sanitize_string('"bonjour ca va'))
        # no remove '
        self.assertEqual("'bonjour ca va'", sanitize_string("'bonjour ca va'"))

    def test_generate_path_without_extention(self):
        self.assertEqual("dir/file.xml", generate_path("dir/", "file", None))
        self.assertEqual("dir/file..xml", generate_path("dir/", "file.", None))

    def test_generate_path_with_extention(self):
        self.assertEqual("dir/file.op.xml", generate_path("dir/", "file.op", None))
        self.assertEqual("dir/file.xml", generate_path("dir/", "file.xml", None))

    def test_generate_path_without_slash_dir(self):
        self.assertEqual("dir/file.xml", generate_path("dir", "file.xml", None))
        self.assertEqual("dir/output/op/file.xml", generate_path("dir/output/op", "file.xml", None))

    def test_generate_path_with_resource(self):
        resources = """
        --- another file ----
    resource 0x7f180012 xml/file_final
      () (file) res/file.xml type=XML
    resource 0x7f180512 xml/other_file
      () (file) res/other_file.xml type=XML
        """
        self.assertEqual("dir/file_final.xml", generate_path("dir/", "file.xml", resources))
        self.assertEqual("dir/nofile.xml", generate_path("dir/", "nofile.xml", resources))
