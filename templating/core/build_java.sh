#!/bin/bash

mode=$1

if [ "x${JSONTENG_BUILD_VERSION}" == "x" ] ; then
  source build.version
fi

if [ "x${mode}" == "xrelease" ]; then
  ./gradlew build publish publishToMavenLocal
else
  ./gradlew build publishToMavenLocal
fi

pushd build/libs/; rm -f jsonteng.jar; ln -s jsonteng-${JSONTENG_BUILD_VERSION}.jar jsonteng.jar; popd
