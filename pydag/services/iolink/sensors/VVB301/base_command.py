import requests

class Client:
    def process_response(self, iol_master_response):
        raise NotImplementedError("Subclasses must implement this method")
    
    #mainly to enforce the kind of data the client is expected to receive
    def valid(self, iol_master_response):
        return (iol_master_response is not None) and iol_master_response.get("cid", None) is not None and iol_master_response.get("code", 0) == 200

class BaseCommand:
    def __init__(self, base_url, endpoint, params_or_data=None):
        self.base_url = "http://" + base_url
        self.endpoint = endpoint
        self.params_or_data = params_or_data
        self.next_command = None
        self._result = None
        self._response_client = None

    def chain(self, next_command_class, *args, **kwargs):
        next_command = next_command_class(self.base_url, *args, **kwargs)
        if self.can_chain(next_command):
            self.next_command = next_command
            return self.next_command
        else:
            raise ValueError(f"Cannot chain {next_command_class.__name__} to {self.__class__.__name__}")
    
    def chain_existing(self, next_command):
        if self.can_chain(next_command):
            self.next_command = next_command
            return self.next_command
        else:
            raise ValueError(f"Cannot chain next_command: {next_command}")

    def can_chain(self, next_command):
        return isinstance(next_command, BaseCommand)

    def execute(self):
        url = self.base_url
        if self.endpoint and len(self.endpoint) > 0:
            url = url + "/" + self.endpoint
        response = requests.post(url, json=self.params_or_data)

        self._result = response.json()

        response.close()
        response = None

        if self._response_client is not None:
            self._response_client.process_response(self._result)
        if self.next_command:
            return self.next_command.execute()
        return self._result

    #not sure if we have time to make the async implementation as well
    async def execute_async(self):
        raise NotImplementedError("Subclasses must implement this method")
    
    def attach_client(self, response_client: Client):
        self._response_client = response_client