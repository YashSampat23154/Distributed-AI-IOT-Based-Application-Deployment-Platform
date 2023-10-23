import os
from azure.storage.blob import BlobClient
from dotenv import load_dotenv
import logger as logger

load_dotenv()

def download_the_zip_file(json_file_name):
    
    app_name = json_file_name["app_name"]
    service_name = json_file_name["service_name"]
    
    print(f'Downloading zip file from blob for app[{app_name}] service[{service_name}]')
    logger.log_message('DEBUG', f'Downloading zip file for app[{app_name}] service[{service_name}]')

    zip_name = app_name + "--" + service_name + ".zip"

    containerName = os.getenv('AZURE_BLOB_CONTAINER_DB')

    blob_url = f'https://applicationrepo326.blob.core.windows.net/{containerName}/{zip_name}'
    
    print(blob_url)
    logger.log_message('INFO', f"blob url formed: {blob_url}")

    try: 
        blob_client = BlobClient.from_blob_url(blob_url, connection_string = os.getenv('AZURE_BLOB_CONNECTION_STRING'))
        try:
            with open(zip_name, "wb") as local_file:
                blob_data = blob_client.download_blob()
                blob_data.readinto(local_file)
        except:
            print(f"File does't exist with name : {zip_name}")
            logger.log_message('ERROR', f"File does't exist with name[{zip_name}]")
            return None
        
    except:
        print("Invalid blob storage connection URL")
        logger.log_message('ERROR', f"Invalid blob storage connection URL[{blob_url}]")
        return None

    print(f"File downloaded from blob for app[{app_name}] service[{service_name}]")
    
    logger.log_message('DEBUG', f"File downloaded from blob for app[{app_name}] service[{service_name}]")

    return zip_name
