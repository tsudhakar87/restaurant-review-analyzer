# S3 JSON Uploader

A Python CLI application that randomly selects and uploads JSON files from a specified folder to an AWS S3 bucket at regular intervals.

## Requirements

- Python 3.11
- AWS account with S3 access
- Required Python packages (see requirements.txt)

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your AWS credentials:
   ```bash
   cp .env.example .env
   ```
4. Edit the `.env` file with your AWS credentials
5. Update the configuration variables in `src/s3_uploader.py`:
   - `DATA_FOLDER`: Path to your JSON files
   - `UPLOAD_INTERVAL`: Time between uploads in seconds
   - `S3_BUCKET_NAME`: Your target S3 bucket name

## Usage

Run the script:

```bash
python src/s3_uploader.py
```

The script will:

1. Load AWS credentials from the .env file
2. Connect to your S3 bucket
3. Randomly select a JSON file from the specified folder
4. Upload it to the S3 bucket
5. Wait for the specified interval
6. Repeat the process

## Project Structure

```
.
├── data-news-articles/     # Folder containing JSON files to upload
├── src/
│   └── s3_uploader.py     # Main script
├── .env                   # AWS credentials (not in version control)
├── .env.example          # Template for .env file
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Security Notes

- Never commit your `.env` file to version control
- Keep your AWS credentials secure
- Use appropriate IAM roles and permissions for S3 access
