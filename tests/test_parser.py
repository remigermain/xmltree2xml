import unittest

from ..src.main import XmlTreeElement, parse_xml


class TestParser(unittest.TestCase):

    def assertXmlTreeEqual(self, s, d):

        self.assertEqual(s.tag, d.tag)
        self.assertEqual(s.attributes, d.attributes)
        self.assertEqual(s.extra, d.extra)
        self.assertEqual(s.text, d.text)
        self.assertEqual(s.extra, d.extra)
        self.assertEqual(len(s.childrens), len(d.childrens))
        if s.childrens:
            for child_s, child_d in zip(s.childrens, d.childrens):
                self.assertXmlTreeEqual(child_s, child_d)

    def test_parse(self):
        value = """E: list (line=16)
  A: name="carrier_config_list" (Raw: "carrier_config_list")
    E: pbundle_as_map (line=17)
        E: string-array (line=19)
          A: name="mccmnc" (Raw: "mccmnc")
            E: item (line=20)
              A: value="TEST" (Raw: "TEST")
    E: pbundle_as_map (line=24)
        E: string-array (line=26)
          A: name="mccmnc" (Raw: "mccmnc")
            E: item (line=28)
              A: value=20601
            E: item (line=30)
              A: value=20810
            E: item (line=31)
              A: value=20826
"""
        root = parse_xml(value)
        self.assertIsInstance(root, XmlTreeElement)

        l = XmlTreeElement("list", {"line": "16"})
        l.add_attr("name", "carrier_config_list", extra={"Raw": "carrier_config_list"})

        pbundle_as_map = XmlTreeElement("pbundle_as_map", {"line": "17"})
        c = XmlTreeElement("string-array", {"line": "19"})
        c.add_attr("name", "mccmnc", extra={"Raw": "mccmnc"})

        it = XmlTreeElement("item", {"line": "20"})
        it.add_attr("value", "TEST", extra={"Raw": "TEST"})

        c.add_child(it)
        pbundle_as_map.add_child(c)
        l.add_child(pbundle_as_map)

        pbundle_as_map = XmlTreeElement("pbundle_as_map", {"line": "24"})
        c = XmlTreeElement("string-array", {"line": "26"})
        c.add_attr("name", "mccmnc", extra={"Raw": "mccmnc"})

        it = XmlTreeElement("item", {"line": "28"})
        it.add_attr("value", "20601")
        c.add_child(it)

        it = XmlTreeElement("item", {"line": "30"})
        it.add_attr("value", "20810")
        c.add_child(it)

        it = XmlTreeElement("item", {"line": "31"})
        it.add_attr("value", "20826")
        c.add_child(it)

        pbundle_as_map.add_child(c)

        l.add_child(pbundle_as_map)

        self.assertXmlTreeEqual(root, l)

    def test_wrong_format_indente(self):
        value = " E: list (line=16)"
        with self.assertRaises(ValueError):
            parse_xml(value)

        value = """E: list (line=16)
  A: name="carrier_config_list" (Raw: "carrier_config_list")
    E: pbundle_as_map (line=17)
        E: string-array (line=19)
          A: name="mccmnc" (Raw: "mccmnc")
             E: item (line=20)
              A: value="TEST" (Raw: "TEST")
    E: pbundle_as_map (line=24)
        E: string-array (line=26)
          A: name="mccmnc" (Raw: "mccmnc")
            E: item (line=28)
              A: value=20601
            E: item (line=30)
              A: value=20810
            E: item (line=31)
              A: value=20826
"""
        with self.assertRaises(ValueError):
            parse_xml(value)

    def test_wrong_indent_attr(self):
        value = """E: list (line=16)
  A: name="carrier_config_list" (Raw: "carrier_config_list")
    E: pbundle_as_map (line=17)
        E: string-array (line=19)
          A: name="mccmnc" (Raw: "mccmnc")
        A: value="TEST" (Raw: "TEST")
"""
        with self.assertRaises(ValueError):
            parse_xml(value)

        value = """A: value="TEST" (Raw: "TEST")"""
        with self.assertRaises(ValueError):
            parse_xml(value)

        value = """  A: value="TEST" (Raw: "TEST")"""
        with self.assertRaises(ValueError):
            parse_xml(value)

    def test_wrong_indent_text(self):
        value = """E: list (line=16)
  A: name="carrier_config_list" (Raw: "carrier_config_list")
    E: pbundle_as_map (line=17)
        E: string-array (line=19)
          A: name="mccmnc" (Raw: "mccmnc")
        T: value="TEST" (Raw: "TEST")
"""
        with self.assertRaises(ValueError):
            parse_xml(value)

        value = """T: value="TEST" (Raw: "TEST")"""
        with self.assertRaises(ValueError):
            parse_xml(value)

        value = """  T: value="TEST" (Raw: "TEST")"""
        with self.assertRaises(ValueError):
            parse_xml(value)
        
        value = """E: list (line=16)\n  T: value="TEST" (Raw: "TEST")"""
        with self.assertRaises(ValueError):
            parse_xml(value)