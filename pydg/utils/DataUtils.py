class DataUtils:
    
    @staticmethod
    def force_numeric(value):
        """_attempty to convert the given value into an int or float

        Args:
            value (any): any object

        Returns:
            _type_: returns a numeric value if possible otherwise the original object
        """
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value  # Keep as string if not numeric