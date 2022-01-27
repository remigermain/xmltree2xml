from ..src.main import sanitize_string
import unittest


class TestSanitizeFunction(unittest.TestCase):
    def test_sanitize_string(self):
        self.assertEqual('bonjour ca va', sanitize_string('"bonjour ca va"'))
        # missing end quote
        self.assertEqual('bonjour ca va"', sanitize_string('bonjour ca va"'))
        self.assertEqual('"bonjour ca va', sanitize_string('"bonjour ca va'))
        # no remove '
        self.assertEqual("'bonjour ca va'", sanitize_string("'bonjour ca va'"))
