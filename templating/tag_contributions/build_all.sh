#!/bin/bash

mode=$1

./build_py.sh $mode

./build_java.sh $mode
