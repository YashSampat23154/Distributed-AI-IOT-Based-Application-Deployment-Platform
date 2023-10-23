import os
from azure.storage.blob import BlobClient
from dotenv import load_dotenv
import logger as log

load_dotenv()

def download_the_zip_file(app_id, app_name, service_name):

    print(f"downloading zip file from blob storage for app[{app_name}] service[{service_name}]")
    log.log_message('DEBUG', f"downloading zip file from blob storage for app[{app_name}] service[{service_name}]")

    # generate zipname stored inside blob storage
    zip_name = app_id + "--" + service_name + ".zip"

    blob_url = f'https://applicationrepo326.blob.core.windows.net/appdb/{zip_name}'
    
    print(blob_url)
    log.log_message('INFO', f"blob url formed: {blob_url}")

    try: 
        blob_client = BlobClient.from_blob_url(blob_url, connection_string = "https;AccountName=applicationrepo326;AccountKey=90h6wbX3Ky2xC2wsMmuWip3XmncCZBdeZgutxJa2L3ngru5IVVlZ0HI2aWXrnw53HM9fVXzaR4Og+ASt4pPSoA==;EndpointSuffix=core.windows.net")
        dest_path = f'./services/{zip_name}'
        try:
            with open(dest_path, "wb") as local_file:
                blob_data = blob_client.download_blob()
                blob_data.readinto(local_file)
        except:
            print(f"File does't exist with name : {zip_name}")
            log.log_message('ERROR', f"File does't exist with name[{zip_name}]")
            return None
        
    except:
        print("Invalid blob storage connection URL")
        log.log_message('ERROR', f"Invalid blob storage connection URL[{blob_url}]")
        return None

    print(f"File downloaded from blob for app[{app_name}] service[{service_name}]")
    
    
    log.log_message('DEBUG', f"File downloaded from blob for app[{app_name}] service[{service_name}]")

    return zip_name

