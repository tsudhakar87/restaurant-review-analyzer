import json
import boto3
import pandas as pd
import nltk
from textblob import TextBlob # use this library for sentiment analysis
import psycopg2 #postgresql database adapter
import os
import io

nltk.download('punkt')

# env variables of rds instance from aws console
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ.get('DB_PORT', '5432')

# clean text
def clean_text(text):
    if pd.isna(text):
        return ""
    return text.replace('\n', ' ').strip()

# use text blob library to get sentiment
def get_sentiment(text):
    return TextBlob(text).sentiment.polarity
    # from documentation:
        # The polarity score is a float within the range [-1.0, 1.0]. 
        # The subjectivity is a float within the range [0.0, 1.0] 
        # where 0.0 is very objective and 1.0 is very subjective.

# 
def lambda_handler(event, context):
    # Get bucket name and object key from the event
    s3 = boto3.client('s3')
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Load the CSV from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(io.BytesIO(response['Body'].read()))

    # Clean and analyze
    df['Review'] = df['Review'].apply(clean_text)
    df['Sentiment'] = df['Review'].apply(get_sentiment)

    # Write to RDS
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()

        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO reviews (restaurant_name, review, sentiment)
                VALUES (%s, %s, %s)
            """, (row['Restaurant_Name'], row['Review'], row['Sentiment']))

        conn.commit()
        cur.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps(f'Successfully processed {len(df)} reviews from {key}')
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Failed to write to RDS')
        }
