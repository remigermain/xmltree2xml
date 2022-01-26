import unittest
from ..src.main import parse_line


class TestParseLine(unittest.TestCase):

    def test_parse_line(self):
        result = parse_line("        A: http://schemas.android.com/apk/res/android:title(0x010101e1)=\"Load current\" (Raw: \"Load current\")")
        self.assertEqual(len("        "), result[0])
        self.assertEqual("A", result[1])
        self.assertEqual(("http://schemas.android.com/apk/res/android:title(0x010101e1)", "\"Load current\"", "\"Load current\""), result[2])
