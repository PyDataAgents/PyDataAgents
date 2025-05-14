import os

class FileParser:
    
    @staticmethod
    def exists_file(file_path : str) -> bool:
        return os.path.isfile(file_path)