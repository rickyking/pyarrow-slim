#!/bin/bash
set -euo pipefail

# Build PyArrow wheel with bundled Arrow C++ libraries
# This script is meant to be run inside the build container after build_arrow_cpp.sh

ARROW_HOME=${ARROW_HOME:-/opt/arrow}
ARROW_SOURCE=${ARROW_SOURCE:-/build/arrow}
PYTHON_BIN=${PYTHON_BIN:-python}
OUTPUT_DIR=${OUTPUT_DIR:-/wheelhouse}
BUILD_TYPE=${BUILD_TYPE:-release}

echo "=== Building PyArrow ==="
echo "ARROW_HOME: ${ARROW_HOME}"
echo "ARROW_SOURCE: ${ARROW_SOURCE}"
echo "PYTHON_BIN: ${PYTHON_BIN}"
echo "OUTPUT_DIR: ${OUTPUT_DIR}"

# Set environment for Arrow discovery
export LD_LIBRARY_PATH="${ARROW_HOME}/lib:${ARROW_HOME}/lib64:${LD_LIBRARY_PATH:-}"
export PATH="${ARROW_HOME}/bin:${PATH}"
export Arrow_DIR="${ARROW_HOME}/lib/cmake/Arrow"
export Parquet_DIR="${ARROW_HOME}/lib/cmake/Parquet"
export ArrowDataset_DIR="${ARROW_HOME}/lib/cmake/ArrowDataset"

# PyArrow build configuration - match C++ build
export PYARROW_WITH_PARQUET=1
export PYARROW_WITH_DATASET=1
export PYARROW_WITH_FILESYSTEM=1
export PYARROW_WITH_COMPUTE=1
export PYARROW_WITH_IPC=1

# Disable features not built in C++
export PYARROW_WITH_S3=0
export PYARROW_WITH_GCS=0
export PYARROW_WITH_AZURE=0
export PYARROW_WITH_HDFS=0
export PYARROW_WITH_FLIGHT=0
export PYARROW_WITH_GANDIVA=0
export PYARROW_WITH_ORC=0
export PYARROW_WITH_CUDA=0
export PYARROW_WITH_SUBSTRAIT=0
export PYARROW_WITH_ACERO=0

# Bundle Arrow C++ libraries into the wheel
export PYARROW_BUNDLE_ARROW_CPP=1

# Optional: Extra CMake options
export PYARROW_CMAKE_OPTIONS="-DARROW_SIMD_LEVEL=SSE4_2"

cd "${ARROW_SOURCE}/python"

# Install build dependencies
${PYTHON_BIN} -m pip install --upgrade pip
${PYTHON_BIN} -m pip install cython numpy setuptools wheel setuptools_scm

echo "=== Building PyArrow wheel ==="
${PYTHON_BIN} setup.py build_ext --build-type=${BUILD_TYPE} bdist_wheel

mkdir -p "${OUTPUT_DIR}"

# If auditwheel is available, repair the wheel for manylinux compatibility
if command -v auditwheel &> /dev/null; then
    echo "=== Repairing wheel for manylinux compatibility ==="
    auditwheel repair dist/*.whl -w "${OUTPUT_DIR}"
else
    echo "=== Copying wheel (auditwheel not available) ==="
    cp dist/*.whl "${OUTPUT_DIR}/"
fi

echo "=== PyArrow build complete ==="
echo "Wheel(s) in: ${OUTPUT_DIR}"
ls -lh "${OUTPUT_DIR}"/*.whl
