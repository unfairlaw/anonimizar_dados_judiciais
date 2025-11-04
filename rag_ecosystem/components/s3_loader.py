"""S3 document loader for AWS integration."""

import boto3
from typing import List, Dict, Optional, Any
from pathlib import Path
import tempfile
from langchain_core.documents import Document
from rag_ecosystem.utils.logger import setup_logger

logger = setup_logger("s3_loader")


class S3DocumentLoader:
    """Load documents from AWS S3 bucket."""

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
    ):
        """Initialize S3 document loader.

        Args:
            bucket_name: S3 bucket name
            aws_access_key_id: AWS access key (uses IAM role if None)
            aws_secret_access_key: AWS secret key (uses IAM role if None)
            region_name: AWS region (defaults to us-east-1)
        """
        self.bucket_name = bucket_name
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
            # Use IAM role credentials (recommended for EC2/Lambda)
            self.s3_client = boto3.client("s3", region_name=self.region_name)

    def list_files(
        self, prefix: str = "", suffix: str = ""
    ) -> List[str]:
        """List files in S3 bucket.

        Args:
            prefix: Filter by prefix (folder path)
            suffix: Filter by suffix (file extension)

        Returns:
            List of S3 object keys
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )

            if "Contents" not in response:
                logger.warning(f"No objects found in bucket {self.bucket_name} with prefix {prefix}")
                return []

            files = [
                obj["Key"]
                for obj in response["Contents"]
                if not obj["Key"].endswith("/")  # Exclude folders
            ]

            if suffix:
                files = [f for f in files if f.endswith(suffix)]

            logger.info(f"Found {len(files)} files in S3")
            return files

        except Exception as e:
            logger.error(f"Error listing S3 files: {str(e)}")
            raise

    def load_file(self, key: str) -> str:
        """Load a single file from S3.

        Args:
            key: S3 object key

        Returns:
            File content as string
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            content = response["Body"].read()

            # Try to decode as text
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                # Try latin-1 encoding
                return content.decode("latin-1")

        except Exception as e:
            logger.error(f"Error loading file {key}: {str(e)}")
            raise

    def load_file_to_temp(self, key: str) -> str:
        """Download S3 file to temporary location.

        Useful for binary files (PDFs, DOCX, etc.)

        Args:
            key: S3 object key

        Returns:
            Path to temporary file
        """
        try:
            # Create temp file with same extension
            suffix = Path(key).suffix
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=suffix
            )

            self.s3_client.download_file(
                self.bucket_name, key, temp_file.name
            )

            logger.info(f"Downloaded {key} to {temp_file.name}")
            return temp_file.name

        except Exception as e:
            logger.error(f"Error downloading file {key}: {str(e)}")
            raise

    def load_documents(
        self, prefix: str = "", suffix: str = ".txt"
    ) -> List[Document]:
        """Load multiple documents from S3 as LangChain documents.

        Args:
            prefix: S3 prefix (folder path)
            suffix: File extension filter

        Returns:
            List of Document objects
        """
        files = self.list_files(prefix=prefix, suffix=suffix)
        documents = []

        for key in files:
            try:
                content = self.load_file(key)
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": f"s3://{self.bucket_name}/{key}",
                        "bucket": self.bucket_name,
                        "key": key,
                        "filename": Path(key).name,
                    },
                )
                documents.append(doc)
                logger.info(f"Loaded document: {key}")

            except Exception as e:
                logger.error(f"Failed to load {key}: {str(e)}")
                continue

        logger.info(f"Loaded {len(documents)} documents from S3")
        return documents

    def upload_file(self, local_path: str, s3_key: str) -> None:
        """Upload a file to S3.

        Args:
            local_path: Local file path
            s3_key: Destination S3 key
        """
        try:
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key)
            logger.info(f"Uploaded {local_path} to s3://{self.bucket_name}/{s3_key}")

        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise

    def file_exists(self, key: str) -> bool:
        """Check if a file exists in S3.

        Args:
            key: S3 object key

        Returns:
            True if file exists
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except:
            return False

    def get_file_metadata(self, key: str) -> Dict[str, Any]:
        """Get metadata for an S3 object.

        Args:
            key: S3 object key

        Returns:
            Metadata dictionary
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name, Key=key
            )

            return {
                "size": response["ContentLength"],
                "last_modified": response["LastModified"],
                "content_type": response.get("ContentType", "unknown"),
                "etag": response["ETag"],
            }

        except Exception as e:
            logger.error(f"Error getting metadata for {key}: {str(e)}")
            raise
