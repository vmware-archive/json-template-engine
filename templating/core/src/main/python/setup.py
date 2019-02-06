# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

import setuptools

with open("../../../../../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jsonteng",
    version="1.0.1",
    author="VMware",
    author_email="jimy@vmware.com",
    description="A template engine for JSON files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Apache 2.0 :: Apache 2.0",
        "Operating System :: OS Independent",
    ],
)
