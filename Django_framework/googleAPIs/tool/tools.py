import os
import uuid
import datetime
from google.cloud import storage

def generate_download_signed_urls(blob_names, num_images):
    if len(blob_names) != num_images:
        raise ValueError("The number of blob names must match the number of images specified")

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

        # Generate signed URL 
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=5),  # URL valid for 5 minutes
            method="GET"
        )

        urls.append((modified_blob_name, url))

    return urls

