#!/usr/bin/env python3

import argparse
import os
import re
from functools import reduce


class XmlTreeElement:
    """ xmltree implementation """
    def __init__(self, tag, text=None, child=[], attrs={}, extra={}):
        self.tag = tag
        self.extra = extra

        self.text = text

        self.attributes = {**attrs}
        self.extra_attrs = {}
        self.extra = {**extra}
        self.childrens = [*child]
        self.namespaces = {}

    def add_child(self, child):
        if self.text is not None:
            raise ValueError("error can't set child with text value")
        self.childrens.append(child)

    def set_text(self, text):
        if len(self.childrens) != 0:
            raise ValueError("error can't set text with childs")
        elif self.text:
            raise ValueError("error can't set text with text set")
        self.text = text

    def add_attr(self, key, value, extra={}):
        self.extra_attrs[key] = extra
        self.attributes[key] = value

    def add_namespace(self, key, value):
        self.namespaces[f"xmls:{key}"] = value

    def add_namespaces(self, **namespaces):
        for key, val in namespaces.items():
            self.add_namespace(key, val)

    def add_attrs(self, **attrs):
        self.attributes.update(attrs)

    def to_str(self, depth=0, indentation=4):
        spance_indentation = " " * (depth * indentation)

        # convert attributes
        attrs = reduce(lambda fi, d: f"{fi} {d[0]}=\"{str(d[1])}\"", self.attributes.items(), "")
        namespaces = reduce(lambda fi, d: f"{fi} {d[0]}=\"{str(d[1])}\"", self.namespaces.items(), "")
        child = reduce(lambda fi, child: f"{fi}\n" + child.to_str(depth + 1, indentation), self.childrens, "")

        start_tag = f"{spance_indentation}<{self.tag}{namespaces}{attrs}"
        end_tag = f"</{self.tag}>"

        if self.text:
            return f"{start_tag}>{self.text}{end_tag}"
        elif not self.childrens:
            return f"{start_tag} />"
        return f"{start_tag}>{child}\n{spance_indentation}{end_tag}"


def sanitize_string(val):
    if val[0] == "\"" and val[-1] == "\"":
        return val[1:-1]
    return val


# WARNING eend url "res-auto:" or "android:" is unknow
attr_reg = re.compile(r"^(http://schemas\.android\.com/apk/res/)([a-zA-Z\.:_\-]+)\(0x[a-f0-9]+\)$")
attr_reg2 = re.compile(r"^(http://schemas\.android\.com/apk/res-auto:)([a-zA-Z\.:_\-]+)\(0x[a-f0-9]+\)$")


def sanitize_android_key(val, resources):
    mat = attr_reg.match(val)
    if mat:
        # 0 = url
        # 1 = namespace ?
        # 2 = hexa ?
        return mat.groups()[1]
    mat = attr_reg2.match(val)
    if mat:
        return "app:" + mat.groups()[1]
    return val


"""
    Accessing resources from XML
    @[<package_name>:]<resource_type>/<resource_name>

    Referencing style attributes
    ?[<package_name>:][<resource_type>/]<resource_name>

"""


def sanitize_android_value(val, resources):
    val = sanitize_string(val)
    # WARNING prefix "?" is unknow
    if resources:
        if val[0] == "@":
            mat = re.search(r"\n\s{4}resource " + re.escape(val[1:]) + r" ([^\s\n]+)\n", resources)
            if mat:
                return "@" + mat.groups()[0]
        elif val[0] == "?":
            mat = re.search(r"\n\s{4}resource 0x[a-f0-9]+ (.+?)\n\s{6}\(\) \(style\) size=\d+ parent=" + re.escape(val[1:]), resources)
            if mat:
                return "?android:" + mat.groups()[0]
    return val


"""
    E: Element
    A: Attribute
    T: Text value
    N: Namespace
"""
elements = {
    "E": re.compile(r"^(\s*)E: ([a-zA-Z][a-zA-Z0-9\-_\.]+?) \(line=(\d+)\)\s*$"),
    "A": re.compile(r"^(\s*)A: (.+?)=(.+?)(?: \(Raw: (.+?)\))?\s*$"),
    "T": re.compile(r"^(\s*)T: (.+?)$"),
    "N": re.compile(r"^(\s*)N: ([^\n\s=]+?)=(.+?) \(line=(\d+?)\)\s*$"),
}


