"""
Operators for R2 (S3-compatible) storage operations.
Uses Airflow's S3Hook with custom endpoint URL for Cloudflare R2.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from airflow.providers.amazon.aws.hooks.s3 import S3Hook


def get_r2_hook(conn_id: str = "r2_default") -> S3Hook:
    """
    Get an S3Hook configured for R2.

    The connection should be configured with:
    - conn_type: aws
    - extra: {"endpoint_url": "https://<account_id>.r2.cloudflarestorage.com"}
    """
    return S3Hook(aws_conn_id=conn_id)


def compute_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """Compute hash of a file."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def create_metadata(
    file_path: str,
    remote_filename: str,
    remote_path: str,
    remote_version: str = "1",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """
    Create metadata dict for a file.

    Args:
        file_path: Local path to the file
        remote_filename: Name of the file on remote storage
        remote_path: Remote path (without filename)
        remote_version: Version number for the remote path
        tags: List of tags for the file

    Returns:
        Metadata dictionary
    """
    file_stat = os.stat(file_path)
    file_hash = compute_file_hash(file_path)

    metadata = {
        "local_filename": os.path.basename(file_path),
        "remote_filename": remote_filename,
        "remote_path": remote_path,
        "remote_version": remote_version,
        "size_bytes": file_stat.st_size,
        "sha256": file_hash,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tags": tags or [],
    }

    return metadata


def upload_file_to_r2(
    local_path: str,
    bucket: str,
    remote_path: str,
    remote_filename: str,
    remote_version: str = "1",
    conn_id: str = "r2_default",
    tags: list[str] | None = None,
    upload_metadata: bool = True,
) -> dict[str, str]:
    """
    Upload a file to R2 storage with optional metadata.

    Args:
        local_path: Path to the local file
        bucket: R2 bucket name
        remote_path: Base path on R2 (e.g., "/boundaries/coastline/geopackage")
        remote_filename: Name for the file on R2
        remote_version: Version string for path construction
        conn_id: Airflow connection ID for R2
        tags: List of tags for metadata
        upload_metadata: Whether to upload a .metadata file

    Returns:
        Dict with keys: file_key, metadata_key (if uploaded), sha256
    """
    hook = get_r2_hook(conn_id)

    # Construct the full S3 key
    if remote_version:
        key = f"{remote_path.strip('/')}/v{remote_version}/{remote_filename}"
    else:
        key = f"{remote_path.strip('/')}/{remote_filename}"

    # Also upload to "latest" location
    latest_key = f"{remote_path.strip('/')}/latest/{remote_filename}"

    # Upload main file
    hook.load_file(
        filename=local_path,
        bucket_name=bucket,
        key=key,
        replace=True,
    )

    # Upload to latest
    hook.load_file(
        filename=local_path,
        bucket_name=bucket,
        key=latest_key,
        replace=True,
    )

    result = {
        "file_key": key,
        "latest_key": latest_key,
        "sha256": compute_file_hash(local_path),
    }

    # Create and upload metadata
    if upload_metadata:
        metadata = create_metadata(
            file_path=local_path,
            remote_filename=remote_filename,
            remote_path=remote_path,
            remote_version=remote_version,
            tags=tags,
        )

        metadata_key = f"{key}.metadata"
        hook.load_string(
            string_data=json.dumps(metadata, indent=2),
            bucket_name=bucket,
            key=metadata_key,
            replace=True,
        )
        result["metadata_key"] = metadata_key

    return result


def download_file_from_r2(
    bucket: str,
    remote_key: str,
    local_path: str,
    conn_id: str = "r2_default",
) -> str:
    """
    Download a file from R2 storage.

    Args:
        bucket: R2 bucket name
        remote_key: Full key/path on R2
        local_path: Local path to save the file
        conn_id: Airflow connection ID for R2

    Returns:
        Local path to the downloaded file
    """
    hook = get_r2_hook(conn_id)

    # Ensure parent directory exists
    Path(local_path).parent.mkdir(parents=True, exist_ok=True)

    # Download file
    obj = hook.get_key(key=remote_key, bucket_name=bucket)
    with open(local_path, "wb") as f:
        obj.download_fileobj(f)

    return local_path


def list_metadata_files(
    bucket: str,
    prefix: str,
    conn_id: str = "r2_default",
) -> list[str]:
    """
    List all .metadata files under a prefix.

    Args:
        bucket: R2 bucket name
        prefix: Prefix to search under
        conn_id: Airflow connection ID for R2

    Returns:
        List of metadata file keys
    """
    hook = get_r2_hook(conn_id)
    keys = hook.list_keys(bucket_name=bucket, prefix=prefix.strip("/"))

    return [k for k in (keys or []) if k.endswith(".metadata")]


def read_metadata_file(
    bucket: str,
    key: str,
    conn_id: str = "r2_default",
) -> dict[str, Any]:
    """
    Read and parse a metadata file from R2.

    Args:
        bucket: R2 bucket name
        key: Key of the metadata file
        conn_id: Airflow connection ID for R2

    Returns:
        Parsed metadata dictionary
    """
    hook = get_r2_hook(conn_id)
    content = hook.read_key(key=key, bucket_name=bucket)
    return json.loads(content)
