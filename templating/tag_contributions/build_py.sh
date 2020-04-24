#!/bin/bash
# Copyright 2019 VMware, Inc.
# SPDX-License-Indentifier: Apache-2.0

if [ "x${JSONTENG_CONTRIBS_BUILD_VERSION}" == "x" ] ; then
  source build.version
fi

mkdir -p build/python
pushd src/main/python
python3 setup.py sdist bdist_wheel
rm -rf ../../../build/python/dist
mv dist ../../../build/python/
rm -rf build jsonteng_contribs.egg-info
popd
pushd build/python/dist
rm -f jsonteng_contribs.whl
ln -s jsonteng_contribs-${JSONTENG_CONTRIBS_BUILD_VERSION}-py3-none-any.whl jsonteng_contribs.whl
popd
echo "Wheel distribuiton is in build/python/dist"
