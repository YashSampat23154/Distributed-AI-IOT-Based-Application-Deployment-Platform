import os
from pathlib import Path


def delete_the_directory(folder_name_to_delete):
    
    check = Path(folder_name_to_delete)
    
    if(check.is_dir()):
        print("Present")
        command = "rm -r " + folder_name_to_delete
        os.system(command)
        print("Deleted the folder") 
    
    return


def delete_the_file(file_to_delete):
    
    check = Path(file_to_delete)
        
    if(check.is_file()):
        os.remove(file_to_delete)

    return     