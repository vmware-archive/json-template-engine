#!/bin/bash

if [ "x${JSONTENG_BUILD_VERSION}" == "x" ] ; then
  source build.version
fi

make clean cli

