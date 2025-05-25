#!/bin/bash

set -e  # Exit if any command fails

echo "🔧 Compiling Python C API testbench..."
gcc -O3 bench_py_dict.c -I$(python3-config --includes) $(python3-config --ldflags) -o bench_py_dict
echo "🚀 Running Python C API testbench..."
./bench_py_dict

echo ""
echo "🔧 Compiling C++ STL unordered_map testbench..."
g++ -std=c++17 -O3 bench_unordered_map.cpp -o bench_um
echo "🚀 Running C++ STL testbench..."
./bench_um
