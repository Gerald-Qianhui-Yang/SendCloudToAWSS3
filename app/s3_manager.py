import os
import json
import boto3
from config.logger import setup_logger

logger = setup_logger(__name__)

class S3Manager:
    """Manages AWS S3 operations for webhook data storage"""

    def __init__(self):
        """Initialize S3 client with AWS credentials"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.bucket_name = os.getenv('AWS_S3_BUCKET')
            logger.info(f"S3Manager initialized for bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize S3Manager: {str(e)}")
            self.s3_client = None

    def upload_file(self, file_path, s3_key):
        """
        Upload local file to S3

        Args:
            file_path: Local file path to upload
            s3_key: S3 object key (path in S3)

        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            if not self.s3_client or not self.bucket_name:
                logger.warning("S3 client or bucket not configured")
                return False

            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            logger.info(f"File uploaded to S3: s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"S3 file upload failed for {s3_key}: {str(e)}")
            return False

    def upload_json(self, data, s3_key):
        """
        Upload Python dictionary as JSON to S3

        Args:
            data: Dictionary to upload as JSON
            s3_key: S3 object key (path in S3)

        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            if not self.s3_client or not self.bucket_name:
                logger.warning("S3 client or bucket not configured")
                return False

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(data, ensure_ascii=False, indent=2),
                ContentType='application/json'
            )
            logger.info(f"JSON uploaded to S3: s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"S3 JSON upload failed for {s3_key}: {str(e)}")
            return False
