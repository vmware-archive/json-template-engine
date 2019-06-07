#/bin/bash

source build.version

# Remove build directory
rm -rf ./build

# Build python
./build_py.sh

# Build java
./gradlew build uploadArchive

