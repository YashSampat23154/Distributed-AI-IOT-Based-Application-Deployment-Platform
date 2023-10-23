#It will take the file name to unzip as an argument.
from zipfile import ZipFile
import logger as log
from delete_things import delete_the_directory

def unzipping(file_to_unzip):

    print(f"Unzipping file[{file_to_unzip}]")
    log.log_message('DEBUG', f"Unzipping file[{file_to_unzip}]")

    folder_name = file_to_unzip.split(".")[0]
    delete_the_directory(folder_name)

    file_path = f"./services/{file_to_unzip}"

    folder_path = f"./services/{folder_name}"
   
    with ZipFile(file_path, 'r') as f:
        f.extractall(folder_path)

    print(f"File un-zipping completed for file[{file_to_unzip}]")
    log.log_message('DEBUG', f"File un-zipping completed for file[{file_to_unzip}]")
    
    return folder_name
