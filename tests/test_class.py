import unittest

from ..src.main import XmlTreeElement, parse_xml


class TestXmlClass(unittest.TestCase):

    def test_tag(self):
        c = XmlTreeElement("isatag")
        self.assertEqual(c.tag, "isatag")
    
    def test_attr(self):
        c = XmlTreeElement("isatag")
        c.add_attr("kfffey", "value9595")
        self.assertEqual(c.attributes, {"kfffey": "value9595"})
    
    def test_text(self):
        c = XmlTreeElement("isatag")
        c.set_text("is a text")
        self.assertEqual(c.text, "is a text")

    def test_child(self):
        c = XmlTreeElement("isatag")
        chil = XmlTreeElement("lopilp")
        c.add_child(chil)
        self.assertEqual(c.childrens[0], chil)

    def test_set_text_with_child(self):
        c = XmlTreeElement("isatag")
        chil = XmlTreeElement("lopilp")
        c.add_child(chil)
        
        with self.assertRaises(ValueError):
            c.set_text("text")

    def test_set_child_with_text(self):
        c = XmlTreeElement("isatag")
        c.set_text("text")
        
        with self.assertRaises(ValueError):
            c.add_child(XmlTreeElement("lopilp"))

    def test_format_no_child_no_attr_no_text(self):
        c = XmlTreeElement("tag")
        v = c.to_str(0, 0)
        self.assertEqual(v, "<tag />")
    
    def test_format_no_child_no_attr_with_text(self):
        c = XmlTreeElement("tag")
        c.set_text("text")
        v = c.to_str(0, 0)
        self.assertEqual(v, "<tag>text</tag>")

    def test_format_no_child_with_attr_no_text(self):
        c = XmlTreeElement("tag")
        c.add_attr("key", "value")
        c.add_attr("anotherkey", "5555?pp")
        v = c.to_str(0, 0)
        self.assertEqual(v, '<tag key="value" anotherkey="5555?pp" />')

    def test_format_with_child_no_attr_no_text(self):
        c = XmlTreeElement("tag")
        c.add_child(XmlTreeElement("div"))
        v = c.to_str(0, 0)
        self.assertEqual(v, '<tag>\n<div />\n</tag>')

    def test_format_indente(self):
        c = XmlTreeElement("tag")
        chil = XmlTreeElement("div")
        chil.add_child(XmlTreeElement("lol"))
        c.add_child(chil)
        v = c.to_str(0, 4)
        self.assertEqual(v, '<tag>\n    <div>\n        <lol />\n    </div>\n</tag>')
