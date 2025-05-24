from PyDataGrabber.src.utils.StringParser import StringParser


class AdapterUtils:
    
    @staticmethod
    def address_to_list(address : str) -> list:
        addresses = []
        addresses.append(address)
        return addresses

    @staticmethod
    def address_to_dict(address : str) -> dict[str, str]:
        d = StringParser.string_to_dict(address)
        return d