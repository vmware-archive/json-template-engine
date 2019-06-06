# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

import os
import setuptools


setuptools.setup(
    name="jsonteng",
    version=os.getenv("JSONTENG_BUILD_VERSION"),
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
