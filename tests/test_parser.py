import unittest

from ..xmltree2xml.main import XmlTreeElement, parse_xml


class TestParser(unittest.TestCase):

    def assertXmlTreeEqual(self, s, d):

        self.assertIsInstance(s, XmlTreeElement)
        self.assertIsInstance(d, XmlTreeElement)
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
        root_origi = parse_xml(value)

        root_new = XmlTreeElement("list", extra={"line": "16"})
        root_new.add_attr("name", "carrier_config_list", extra={"Raw": "carrier_config_list"})

        pbundle_as_map = XmlTreeElement("pbundle_as_map", extra={"line": "17"})
        c = XmlTreeElement("string-array", extra={"line": "19"})
        c.add_attr("name", "mccmnc", extra={"Raw": "mccmnc"})

        it = XmlTreeElement("item", extra={"line": "20"})
        it.add_attr("value", "TEST", extra={"Raw": "TEST"})

        c.add_child(it)
        pbundle_as_map.add_child(c)
        root_new.add_child(pbundle_as_map)

        pbundle_as_map = XmlTreeElement("pbundle_as_map", extra={"line": "24"})
        c = XmlTreeElement("string-array", extra={"line": "26"})
        c.add_attr("name", "mccmnc", extra={"Raw": "mccmnc"})

        it = XmlTreeElement("item", extra={"line": "28"})
        it.add_attr("value", "20601")
        c.add_child(it)

        it = XmlTreeElement("item", extra={"line": "30"})
        it.add_attr("value", "20810")
        c.add_child(it)

        it = XmlTreeElement("item", extra={"line": "31"})
        it.add_attr("value", "20826")
        c.add_child(it)

        pbundle_as_map.add_child(c)

        root_new.add_child(pbundle_as_map)

        self.assertXmlTreeEqual(root_origi, root_new)

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


class TestParserAndroidReference(unittest.TestCase):
    def test_with_namespace(self):
        value = """N: android=http://schemas.android.com/apk/res/android (line=15)
  E: PreferenceScreen (line=19)
    A: http://schemas.android.com/apk/res/android:title(0x010101e1)=@0x7f1502b8
      E: ListPreference (line=22)
        A: http://schemas.android.com/apk/res/android:entries(0x010100b2)=@0x7f03000e
        A: http://schemas.android.com/apk/res/android:title(0x010101e1)=@0x7f1502b5
        A: http://schemas.android.com/apk/res/android:key(0x010101e8)=@0x7f1502b6
        A: http://schemas.android.com/apk/res/android:summary(0x010101e9)="%s" (Raw: "%s")
        A: http://schemas.android.com/apk/res/android:defaultValue(0x010101ed)=@0x7f1502b4
        A: http://schemas.android.com/apk/res/android:dialogTitle(0x010101f2)=@0x7f1502b5
        A: http://schemas.android.com/apk/res/android:entryValues(0x010101f8)=@0x7f03000f
      E: ListPreference (line=31)
        A: http://schemas.android.com/apk/res/android:entries(0x010100b2)=@0x7f03000c
        A: http://schemas.android.com/apk/res/android:title(0x010101e1)=@0x7f1502bd
        A: http://schemas.android.com/apk/res/android:key(0x010101e8)=@0x7f1502be
        A: http://schemas.android.com/apk/res/android:summary(0x010101e9)="%s" (Raw: "%s")
        A: http://schemas.android.com/apk/res/android:defaultValue(0x010101ed)=@0x7f1502bc
        A: http://schemas.android.com/apk/res/android:dialogTitle(0x010101f2)=@0x7f1502bd
        A: http://schemas.android.com/apk/res/android:entryValues(0x010101f8)=@0x7f03000d
      E: ListPreference (line=40)
        A: http://schemas.android.com/apk/res/android:title(0x010101e1)=@0x7f150604
        A: http://schemas.android.com/apk/res/android:key(0x010101e8)=@0x7f1502b7
        A: http://schemas.android.com/apk/res/android:summary(0x010101e9)="%s" (Raw: "%s")
        A: http://schemas.android.com/apk/res/android:dialogTitle(0x010101f2)=@0x7f150604"""

        root = parse_xml(value)

        expected = """<PreferenceScreen xmls:android="http://schemas.android.com/apk/res/android" android:title="@0x7f1502b8">
    <ListPreference android:entries="@0x7f03000e" android:title="@0x7f1502b5" android:key="@0x7f1502b6" android:summary="%s" android:defaultValue="@0x7f1502b4" android:dialogTitle="@0x7f1502b5" android:entryValues="@0x7f03000f" />
    <ListPreference android:entries="@0x7f03000c" android:title="@0x7f1502bd" android:key="@0x7f1502be" android:summary="%s" android:defaultValue="@0x7f1502bc" android:dialogTitle="@0x7f1502bd" android:entryValues="@0x7f03000d" />
    <ListPreference android:title="@0x7f150604" android:key="@0x7f1502b7" android:summary="%s" android:dialogTitle="@0x7f150604" />
</PreferenceScreen>"""

        self.assertEqual(expected, root.to_str())
