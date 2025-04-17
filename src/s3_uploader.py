import os
import random
import time
from pathlib import Path
import boto3
from dotenv import load_dotenv

# The folder where source CSV files are located
DATA_FOLDER = "data-reviews"

# Time interval between uploads in seconds
UPLOAD_INTERVAL = 3

# Total number of uploads to perform
NUM_UPLOADS = 1


# Load environment variables from .env
def load_env_variables():
    load_dotenv()
    return {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "aws_region": os.getenv("AWS_REGION", "us-east-1"),
        "s3_bucket_name": os.getenv("S3_BUCKET_RAW"),
    }


# Select a random CSV file from the input folder
def get_random_csv_file(folder_path):
    csv_files = list(Path(folder_path).glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {folder_path}")
    return random.choice(csv_files)


# Upload the selected file to the S3 bucket
def upload_to_s3(s3_client, file_path, bucket_name):
    try:
        with open(file_path, "rb") as file:
            safe_key = f"uploads/{Path(file_path).name.replace(' ', '_')}"
            s3_client.upload_fileobj(file, bucket_name, safe_key)
        print(f"Successfully uploaded {file_path.name} to S3 bucket '{bucket_name}'")
    except Exception as e:
        print(f"Error uploading {file_path.name}: {str(e)}")


def main():
    # Load AWS credentials
    aws_credentials = load_env_variables()

    # Validate environment variables
    for key in ["aws_access_key_id", "aws_secret_access_key", "aws_region", "s3_bucket_name"]:
        if not aws_credentials[key]:
            raise ValueError(f"Missing required environment variable: {key.upper()}")

    # Initialize boto3 S3 client
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_credentials["aws_access_key_id"],
        aws_secret_access_key=aws_credentials["aws_secret_access_key"],
        region_name=aws_credentials["aws_region"],
    )

    print(f"📦 Starting S3 uploader. Uploading one CSV every {UPLOAD_INTERVAL} seconds...")

    count_uploads = 0
    while count_uploads < NUM_UPLOADS:
        count_uploads += 1
        try:
            file_path = get_random_csv_file(DATA_FOLDER)
            upload_to_s3(s3_client, file_path, aws_credentials["s3_bucket_name"])
            time.sleep(UPLOAD_INTERVAL)
        except Exception as e:
            print(f"⚠️  An error occurred: {str(e)}")
            time.sleep(UPLOAD_INTERVAL)


if __name__ == "__main__":
    main()
