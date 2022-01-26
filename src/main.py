#!/usr/bin/env python3

import argparse
import os
import re


class XmlTreeElement:
    """ xmltree implementation """
    def __init__(self, tag, extra={}):
        self.tag = tag
        self.extra = extra

        self.text = None
        self.attributes = {}
        self.childrens = []
        self._unk = {}

    def add_child(self, child):
        if self.text is not None:
            raise ValueError("error can't set child with text value")
        self.childrens.append(child)

    def set_text(self, text):
        if self.childrens:
            raise ValueError("error can't set text with childs")
        elif self.text:
            raise ValueError("error can't set text with text set")
        self.text = text

    def add_attr(self, key, value, extra={}):
        self.extra[key] = extra
        self.attributes[key] = value

    def to_str(self, depth=0, indentation=4):
        spance_indentation = " " * (depth * indentation)

        # convert attributes
        attrs = ""
        if self.attributes:
            _a = [f'{key}="{str(value)}"' for key, value in self.attributes.items()]
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
    if val[0] == '"' and val[-1] == '"':
        return val[1:-1]
    return val


attr_reg = re.compile(r"^(http://schemas\.android\.com/apk/res/)([a-zA-Z\.:]+)\(0x[a-f0-9]+\)$")


def sanitize_android_key(val, resources_file):
    mat = attr_reg.match(val)
    if mat:
        # 0 = url
        # 1 = path ?
        # 2 = hexa ?
        return mat.groups()[1]
    return val


def sanitize_android_value(val, resources_file):
    val = sanitize_string(val)
    if resources_file and val[0] == "@":
        mat = re.search(r"\n    resource " + val[1:] + r" ([^\s\n]+)\n", resources_file)
        if mat:
            return "@" + mat.groups()[0]
    return val


elements = {
    "E": re.compile(r"^(\s*)E: ([a-zA-Z][a-zA-Z0-9\-_]+) \(line=(\d+)\)\s*$"),
    "A": re.compile(r"^(\s*)A: ([^\n\s=]+)=([^\n\s=]+)(?: \(Raw: (.+)\))?\s*$"),
    "T": re.compile(r"^(\s*)T: ([^\s\t]+)$"),
    "N": re.compile(r"^(\s*)N: ([^\n\s=]+)=([^\n\s=]+) \(line=(\d+)\)\s*$"),
}


def parse_line(line):
    for el_type, reg in elements.items():
        mat = reg.search(line)
        if mat:
            result = mat.groups()
            return len(result[0]), el_type, result[1:]
    raise ValueError("match nothing")


def parse_xml(value, resources_file):
    tree = []
    root = None
    level = 0
    is_android_special = False

    n_element = None

    for pos, line in enumerate(value.split("\n"), start=1):
        if not line:
            continue

        try:
            lvl, el_type, groups = parse_line(line)
            if is_android_special:
                lvl -= 2
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

            key = sanitize_android_key(groups[0], resources_file)
            value = sanitize_android_value(groups[1], resources_file)

            tree[-1].add_attr(key, value, extra=extra)

        elif el_type == "T":
            tree[-1].set_text(groups[0])

        elif el_type == "N":
            is_android_special = True
            n_element = (f"xmlns:{groups[0]}", sanitize_string(groups[1]))

    if is_android_special:
        root.add_attr(*n_element)

    return root


def main():

    p = argparse.ArgumentParser("xmltree2xml", description="convert android xmltree to classic xml.")
    p.add_argument("-n", "--no-header", help="do not add an xml header.", default=False)
    p.add_argument("-r", "--resources-file", nargs=1, help="resource file for replace every android hexa reference to \
        human redable reference.", default=None)
    p.add_argument("-o", "--output-dir", help="output directory.", default="output")
    p.add_argument("file", nargs='+', help="xmltree file.")
    flags = p.parse_args()

    if not os.path.exists(flags.output_dir):
        os.mkdir(flags.output_dir)
    for file_name in flags.file:
        with open(file_name, "r") as f:
            value = f.read()

        resources_file = None
        if flags.resources_file:
            with open(flags.resources_file[0], "r") as f:
                resources_file = f.read()

        try:
            root_el = parse_xml(value, resources_file)
        except Exception as e:
            raise ValueError(f"in '{file_name}': {str(e)}")
        if not root_el:
            raise ValueError(f"{file_name} is empty...")

        value = root_el.to_str()

        if not flags.no_header:
            value = '<?xml version="1.0" encoding="utf-8"?>\n' + value

        path = flags.output_dir
        if path[-1] != "/":
            path += "/"
        path += file_name
        if file_name[-4:] != ".xml":
            path += ".xml"
        with open(path, "w") as f:
            f.write(value)
        print(f"writing '{path}' ...")


if __name__ == "__main__":
    main()
