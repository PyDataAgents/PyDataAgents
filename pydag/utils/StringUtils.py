from urllib.parse import urlparse
import re

class StringUtils:
    
    @staticmethod
    def string_to_dict(s : str, delimiter : str = ";", assign_str : str = "="):    
        d = {}
        splits = s.split(delimiter)
        for split in splits:
            splits2 = split.split(assign_str)
            if len(splits2) == 2:
                d[splits2[0]] = splits2[1]                
        return d
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """ checks the given string for a valid url """
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https", "ftp") and parsed.netloc != ""
    
    @staticmethod
    def is_valid_file_link(s: str) -> bool:
        windows_path = re.compile(
            r'^[a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*$'
        )
        unix_path = re.compile(
            r'^(/[^/\0]+)+/?$'
        )
        file_url = re.compile(
            r'^file://(/|localhost/)?[^\s]+$',
            re.IGNORECASE
        )
        return (
            bool(windows_path.match(s)) or
            bool(unix_path.match(s)) or
            bool(file_url.match(s))
        )