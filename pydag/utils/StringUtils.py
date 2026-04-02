from sympy import re


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
    def is_str_url(s : str) -> bool:
        url_regex = re.compile(
            r'^(https?|ftp)://[^\s/$.?#].[^\s]*$',
            re.IGNORECASE
        )
        return re.match(url_regex, s) is not None