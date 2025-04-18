import streamlit as st
import boto3
import os 


import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError

# UI title
st.title("Upload a Restaurant Review File")

# File uploader component
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
x
if uploaded_file is not None:
    try:
        # Configure your S3 client
        s3 = boto3.client(
            's3',
            region_name='us-east-2',  # Update if you're in another region
            aws_access_key_id= os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key= os.environ['AWS_SECRET_ACCESS_KEY']
        )

        # Upload to S3 (triggering Lambda automatically)
        s3.upload_fileobj(
            uploaded_file,
            'ds4300review-bucket-raw',  # Your raw bucket
            f"uploads/{uploaded_file.name}"
        )

        st.success(f" '{uploaded_file.name}' uploaded successfully!")
        st.info("Your file is being processed. Check back later for analytics.")

    except NoCredentialsError:
        st.error(" AWS credentials not found. Make sure they're set correctly.")
    except Exception as e:
        st.error(f"Upload failed: {e}")

