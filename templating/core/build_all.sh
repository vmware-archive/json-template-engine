#/bin/bash

source build.version

# Remove build directory
echo ">>>> Remvoing ./build ..."
rm -rf ./build
echo

# Build Python
echo ">>>> Build Python version ..."
./build_py.sh
echo

# Build Java
echo ">>>> Build Java version ..."
./build_java.sh
echo

# Build C++
echo ">>>> Build C++ version ..."
./build_c++.sh
echo

# Build Go
echo ">>>> Build Go version ..."
./build_go.sh
echo
