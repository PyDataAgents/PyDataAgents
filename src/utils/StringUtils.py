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
        