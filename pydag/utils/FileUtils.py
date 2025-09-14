import os
from pathlib import Path
import platform
import shutil
import subprocess
import time
from loguru import logger

class FileUtils:
    
    @staticmethod
    def exists_file(file_path : str) -> bool:
        return os.path.isfile(file_path)
    
    @staticmethod
    def exists_folder(folder_path : str) -> bool:
        return os.path.isdir(folder_path)
    
    @staticmethod
    def copy_file(source_file : str, target_file : str) -> bool:
        if FileUtils.exists_file(source_file):
            if os.path.isfile(target_file):
                parent_folder = os.path.dirname(target_file)
                if not os.path.isdir(parent_folder):            
                    os.makedirs(parent_folder)
                shutil.copy2(source_file, target_file)
                return True
            elif os.path.isdir(target_file):
                shutil.copy2(source_file, target_file)
                return True
            else:                
                logger.error("target_file " + target_file + " is not a directory nor a file")
                return False
        else:
            logger.error("target_file " + target_file + " does not exist")
            return False
       
    @staticmethod 
    def move_file(source_file : str, target_file : str) -> bool:
        if FileUtils.exists_file(source_file):
            if os.path.isfile(target_file):
                parent_folder = os.path.dirname(target_file)
                if not os.path.isdir(parent_folder):            
                    os.makedirs(parent_folder)
                shutil.move(source_file, target_file)
                return True
            elif os.path.isdir(target_file):
                shutil.move(source_file, target_file)
                return True
            else:                
                logger.error("target_file " + target_file + " is not a directory nor a file")
                return False
        else:
            logger.error("target_file " + target_file + " does not exist")
            return False
    
    @staticmethod    
    def delete_file(file_path : str) -> bool:
        if FileUtils.exists_file(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e}")
                return False
        else:
            logger.error("File " + file_path + " does not exist")
            return False
      
    @staticmethod  
    def list_files(folder : str, pattern : str = None, extension : str = None, newer_than_seconds : int = None, recursive : bool = False) -> list[str]:
        if os.path.isdir(folder):
            path = Path(folder)
            iterator = path.rglob("*") if recursive else path.iterdir()
            #cutoff = time.time() - older_than_seconds            
            if newer_than_seconds is not None:
                cutoff = time.time() - newer_than_seconds
                files = [
                    f for f in iterator
                    if f.is_file() and f.stat().st_mtime > cutoff
                ]
            else:
                files = [
                    str(f) for f in iterator
                    if f.is_file()
                ]
            if pattern is not None:
                files = [
                    f for f in files
                    if pattern in f
                ]
            if extension is not None:
                files = [
                    f for f in files
                    if f.endswith(extension)
                ]
            return files
            
        else:
            logger.error("Folder " + folder + " does not exist")
            return None
        
    @staticmethod
    def get_folder_bytes(folder : str) -> float:
        if os.path.isdir(folder):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(folder):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.isfile(fp):
                        total_size += os.path.getsize(fp)
            return total_size
        else:
            logger.error("Folder " + folder + " does not exist")
            return 0
    
    @staticmethod    
    def get_extensions_from_folder(folder : str) -> list[str]:
        if os.path.isdir(folder):
            files = FileUtils.list_files(folder)
            file_extensions = list(set(list(f.split('.')[-1] for f in files if '.' in f)))
            return file_extensions
        else:
            logger.error("Folder " + folder + " does not exist")
            return []
    
    @staticmethod    
    def get_modified_date_ms(file_path : str) -> int:
        if FileUtils.exists_file(file_path):
            timestamp = os.path.getmtime(file_path) * 1000  # Convert to milliseconds
            return int(timestamp)
        else:
            logger.error("File " + file_path + " does not exist")
            return 0
    
    @staticmethod    
    def create_dir(dir : str):
        """
        recursively creates all missing parent directories of `dir`
        """
        os.makedirs(dir, exist_ok=True)
        
    @staticmethod
    def parent_folder(file_path : str) -> str:
        """ returns the parent folder of the specified filepath
            <br>Example:
            ```python 
            >>parent_folder("C:\\fake\\path\\file.txt")
            C:\\fake\\path
            ```          
        
            Args:
            file_path (str): file path

        Returns:
            str: parent folder of the specified file path
        """
        return os.path.dirname(file_path)
    
    @staticmethod
    def file_name(file_path : str, with_ext : bool = True) -> str:
        """returns only the filename from `file_path`
        <br>if `with_ext` is true, then also the file extension is returned
        <br>Example:
        ```python
        file_name('C:\\fake\\path\\t.txt', True)
        >>t.txt
        ```

        Args:
            file_path (str): absolute file path
            with_ext (bool, optional): specifies whether to include or exclude file extension. Defaults to True.

        Returns:
            str: file name
        """
        if with_ext:
            return os.path.basename(file_path)
        else:
            return os.path.splitext(os.path.basename(file_path))[0]
        
    @staticmethod
    def open_file(file_path):
        """ opens the file with the OS' standard program

        Args:
            file_path (str): path to the file to open or start
        """
        path = Path(file_path).resolve()
        system = platform.system()
        
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux and other
            subprocess.run(["xdg-open", path])
        
    @staticmethod    
    def user_home() -> str:
        home_dir = Path.home()
        return str(home_dir)