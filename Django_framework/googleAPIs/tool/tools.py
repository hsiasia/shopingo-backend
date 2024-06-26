import os
import uuid
import datetime
from google.cloud import storage

def generate_download_signed_urls(blob_names):
    # Create an authenticated storage client 
    key_path = os.path.join(os.path.dirname(__file__), 'auth.json')
    storage_client = storage.Client.from_service_account_json(key_path)

    bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))

    urls = []
    
    for blob_name in blob_names:
        # Generate a unique identifier for the file name
        unique_suffix = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '-' + str(uuid.uuid4())
        modified_blob_name = f"{unique_suffix}-{blob_name}"

        blob = bucket.blob(modified_blob_name)
        blob_url = f"https://storage.googleapis.com/{os.getenv('BUCKET_NAME')}/{modified_blob_name}"

        
        # Generate signed URL 
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=5),  # URL valid for 5 minutes
            method="PUT",
        )

        urls.append((signed_url, blob_url))

    return urls

