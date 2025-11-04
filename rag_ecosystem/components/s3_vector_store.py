"""S3-backed vector store for persistence in AWS."""

import boto3
import json
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from rag_ecosystem.utils.logger import setup_logger

logger = setup_logger("s3_vector_store")


class S3VectorStorePersistence:
    """Manage ChromaDB persistence to/from S3."""

    def __init__(
        self,
        bucket_name: str,
        s3_prefix: str = "vector_store",
        local_path: str = "/tmp/vector_store",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
    ):
        """Initialize S3 vector store persistence.

        Args:
            bucket_name: S3 bucket name
            s3_prefix: S3 prefix for vector store files
            local_path: Local path for temporary storage
            aws_access_key_id: AWS access key (uses IAM role if None)
            aws_secret_access_key: AWS secret key (uses IAM role if None)
            region_name: AWS region
        """
        self.bucket_name = bucket_name
        self.s3_prefix = s3_prefix
        self.local_path = Path(local_path)
        self.region_name = region_name or "us-east-1"

        # Initialize S3 client
        if aws_access_key_id and aws_secret_access_key:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=self.region_name,
            )
        else:
            self.s3_client = boto3.client("s3", region_name=self.region_name)

        # Create local directory
        self.local_path.mkdir(parents=True, exist_ok=True)

    def download_from_s3(self) -> bool:
        """Download vector store from S3 to local storage.

        Returns:
            True if successful, False if not found
        """
        try:
            logger.info(f"Downloading vector store from S3: {self.bucket_name}/{self.s3_prefix}")

            # List all objects with prefix
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=self.s3_prefix
            )

            if "Contents" not in response:
                logger.warning("No vector store found in S3")
                return False

            # Download each file
            for obj in response["Contents"]:
                key = obj["Key"]
                # Get relative path
                relative_path = key[len(self.s3_prefix):].lstrip("/")

                if not relative_path:  # Skip prefix itself
                    continue

                local_file_path = self.local_path / relative_path
                local_file_path.parent.mkdir(parents=True, exist_ok=True)

                logger.info(f"Downloading {key} to {local_file_path}")
                self.s3_client.download_file(
                    self.bucket_name, key, str(local_file_path)
                )

            logger.info("Vector store downloaded successfully")
            return True

        except Exception as e:
            logger.error(f"Error downloading vector store: {str(e)}")
            return False

    def upload_to_s3(self) -> bool:
        """Upload local vector store to S3.

        Returns:
            True if successful
        """
        try:
            logger.info(f"Uploading vector store to S3: {self.bucket_name}/{self.s3_prefix}")

            if not self.local_path.exists():
                logger.error(f"Local vector store path does not exist: {self.local_path}")
                return False

            # Upload all files in directory
            uploaded_count = 0
            for local_file in self.local_path.rglob("*"):
                if local_file.is_file():
                    # Get relative path
                    relative_path = local_file.relative_to(self.local_path)
                    s3_key = f"{self.s3_prefix}/{relative_path}"

                    logger.info(f"Uploading {local_file} to {s3_key}")
                    self.s3_client.upload_file(
                        str(local_file), self.bucket_name, s3_key
                    )
                    uploaded_count += 1

            logger.info(f"Uploaded {uploaded_count} files to S3")
            return True

        except Exception as e:
            logger.error(f"Error uploading vector store: {str(e)}")
            return False

    def sync_from_s3(self) -> bool:
        """Sync vector store from S3 to local (download if exists).

        Returns:
            True if synced from S3, False if using empty local
        """
        return self.download_from_s3()

    def sync_to_s3(self) -> bool:
        """Sync local vector store to S3 (upload).

        Returns:
            True if successful
        """
        return self.upload_to_s3()

    def clear_local(self) -> None:
        """Clear local vector store directory."""
        if self.local_path.exists():
            shutil.rmtree(self.local_path)
            self.local_path.mkdir(parents=True, exist_ok=True)
            logger.info("Cleared local vector store")

    def get_local_path(self) -> str:
        """Get the local vector store path.

        Returns:
            Local path as string
        """
        return str(self.local_path)
