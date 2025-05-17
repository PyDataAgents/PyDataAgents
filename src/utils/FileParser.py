import os

class FileParser:
    
    @staticmethod
    def exists_file(file_path : str) -> bool:
        return os.path.isfile(file_path)
    
    @staticmethod
    def exists_folder(folder_path : str) -> bool:
        return os.path.isdir(folder_path)