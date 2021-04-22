#!/bin/bash

exe_type=$1
shift 1

core=${LIB_TOP}/json-template-engine/templating/core
tag_contrib=${LIB_TOP}/json-template-engine/templating/tag_contributions
java_libs=${LIB_TOP}/libs

case ${exe_type} in
python)
  export PYTHONPATH=${core}/build/python/dist/jsonteng.whl:${tag_contrib}/build/python/dist/jsonteng_contribs.whl:${PYTHONPATH}
  echo $*
  python3 -m jsonteng.template_engine $@
  ;;
java)
  jars=${core}/build/libs/jsonteng.jar:${tag_contrib}/build/libs/jsonteng-contribs.jar:${java_libs}/jackson-databind-2.9.7.jar:${java_libs}/jython-2.7.1b3.jar:${java_libs}/commons-cli-1.3.1.jar:${java_libs}/jackson-annotations-2.9.0.jar:${java_libs}/jackson-core-2.9.7.jar
  java -cp ${jars} com.vmware.jsonteng.TemplateEngine $*
  ;;
cpp)
  ${core}/build/c++/jsonteng $*
  ;;
go)
  ${core}/build/go/jsonteng_go_linux_x64  $*
  ;;
*)
  echo "Unknow lang type ${lang_type}"
  ;;
esac
