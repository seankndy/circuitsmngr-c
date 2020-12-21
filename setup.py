#!/usr/bin/env python

import ast
import io
import re
import os
from setuptools import find_packages, setup

DEPENDENCIES = []
EXCLUDE_FROM_PACKAGES = ["contrib", "docs", "tests*", "env"]
CURDIR = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(CURDIR, "README.md"), "r", encoding="utf-8") as f:
    README = f.read()

setup(
    name='circuitsmngr-c',
    version='1.1.0',    
    description='circuitsmngr device connect utility',
    url='https://github.com/seankndy/circuitsmngr-c',
    author='Sean Kennedy',
    author_email='sean@kndy.net',
    license='BSD 2-clause',
    zip_safe=False,
    install_requires=[
       "requests",
    ],
    entry_points={"console_scripts": ["c=circuitsmngr_c.main:main"]},
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    keywords=[],
    scripts=[],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python",
    ],
)
