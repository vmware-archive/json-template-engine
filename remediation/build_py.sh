#!/bin/bash
# Copyright 2020 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

if [ "x${JSONREME_BUILD_VERSION}" == "x" ] ; then
  source build.version
fi

mkdir -p build/python
pushd src/main/python
python3 setup.py sdist bdist_wheel
rm -rf ../../../build/python/dist
mv dist ../../../build/python/
rm -rf build *.egg-info
popd
pushd build/python/dist
rm -f jsonreme.whl
ln -s jsonreme-${JSONREME_BUILD_VERSION}-py3-none-any.whl jsonreme.whl
popd
echo "Wheel distribuiton is in build/python/dist"
