import json
import boto3
import pymysql  
import os
import io
import string
import pandas as pd


# Environment variables from AWS console
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = int(os.environ.get('DB_PORT', '3306')) 

# Sample positive and negative word lists
positive_words = {'good', 'great', 'excellent', 'amazing', 'fantastic', 'delicious', 'friendly', 'love', 'wonderful'}
negative_words = {'bad', 'terrible', 'awful', 'worst', 'slow', 'unfriendly', 'disgusting', 'rude', 'hate'}
 
# Clean text
def clean_text(text):
    if pd.isna(text):
        return ""
    return text.replace('\n', ' ').strip().lower()

# Simple rule-based sentiment function
def get_sentiment(text):
    text = text.translate(str.maketrans('', '', string.punctuation)).lower()
    tokens = text.split()
    score = 0
    for word in tokens:
        if word in positive_words:
            score += 1
        elif word in negative_words:
            score -= 1
    return round(score / len(tokens), 3) if tokens else 0


# Lambda handler function
def lambda_handler(event, context):
    print("✅ Lambda Triggered")
    print("Event:", json.dumps(event))
    s3 = boto3.client('s3')
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Read CSV from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(io.BytesIO(response['Body'].read()))

    # Standardize column names
    df.columns = df.columns.str.strip()
    df['Review Comment'] = df['Reveiw Comment'].apply(clean_text)
    df['Sentiment'] = df['Review Comment'].apply(get_sentiment)

    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            cursorclass=pymysql.cursors.DictCursor
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
