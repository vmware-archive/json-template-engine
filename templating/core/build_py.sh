#!/bin/bash
# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

if [ "x${JSONTENG_BUILD_VERSION}" == "x" ] ; then
  source build.version
fi

mkdir -p build/python
pushd src/main/python
python3 setup.py sdist bdist_wheel
rm -rf ../../../build/python/dist
mv dist ../../../build/python/
rm -rf build jsonteng.egg-info
popd
pushd build/python/dist; rm -f jsonteng.whl; ln -s jsonteng-${JSONTENG_BUILD_VERSION}-py3-none-any.whl jsonteng.whl; popd
echo "Wheel distribuiton is in build/python/dist"
