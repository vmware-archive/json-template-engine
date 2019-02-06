#!/bin/bash

mkdir -p build/python
pushd src/main/python
python3 setup.py sdist bdist_wheel
rm -rf ../../../build/python/dist
mv dist ../../../build/python/
rm -rf build muban_extra.egg-info
popd
echo "Wheel distribuiton is in build/python/dist"
