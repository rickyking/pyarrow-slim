#!/usr/bin/env python3
"""
Test script to verify slim PyArrow works with PyIceberg and Cloudflare R2 Data Catalog.

Usage:
    # Set environment variables
    export R2_ACCOUNT_ID="your-account-id"
    export R2_ACCESS_KEY_ID="your-access-key"
    export R2_SECRET_ACCESS_KEY="your-secret-key"
    export R2_BUCKET_NAME="your-bucket"

    # Run the test
    python test_r2_catalog.py
"""

import os
import sys


def check_pyarrow_features():
    """Verify PyArrow has the required features."""
    print("=" * 60)
    print("Checking PyArrow Features")
    print("=" * 60)

    import pyarrow

    print(f"✓ PyArrow version: {pyarrow.__version__}")

    # Check required modules
    required_modules = [
        ("pyarrow.parquet", "Parquet support"),
        ("pyarrow.compute", "Compute kernels"),
        ("pyarrow.dataset", "Dataset API"),
        ("pyarrow.fs", "Filesystem interface"),
    ]

    for module_name, description in required_modules:
        try:
            __import__(module_name)
            print(f"✓ {description}: available")
        except ImportError as e:
            print(f"✗ {description}: NOT available - {e}")
            return False

    # Check S3 is NOT available (expected - we use s3fs instead)
    try:
        from pyarrow.fs import S3FileSystem

        print("⚠ S3FileSystem: available (unexpected, but OK)")
    except ImportError:
        print("✓ S3FileSystem: not available (expected - use s3fs)")

    print()
    return True


def check_pyiceberg():
    """Verify PyIceberg is installed correctly."""
    print("=" * 60)
    print("Checking PyIceberg")
    print("=" * 60)

    try:
        import pyiceberg

        print(f"✓ PyIceberg version: {pyiceberg.__version__}")
    except ImportError:
        print("✗ PyIceberg not installed")
        print("  Run: pip install 'pyiceberg[s3fs]'")
        return False

    try:
        from pyiceberg.catalog import load_catalog

        print("✓ Catalog loading available")
    except ImportError as e:
        print(f"✗ Catalog loading failed: {e}")
        return False

    print()
    return True


def test_r2_catalog():
    """Test connection to Cloudflare R2 Data Catalog."""
    print("=" * 60)
    print("Testing Cloudflare R2 Data Catalog")
    print("=" * 60)

    # Get configuration from environment
    account_id = os.environ.get("R2_ACCOUNT_ID")
    access_key = os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    bucket_name = os.environ.get("R2_BUCKET_NAME")

    # New variables from reference implementation
    catalog_uri = os.environ.get("R2_CATALOG_URI")
    catalog_token = os.environ.get("R2_CATALOG_TOKEN")
    warehouse = os.environ.get("R2_WAREHOUSE")

    if not all([account_id, access_key, secret_key, catalog_uri, catalog_token]):
        print("⚠ R2 credentials not fully configured. Skipping catalog test.")
        print("  Set these environment variables to test:")
        print("    R2_ACCOUNT_ID")
        print("    R2_ACCESS_KEY_ID")
        print("    R2_SECRET_ACCESS_KEY")
        print("    R2_CATALOG_URI")
        print("    R2_CATALOG_TOKEN")
        print()
        return True  # Not a failure, just skipped

    print(f"Account ID: {account_id[:8]}...")
    print(f"Catalog URI: {catalog_uri}")

    from pyiceberg.catalog import load_catalog

    try:
        catalog = load_catalog(
            "r2",
            **{
                "type": "rest",
                "uri": catalog_uri,
                "token": catalog_token,
                "warehouse": warehouse or f"s3://{bucket_name}",
                "s3.endpoint": f"https://{account_id}.r2.cloudflarestorage.com",
                "s3.access-key-id": access_key,
                "s3.secret-access-key": secret_key,
                "s3.region": "auto",
            },
        )
        print("✓ Connected to R2 Catalog")

        # List namespaces
        try:
            namespaces = catalog.list_namespaces()
            print(f"✓ Found {len(namespaces)} namespace(s)")
            for ns in namespaces[:5]:
                print(f"    - {'.'.join(ns)}")
        except Exception as e:
            print(f"⚠ Could not list namespaces: {e}")
            # If listing fails, we can't really proceed with tables
            return False

        # List tables in default namespace (or first available)
        check_namespace = "default"
        if namespaces and "default" not in [n[0] for n in namespaces if n]:
            check_namespace = namespaces[0][0]

        print(f"Checking tables in '{check_namespace}'...")
        try:
            tables = catalog.list_tables(check_namespace)
            print(f"✓ Found {len(tables)} table(s) in '{check_namespace}' namespace")
            for table_id in tables[:5]:
                print(f"    - {table_id}")
        except Exception as e:
            print(f"⚠ Could not list tables: {e}")

        # Test reading specifically ('dashboard', 'breadth')
        target_table_name = "dashboard.breadth"
        print(f"\nTesting reading table: {target_table_name}")
        try:
            table = catalog.load_table(target_table_name)
            print(f"✓ Loaded table {target_table_name}")

            # Scan a few rows to verify data access
            print("  Scanning first 5 rows...")
            scan = table.scan(limit=5)
            arrow_table = scan.to_arrow()
            print(f"✓ Read {arrow_table.num_rows} rows from {target_table_name}")

            if arrow_table.num_rows > 0:
                print("  Sample data:")
                # Print first row as sample, checking for sensitive fields if any?
                # Just printing keys/values safely
                first_row = arrow_table.to_pylist()[0]
                print(f"  {first_row}")
            else:
                print("  (Table is empty)")

        except Exception as e:
            print(f"✗ Failed to read table {target_table_name}: {e}")
            return False

    except Exception as e:
        print(f"✗ Failed to connect to R2 Catalog: {e}")
        return False

    print()
    return True


def test_parquet_roundtrip():
    """Test Parquet read/write functionality."""
    print("=" * 60)
    print("Testing Parquet Read/Write")
    print("=" * 60)

    import pyarrow as pa
    import pyarrow.parquet as pq
    import tempfile
    import os

    # Create test data
    table = pa.table(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "value": [1.1, 2.2, 3.3, 4.4, 5.5],
        }
    )
    print(f"✓ Created test table with {table.num_rows} rows")

    # Write to Parquet
    with tempfile.TemporaryDirectory() as tmpdir:
        parquet_file = os.path.join(tmpdir, "test.parquet")

        pq.write_table(table, parquet_file, compression="snappy")
        file_size = os.path.getsize(parquet_file)
        print(f"✓ Wrote Parquet file ({file_size} bytes, snappy compression)")

        # Read back
        read_table = pq.read_table(parquet_file)
        print(f"✓ Read Parquet file ({read_table.num_rows} rows)")

        # Verify
        if table.equals(read_table):
            print("✓ Data roundtrip verified")
        else:
            print("✗ Data mismatch after roundtrip")
            return False

    print()
    return True


def main():
    """Run all tests."""
    print()
    print("Slim PyArrow + PyIceberg + Cloudflare R2 Test")
    print("=" * 60)
    print()

    all_passed = True

    if not check_pyarrow_features():
        all_passed = False

    if not check_pyiceberg():
        all_passed = False

    if not test_parquet_roundtrip():
        all_passed = False

    if not test_r2_catalog():
        all_passed = False

    print("=" * 60)
    if all_passed:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
