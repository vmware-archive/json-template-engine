#!/bin/bash

if [ "x${JSONTENG_BUILD_VERSION}" == "x" ] ; then
  source ../core/build.version
fi

if [ "x${JSONTENG_CONTRIBS_BUILD_VERSION}" == "x" ] ; then
  source build.version
fi

mode=$1

if [ "x$mode" == "xrelease" ]; then
  ./gradlew build publish
else
  ./gradlew build publishToMavenLocal
fi

pushd build/libs; rm -f jsonteng-contribs.jar; ln -s jsonteng-contribs-${JSONTENG_CONTRIBS_BUILD_VERSION}.jar jsonteng-contribs.jar; popd
