# Slim PyArrow for PyIceberg

A minimal PyArrow build optimized for [PyIceberg](https://py.iceberg.apache.org/) with [Cloudflare R2 Data Catalog](https://developers.cloudflare.com/r2/data-catalog/).

## Why?

The standard PyArrow wheel is ~200MB, which is too large for size-constrained environments like:
- Vercel serverless functions (250MB limit)
- Cloudflare Workers
- AWS Lambda

This repository builds a slim PyArrow (~70-90MB) with only the features needed for PyIceberg.

## Installation

### From GitHub Releases (Recommended)

```bash
# Install the latest release
pip install pyarrow --no-index --find-links https://github.com/rickyking/pyarrow-slim/releases/latest/download/

# Or install a specific version
pip install https://github.com/rickyking/pyarrow-slim/releases/download/v22.0.0/pyarrow-22.0.0-cp312-cp312-manylinux_2_28_x86_64.whl
```

### From Artifacts (Development)

Download the wheel from the [GitHub Actions artifacts](../../actions) and install:

```bash
pip install pyarrow-22.0.0-cp312-cp312-manylinux_2_28_x86_64.whl
```

## Supported Platforms

| Platform | Python Versions |
|----------|-----------------|
| Linux x86_64 (amd64) | 3.12, 3.13 |
| Linux aarch64 (arm64) | 3.12, 3.13 |

## Enabled Features

| Feature | Status | Description |
|---------|--------|-------------|
| `ARROW_PARQUET` | ✅ ON | Parquet file read/write |
| `ARROW_FILESYSTEM` | ✅ ON | Filesystem abstraction |
| `ARROW_COMPUTE` | ✅ ON | Compute kernels |
| `ARROW_IPC` | ✅ ON | Inter-process communication |
| `ARROW_DATASET` | ✅ ON | Dataset API for partitioned data |
| `ARROW_CSV` | ✅ ON | CSV read/write |
| `ARROW_JSON` | ✅ ON | JSON read/write |
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

## Build Configuration

- **Arrow Version**: 22.0.0 (latest)
- **Base Image**: `manylinux_2_28` (AlmaLinux 8)
- **ARM64 Builds**: Native GitHub runners (`ubuntu-24.04-arm`)

## Creating a Release

1. Tag the commit:
   ```bash
   git tag v22.0.0
   git push origin v22.0.0
   ```

2. GitHub Actions will automatically:
   - Build wheels for all platforms (amd64 + arm64)
   - Create a GitHub Release with the wheels
   - Make them available for `pip install`

## License

This project builds Apache Arrow, which is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
