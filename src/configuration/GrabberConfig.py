import json
from PyDataGrabber.src.grabbers.Grabber import Grabber


class GrabberConfig:
    """
    Configuration class for the Grabber application.
    """

    def __init__(self, grabber : Grabber = None):
        self.grabber_config = dict()
        self.adapter_configs = []
        self.buffer_configs = []
        self.mapping_configs = []
        self.service_configs = []
        
        if grabber is not None:
            # create grabber config
            self.grabber_config = grabber.config_options()
            # create adapter configs
            for adapter in grabber.adapter_store.values():
                self.adapter_configs.append(adapter.config_options())       
            # create buffer configs
            for buffer in grabber.buffer_store.values():
                self.buffer_configs.append(buffer.config_options())
            # create mapping configs
            for mapping_thread in grabber.mapping_store.values():
                self.mapping_configs.append(mapping_thread.mapping.config_options())
            # create service configs
            for service in grabber.service_store.values():
                self.service_configs.append(service.config_options())
     
    def json(self) -> str:
        """
        Convert the configuration to a JSON string.
        """
        d = dict()
        d["grabber"] = self.grabber_config
        d["adapters"] = self.adapter_configs
        d["buffers"] = self.buffer_configs
        d["mappings"] = self.mapping_configs
        d["services"] = self.service_configs        
        return json.dumps(d, indent=4)
               
    def __str__(self) -> str:
        return self.json()
    