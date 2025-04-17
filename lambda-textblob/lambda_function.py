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

# lambda function
# boto3: AWS SDK to connect to AWS services
def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Read CSV from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(io.BytesIO(response['Body'].read()))

    # Rename columns for consistency
    df.columns = df.columns.str.strip()
    
    df['Review Comment'] = df['Reveiw Comment'].apply(clean_text)
    df['Sentiment'] = df['Review Comment'].apply(get_sentiment)

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
                INSERT INTO reviews (
                    title,
                    number_of_reviews,
                    category,
                    review_comment,
                    sentiment,
                    popular_food,
                    online_order
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                row['Title'],
                int(str(row['Number of review']).replace(",", "")),
                row['Catagory'],
                row['Review Comment'],
                row['Sentiment'],
                row['Popular food'],
                row['Online Order']
            ))

        conn.commit()
        cur.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps(f"Successfully processed {len(df)} rows from {key}")
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Failed to write to RDS')
        }
