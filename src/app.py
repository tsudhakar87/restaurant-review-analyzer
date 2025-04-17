import streamlit as st
import boto3

st.title("Upload Restaurant Review File")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    s3 = boto3.client('s3')
    s3.upload_fileobj(uploaded_file, 'tripadvisor-raw-bucket', uploaded_file.name)
    st.success("File uploaded successfully!")
