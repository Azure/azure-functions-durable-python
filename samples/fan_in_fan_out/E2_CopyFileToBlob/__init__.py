import os
import pathlib
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

connect_str = os.getenv('AzureWebJobsStorage')

def main(filePath: str) -> str:
    # Create the BlobServiceClient object which will be used to create a container client
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    
    # Create a unique name for the container
    container_name = "backups"
    
    # Create the container if it does not exist
    try:
        blob_service_client.create_container(container_name)
    except ResourceExistsError:
        pass

    # Create a blob client using the local file name as the name for the blob
    parent_dir, fname = pathlib.Path(filePath).parts[-2:] # Get last two path components
    blob_name = parent_dir + "_" + fname
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Count bytes in file
    byte_count = os.path.getsize(filePath)

    # Upload the created file
    with open(filePath, "rb") as data:
        blob_client.upload_blob(data)

    return byte_count
