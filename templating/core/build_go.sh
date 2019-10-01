#!/bin/bash

if [ "x${JSONTENG_BUILD_VERSION}" == "x" ] ; then
  source build.version
fi

export GOPATH=$(pwd)/src/main/go:$(pwd)/../tag_contributions/src/main/go

go build -pkgdir $(pwd)/build/go/obj jsonteng
go fmt jsonteng
go build -pkgdir $(pwd)/build/go/obj jsonteng_contribs/tags
go fmt jsonteng_contribs/tags
go build -o $(pwd)/build/go/jsonteng_go_linux_x64 -pkgdir $(pwd)/build/go/obj $(pwd)/src/main/go/src/cli.go
go fmt $(pwd)/src/main/go/src/cli.go

tar czf $(pwd)/build/go/source_go_${JSONTENG_BUILD_VERSION}.tgz -C $(pwd)/src/main/go src -C $(pwd)/../tag_contributions/src/main/go src
