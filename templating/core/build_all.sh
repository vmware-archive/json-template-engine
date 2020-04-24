#/bin/bash

mode=$1

source build.version

# Remove build directory
echo ">>>> Remvoing ./build ..."
rm -rf ./build
echo

# Build Python
echo ">>>> Build Python version ..."
./build_py.sh ${mode}
echo

# Build Java
echo ">>>> Build Java version ..."
./build_java.sh ${mode}
echo

# Build C++
echo ">>>> Build C++ version ..."
./build_c++.sh ${mode}
echo

# Build Go
echo ">>>> Build Go version ..."
./build_go.sh ${mode}
echo
