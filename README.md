# Slim PyArrow for PyIceberg

A minimal PyArrow build optimized for [PyIceberg](https://py.iceberg.apache.org/) with [Cloudflare R2 Data Catalog](https://developers.cloudflare.com/r2/data-catalog/).

## Why?

The standard PyArrow wheel is ~200MB, which is too large for size-constrained environments like:
- Vercel serverless functions (250MB limit)
- Cloudflare Workers
- AWS Lambda

This repository builds a slim PyArrow (~50-70MB) with only the features needed for PyIceberg.

## Installation

### From GitHub Releases (Recommended)

```bash
# Install the latest release
pip install pyarrow --no-index --find-links https://github.com/YOUR_USERNAME/cryo-nebula/releases/latest/download/

# Or install a specific version
pip install https://github.com/YOUR_USERNAME/cryo-nebula/releases/download/v18.1.0/pyarrow-18.1.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
```

### From Artifacts (Development)

Download the wheel from the [GitHub Actions artifacts](../../actions) and install:

```bash
pip install pyarrow-18.1.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
```

## Supported Platforms

| Platform | Python Versions |
|----------|-----------------|
| Linux x86_64 (amd64) | 3.10, 3.11, 3.12 |
| Linux aarch64 (arm64) | 3.10, 3.11, 3.12 |

## Enabled Features

| Feature | Status | Description |
|---------|--------|-------------|
| `ARROW_PARQUET` | ✅ ON | Parquet file read/write |
| `ARROW_FILESYSTEM` | ✅ ON | Filesystem abstraction |
| `ARROW_COMPUTE` | ✅ ON | Compute kernels |
| `ARROW_IPC` | ✅ ON | Inter-process communication |
| `ARROW_DATASET` | ✅ ON | Dataset API for partitioned data |
| Snappy | ✅ ON | Compression codec |
| ZSTD | ✅ ON | Compression codec |
| LZ4 | ✅ ON | Compression codec |
| ZLIB | ✅ ON | Compression codec |

## Disabled Features (for smaller size)

| Feature | Reason |
|---------|--------|
| `ARROW_S3` | Use `s3fs` instead for R2/S3 access |
| `ARROW_GCS` | Not needed for R2 |
| `ARROW_AZURE` | Not needed for R2 |
| `ARROW_HDFS` | Not needed |
| `ARROW_FLIGHT` | Not needed |
| `ARROW_GANDIVA` | LLVM expression compiler not needed |
| `ARROW_ORC` | ORC format not needed |
| `ARROW_CSV` | CSV not needed |
| `ARROW_JSON` | JSON not needed |
| `ARROW_CUDA` | GPU support not needed |
| `ARROW_SUBSTRAIT` | Query planning not needed |
| `ARROW_ACERO` | Query execution not needed |

## Usage with PyIceberg

```python
# Install dependencies
# pip install pyiceberg[s3fs] pyarrow  # Use slim wheel

from pyiceberg.catalog import load_catalog

# Connect to Cloudflare R2 Data Catalog
catalog = load_catalog(
    "r2",
    **{
        "type": "rest",
        "uri": "https://<account-id>.r2.cloudflarestorage.com",
        "credential": "<access-key-id>:<secret-access-key>",
        "warehouse": "s3://<bucket-name>",
        "s3.endpoint": "https://<account-id>.r2.cloudflarestorage.com",
        "s3.access-key-id": "<access-key-id>",
        "s3.secret-access-key": "<secret-access-key>",
        "s3.region": "auto",
    }
)

# List tables
tables = catalog.list_tables("default")

# Read a table
table = catalog.load_table("default.my_table")
df = table.scan().to_pandas()
```

## Building Locally

### Using Docker

```bash
# Build for the current platform
docker build -f docker/Dockerfile.build -t slim-pyarrow-builder .

# Extract the wheel
docker create --name extract slim-pyarrow-builder
docker cp extract:/pyarrow-*.whl ./
docker rm extract
```

### Manual Build

1. Clone Apache Arrow:
   ```bash
   git clone --depth 1 --branch apache-arrow-18.1.0 https://github.com/apache/arrow.git
   ```

2. Build Arrow C++:
   ```bash
   export ARROW_HOME=/opt/arrow
   ./scripts/build_arrow_cpp.sh
   ```

3. Build PyArrow:
   ```bash
   ./scripts/build_pyarrow.sh
   ```

## Creating a Release

1. Tag the commit:
   ```bash
   git tag v18.1.0
   git push origin v18.1.0
   ```

2. GitHub Actions will automatically:
   - Build wheels for all platforms
   - Create a GitHub Release with the wheels
   - Make them available for `pip install`

## License

This project builds Apache Arrow, which is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
