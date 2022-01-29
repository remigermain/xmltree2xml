#!/usr/bin/env python3

import setuptools
import os
import sys


version = "0.1.0"

if sys.argv[-1] == 'publish':
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system('rm -rf dist xmltree2xml.egg-info')
    os.system("python setup.py sdist")
    if os.system("twine check dist/*"):
        print("twine check failed. Packages might be outdated.")
        print("Try using `pip install -U twine wheel`.\nExiting.")
        sys.exit()
    os.system("twine upload dist/*")
    sys.exit()


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xmltree2xml",
    version=version,
    author="rgermain",
    license='MIT',
    author_email='contact@germainremi.fr',
    description="convert compile xmltree file from android to classic xml",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/remigermain/xmltree2xml",
    project_urls={
        "Bug Tracker": "https://github.com/remigermain/xmltree2xml/issues",
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
    packages=["xmltree2xml"],
    python_requires=">=3.6",
    entry_points={
        "entry_points": "app=xmltree2xml.main:main"
    }
)
