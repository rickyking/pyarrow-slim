#!/bin/bash
set -euo pipefail

# Build Arrow C++ with minimal features for PyIceberg
# This script is meant to be run inside the build container

ARROW_HOME=${ARROW_HOME:-/opt/arrow}
ARROW_SOURCE=${ARROW_SOURCE:-/build/arrow}
BUILD_DIR=${BUILD_DIR:-${ARROW_SOURCE}/cpp/build}
BUILD_TYPE=${BUILD_TYPE:-Release}
PARALLEL_JOBS=${PARALLEL_JOBS:-$(nproc)}

echo "=== Building Arrow C++ ==="
echo "ARROW_HOME: ${ARROW_HOME}"
echo "ARROW_SOURCE: ${ARROW_SOURCE}"
echo "BUILD_TYPE: ${BUILD_TYPE}"
echo "PARALLEL_JOBS: ${PARALLEL_JOBS}"

mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

cmake "${ARROW_SOURCE}/cpp" \
    -GNinja \
    -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
    -DCMAKE_INSTALL_PREFIX=${ARROW_HOME} \
    -DCMAKE_INSTALL_LIBDIR=lib \
    \
    `# === Core features for PyIceberg ===` \
    -DARROW_PARQUET=ON \
    -DARROW_FILESYSTEM=ON \
    -DARROW_COMPUTE=ON \
    -DARROW_IPC=ON \
    -DARROW_DATASET=ON \
    \
    `# === Compression codecs (common for Parquet) ===` \
    -DARROW_WITH_SNAPPY=ON \
    -DARROW_WITH_ZSTD=ON \
    -DARROW_WITH_LZ4=ON \
    -DARROW_WITH_ZLIB=ON \
    -DARROW_WITH_BROTLI=OFF \
    -DARROW_WITH_BZ2=OFF \
    \
    `# === Disable unused features for smaller size ===` \
    -DARROW_S3=ON \
    -DARROW_GCS=OFF \
    -DARROW_AZURE=OFF \
    -DARROW_HDFS=OFF \
    -DARROW_FLIGHT=OFF \
    -DARROW_FLIGHT_SQL=OFF \
    -DARROW_GANDIVA=OFF \
    -DARROW_ORC=OFF \
    -DARROW_CUDA=OFF \
    -DARROW_SUBSTRAIT=OFF \
    -DARROW_CSV=OFF \
    -DARROW_JSON=OFF \
    -DARROW_ACERO=ON \
    \
    `# === Build options ===` \
    -DARROW_BUILD_TESTS=OFF \
    -DARROW_BUILD_BENCHMARKS=OFF \
    -DARROW_BUILD_UTILITIES=OFF \
    -DARROW_DEPENDENCY_SOURCE=BUNDLED \
    -DARROW_SIMD_LEVEL=SSE4_2

echo "=== Compiling Arrow C++ ==="
ninja -j${PARALLEL_JOBS}

echo "=== Installing Arrow C++ ==="
ninja install

echo "=== Arrow C++ build complete ==="
echo "Installed to: ${ARROW_HOME}"
ls -la ${ARROW_HOME}/lib/ | head -20
