#!/usr/bin/env python3

import argparse
import os
import re


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

    def add_attrs(self, **attrs):
        self.attributes.update(attrs)

    def to_str(self, depth=0, indentation=4):
        spance_indentation = " " * (depth * indentation)

        # convert attributes
        attrs = ""
        if self.attributes:
            _a = [f"{key}=\"{str(value)}\"" for key, value in self.attributes.items()]
            attrs = " " + " ".join(_a)

        # text element
        if self.text:
            return f"{spance_indentation}<{self.tag}{attrs}>{self.text}</{self.tag}>"

        # auto close tag
        elif not self.childrens:
            return f"{spance_indentation}<{self.tag}{attrs} />"

        # convert child
        _chil = [child.to_str(depth=depth + 1, indentation=indentation) for child in self.childrens]
        childs = "\n".join(_chil)
        return f"{spance_indentation}<{self.tag}{attrs}>\n{childs}\n{spance_indentation}</{self.tag}>"


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
        # 1 = path ?
        # 2 = hexa ?
        return mat.groups()[1]
    mat = attr_reg2.match(val)
    if mat:
        return "app:" + mat.groups()[1]
    return val


def sanitize_android_value(val, resources):
    val = sanitize_string(val)
    # WARNING prefix "?" is unknow
    if resources:
        if val[0] in ["@", "?"]:
            mat = re.search(r"\n    resource " + re.escape(val[1:]) + r" ([^\s\n]+)\n", resources)
            if mat:
                if val[0] == "@":
                    return "@" + mat.groups()[0]
                return "?android:" + mat.groups()[0]
        if val[0] == "?":
            mat = re.search(r"\n\s{8}(.+?)\(0x[a-f0-9]+\)=" + re.escape(val) + "\n", resources)
            if mat:
                return "?android:" + mat.groups()[0]
    return val


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

    # unknow N: type
    is_android_special = 0
    n_element = {}

    for pos, line in enumerate(value.split("\n"), start=1):
        if not line:
            continue

        try:
            lvl, el_type, groups = parse_line(line)
            lvl -= ((is_android_special % 2) * 2)
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

            if len(tree) > 1 and level >= lvl:
                tree = tree[:lvl]
            level = lvl
            if not root:
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
            is_android_special += 1
            n_element[f"xmlns:{groups[0]}"] = sanitize_string(groups[1])

    # add N attribute
    root.add_attrs(**n_element)

    return root


def generate_path(output_dir, filename, resources):
    filename = os.path.basename(filename)
    if filename[-4:] != ".xml":
        filename += ".xml"

    # rename file wit resource name
    if resources:
        mat = re.search(r"\n\s{4}resource 0x[a-f0-9]+ xml/([a-zA-Z][a-zA-Z_-]*)\n\s{6}\(\) \(file\) res/" + re.escape(filename) + " type=XML", resources)
        if mat:
            filename = mat.groups()[0] + ".xml"
    return output_dir + filename


def main():

    p = argparse.ArgumentParser("xmltree2xml", description="convert android xmltree to classic xml.")
    p.add_argument("-n", "--no-header", help="do not add an xml header.", action="store_true", default=False)
    p.add_argument("-r", "--resources", nargs=1, help="resource file for replace every hexa reference to human redable reference.", default=None)
    p.add_argument("-o", "--output-dir", help="output directory.", default="output")
    p.add_argument("-f", "--rename-file", help="rename output file with resource name.", action="store_true", default=False)
    p.add_argument("file", nargs='+', help="xmltree file.")
    flags = p.parse_args()

    output_dir = os.path.normpath(flags.output_dir + "/")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

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

        path = generate_path(output_dir, filename, resources if flags.rename_file else None)
        with open(path, "w") as f:
            if not flags.no_header:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(root_el.to_str())

        print(f"writing '{path}' ...")


if __name__ == "__main__":
    main()
