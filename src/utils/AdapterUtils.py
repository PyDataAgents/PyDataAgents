from PyDataGrabber.src.utils.StringUtils import StringUtils


class AdapterUtils:
    
    @staticmethod
    def address_to_list(address : str) -> list:
        addresses = []
        addresses.append(address)
        return addresses

    @staticmethod
    def address_to_dict(address : str) -> dict[str, str]:
        d = StringUtils.string_to_dict(address)
        return d