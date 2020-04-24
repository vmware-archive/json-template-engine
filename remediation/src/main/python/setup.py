# Copyright 2019 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import os
import setuptools

setuptools.setup(
    name="jsonreme",
    version=os.getenv("JSONREME_BUILD_VERSION"),
    author="VMware",
    author_email="jimy@vmware.com",
    description="JSON Remediator.",
    long_description="JSON Remediator.",
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
