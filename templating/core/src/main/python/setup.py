# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

import setuptools


setuptools.setup(
    name="jsonteng",
    version="1.0.2",
    author="VMware",
    author_email="jimy@vmware.com",
    description="A template engine for JSON files.",
    long_description="A template engine for parameterized JSON files",
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
