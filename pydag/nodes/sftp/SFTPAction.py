from dataclasses import dataclass, field
import paramiko
from loguru import logger


from ...agents.Agent import Agent
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class SFTPAction(BufferNode, Action):
    """ `Action` that puts a local file on a remote SFTP server with Basic Authentification.
    
        This `BufferNode` requires two input_keys, LOCAL_FILE must be specified before REMOTE_FILE.
        
        For Example:
        ```python
        sa = SFTPAction(input_keys=["localpath", "remotepath"], ...)
        ```
    """

    host : str = field(default=None)
    user : str = field(default=None)
    password : str = field(default=None)

    def __post_init__(self):
        super().__post_init__()
        self._ssh_client : paramiko.SSHClient = None

    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        # check if there are two input keys specified for local file path and remote file path
        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh_client.connect(self.host, username=self.user, password=self.password)

    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        self._ssh_client.close()
        self._ssh_client = None

    def _on_execute(self):
        data = self.get_parent_data(by_rows=True)
        row : dict
        for row in data:
            if len(row) == 2:
                sftp = self._ssh_client.open_sftp()
                it = iter(row.items())
                local_key, local_file = next(it)
                remote_key, remote_file = next(it)
                sftp.put(local_file, remote_file)
                sftp.close()
                self.add_data({remote_key: remote_file})
            else:
                logger.warning("row dictionary of parent data must have exactly two keys with filepaths or local and remote files")