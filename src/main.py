#!/usr/bin/env python3

import argparse
import os
import re


class XmlTreeElement:
    def __init__(self, tag, **kwargs):
        self.tag = tag
        self.kwargs = kwargs

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

    def add_attr(self, key, value, _unk={}):
        self._unk[key] = _unk
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


def span(line, fnc):
    """number char span , fnc"""
    for i, c in enumerate(line):
        if not fnc(c):
            return i
    return 0


def parse_line(line, padding):
    info = {}
    # start space
    idx = span(line, str.isspace)
    clc = idx
    if padding:
        clc += 2
    info["level"] = clc // 4
    info["mod"] = clc % 4
    line = line[idx:]

    # type like E:, A: ...
    sp = line.index(":")
    info["type"] = line[:sp]
    line = line[sp + 1:]

    # take element
    if info["type"] in ["E", "N"]:
        try:
            sp = line.index("(")
            info["value"] = line[:sp].strip()

            # unknow value in parentes
            line, pos = line[sp:].replace("(", "").replace(")", "").strip().split("=")
            info["kwargs"] = {line.strip(): int(pos.strip())}
        except Exception:
            raise ValueError("wrong format")

        if info["type"] == "N":
            key, value = info["value"].split("=")
            info["key"] = f"xmls:{key}"
            info["value"] = value

    # take attribute
    elif info["type"] == "A":

        idx = line.index("=")
        info["key"] = line[:idx].strip()
        line = line[idx + 1:]

        info["unk"] = {}
        if line[0] in '"':
            # start = 1 for space "
            idx = line.index("\"", 1)
            info["value"] = line[:idx].replace('"', '')

            line = line[idx+1:]

            value = line[line.index("(Raw: "):].replace(")", "").strip()
            info["unk"]["Raw"] = value.replace('"', "").strip()

        else:
            v = line.strip()
            if v.isdigit():
                v = int(v)
            info["value"] = v

        c = re.compile(r"^http://schemas\.android\.com/apk/res/([a-zA-Z\.:]+)\(0x[a-f0-9]+\)$")
        m = c.match(info["key"])
        if m:
            info["key"] = m.groups()[0]

    # take text value
    elif info["type"] == "T":
        info["value"] = line.strip().replace("'", "")
    return info


def parse_xml(value):
    tree = []
    root = None
    level = 0
    padding = False

    n_element = None

    for pos, line in enumerate(value.split("\n"), start=1):
        if not line:
            continue

        try:
            info = parse_line(line, padding)
        except Exception as e:
            raise ValueError(f"{str(e)} in line {pos}")

        # check formating
        if info["level"] > level + 1:
            raise ValueError(f"to many indentation in line {pos}")
        elif info["mod"] not in [0, 2]:
            raise ValueError(f"wrong indentation in line {pos}")
        elif info["type"] == "A" and not tree:
            raise ValueError(f"wrong format for 'A' type in line {pos}")
        elif info["type"] == "A" and (level != info["level"] or info["mod"] != 2):
            raise ValueError(f"wrong indentation for 'A' type in line {pos}")
        elif info["type"] == "T" and (level + 1 != info["level"] or info["mod"] != 0):
            raise ValueError(f"wrong indentation for 'T' type in line {pos}")
        elif info["level"] == 0 and info["type"] == "E" and root:
            raise ValueError(f"multiple root element in line {pos}")

        if info["type"] == "E":
            xml_el = XmlTreeElement(info["value"], **info["kwargs"])

            if len(tree) > 1 and level >= info["level"]:
                tree = tree[:info["level"]]
            level = info["level"]

            if not root:
                root = xml_el
            else:
                tree[-1].add_child(xml_el)

            tree.append(xml_el)

        elif info["type"] == "A":
            tree[-1].add_attr(info["key"], info["value"], _unk=info["unk"])
        elif info["type"] == "T":
            tree[-1].set_text(info["value"])
        elif info["type"] == "N":
            padding = True
            n_element = (info['key'], info["value"])
        # else:
        #     raise ValueError(f"unknow type '{info['type']}'")

    if n_element:
        root.add_attr(*n_element)

    return root


def main():

    p = argparse.ArgumentParser("xmltree2xml", description="convert android xmltree to classic xml.")
    p.add_argument("-n", "--no-header", help="do not add an xml header.", default=False)
    p.add_argument("-o", "--output-dir", help="output directory.", default="output")
    p.add_argument("file", nargs='+', help="xmltree file")
    flags = p.parse_args()

    if not os.path.exists(flags.output_dir):
        os.mkdir(flags.output_dir)
    for file_name in flags.file:
        with open(file_name, "r") as f:
            value = f.read()

        try:
            root_el = parse_xml(value)
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
