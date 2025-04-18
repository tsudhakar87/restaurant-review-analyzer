import streamlit as st
import boto3
import pandas as pd
import pymysql
import matplotlib.pyplot as plt
import os 

st.title("TripAdvisor Review Uploader + Dashboard")

uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file:
    s3 = boto3.client("s3")
    try:
        s3.upload_fileobj(
            uploaded_file,
            "tripadvisor-raw-bucket", 
            f"uploads/{uploaded_file.name}"
        )
        st.success("File uploaded to S3 and is being processed!")
    except Exception as e:
        st.error(f"Upload failed: {e}")

st.markdown("---")



# Function to Load Data from RDS 
@st.cache_data(ttl=60)
def load_reviews():
    try:
        conn = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database='reviews',
            port=os.getenv('DB_PORT')
        )
        query = "SELECT * FROM reviews"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Failed to connect to RDS: {e}")
        return pd.DataFrame()

# Display Data + Visualizations 
if st.button("Load Review Data"):
    df = load_reviews()

    if not df.empty:
        st.subheader("Raw Review Table")
        st.dataframe(df.head(20))

        st.subheader("Sentiment Distribution")
        fig1, ax1 = plt.subplots()
        df['sentiment'].hist(bins=20, ax=ax1)
        ax1.set_xlabel("Sentiment Score")
        ax1.set_ylabel("Count")
        st.pyplot(fig1)

        st.subheader("Avg Sentiment by Category")
        cat_sent = df.groupby("category")["sentiment"].mean().sort_values(ascending=False)
        st.bar_chart(cat_sent)
    else:
        st.warning("No data available yet. Try again shortly after upload.")

        