def parse_line(line):
    for el_type, reg in elements.items():
        mat = reg.search(line)
        if mat:
            result = mat.groups()
            return len(result[0]), el_type, result[1:]
    raise ValueError("match nothing")


def parse_xml(value, resources=None):
    tree = []
    root = None
    level = 0

    namespaces_number = 0
    namespaces = {}

    for pos, line in enumerate(value.split("\n"), start=1):
        if not line:
            continue

        try:
            lvl, el_type, groups = parse_line(line)
            lvl -= ((namespaces_number % 2) * 2)
            mod = lvl % 4
            lvl //= 4
        except Exception as e:
            raise ValueError(f"{str(e)} in line {pos}")

        # check formating
        if lvl > level + 1:
            raise ValueError(f"to many indentation in line {pos}")
        elif mod not in [0, 2]:
            raise ValueError(f"wrong indentation in line {pos}")
        elif el_type == "A" and not tree:
            raise ValueError(f"wrong format for 'A' type in line {pos}")
        elif el_type == "A" and (level != lvl or mod != 2):
            raise ValueError(f"wrong indentation for 'A' type in line {pos}")
        elif el_type == "T" and (level + 1 != lvl or mod != 0):
            raise ValueError(f"wrong indentation for 'T' type in line {pos}")
        elif lvl == 0 and el_type == "E" and root:
            raise ValueError(f"multiple root element in line {pos}")

        if el_type == "E":
            xml_el = XmlTreeElement(groups[0], extra={"line": sanitize_string(groups[1])})

            xml_el.add_namespaces(**namespaces)
            namespaces = {}

            if len(tree) > 1 and level >= lvl:
                tree = tree[:lvl]
            level = lvl
            if root is None:
                root = xml_el
            else:
                tree[-1].add_child(xml_el)
            tree.append(xml_el)

        elif el_type == "A":
            extra = {}
            if groups[2]:
                extra["Raw"] = sanitize_string(groups[2])

            tree[-1].add_attr(
                sanitize_android_key(groups[0], resources),
                sanitize_android_value(groups[1], resources),
                extra=extra
            )

        elif el_type == "T":
            tree[-1].set_text(groups[0])

        elif el_type == "N":
            if root:
                raise ValueError("N type is aleready create")
            namespaces_number += 1
            namespaces[groups[0]] = sanitize_string(groups[1])

    return root


def generate_path(output_dir, filename, resources=None):

    filename = os.path.basename(filename)
    if filename[-4:] != ".xml":
        filename += ".xml"

    # rename file wit resource name
    if resources:
        mat = re.search(r"\n\s{4}resource 0x[a-f0-9]+ xml/([a-zA-Z][a-zA-Z_-]*)\n\s{6}\(\) \(file\) res/" + re.escape(filename) + " type=XML", resources)
        if mat:
            filename = mat.groups()[0] + ".xml"

    return os.path.normpath(output_dir + "/" + filename)


def main():

    p = argparse.ArgumentParser("xmltree2xml", description="convert android xmltree to classic xml.")
    p.add_argument("-n", "--no-header", help="do not add an xml header.", action="store_true", default=False)
    p.add_argument("-r", "--resources", nargs=1, help="resource file for replace every hexa reference to human redable reference.", default=None)
    p.add_argument("-o", "--output-dir", help="output directory.", default="output")
    p.add_argument("-f", "--rename-file", help="rename output file with resource name.", action="store_true", default=False)
    p.add_argument("file", nargs='+', help="xmltree file.")
    flags = p.parse_args()

    if not os.path.exists(flags.output_dir):
        os.mkdir(flags.output_dir)

    for filename in flags.file:
        with open(filename, "r") as f:
            value = f.read()

        resources = None
        if flags.resources:
            with open(flags.resources[0], "r") as f:
                resources = f.read()

        try:
            root_el = parse_xml(value, resources)
            if not root_el:
                raise ValueError("file is empty...")
        except Exception as e:
            raise ValueError(f"from '{filename}': {str(e)}")

        path = generate_path(flags.output_dir, filename, resources if flags.rename_file else None)
        with open(path, "w") as f:
            if not flags.no_header:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(root_el.to_str())

        print(f"writing '{path}' ...")


if __name__ == "__main__":
    main()
