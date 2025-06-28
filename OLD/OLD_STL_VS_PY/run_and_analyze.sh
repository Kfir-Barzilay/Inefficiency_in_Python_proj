#!/bin/bash
set -e

echo "=== 🧪 C++ unordered_map Benchmark ==="

# Compile with debug symbols to get function names in perf
echo "🔨 Compiling dict.cpp with -g for symbols..."
g++ -O2 -std=c++17 -g dict.cpp -o dict_cpp

# Show linked libraries
echo "🔗 Shared libraries used by C++ binary:"
ldd ./dict_cpp

# Run and profile with perf
echo "🏃 Running dict_cpp with perf..."
perf record -g ./dict_cpp
echo "📊 perf report for C++ (summary):"
perf report --stdio | head -20

echo "📌 For full symbol names, run:"
echo "    perf annotate"
echo "    perf script | c++filt"

echo ""
echo "=== 🧪 Python dict Benchmark ==="

# Show linked libraries for Python interpreter
echo "🔗 Shared libraries used by Python:"
ldd $(which python3)

# Run and profile with py-spy
echo "🏃 Running dict.py with py-spy..."
py-spy record -o profile_py.svg -- python3 dict.py
echo "📊 py-spy flamegraph saved as profile_py.svg"
echo "🖼️  Open this file in your browser to explore performance"

# Run and profile with perf too
echo "🏃 Running dict.py with perf..."
perf record -g python3 dict.py
echo "📊 perf report for Python (summary):"
perf report --stdio | head -20

echo "📌 For full breakdown, run:"
echo "    perf annotate"
echo "    perf script"

echo ""
echo "✅ All done! Use the SVG for Python flamegraph, and perf tools for C++ deep dive."
