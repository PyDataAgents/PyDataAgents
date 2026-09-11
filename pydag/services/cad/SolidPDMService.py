from dataclasses import dataclass, field
import win32com.client
import pythoncom
from pathlib import Path


from ..ServiceException import ServiceException
from ...agents.Agent import Agent
from ..Service import Service

EDM_VAULT_OBJECT = "ConisioLib.EdmVault"
VAULT_SERIAL_GENERATOR = ""

@dataclass
class SolidPDMService(Service):
    """ `Service` for high-level wrapping of SolidWorks PDM Professional COM API.
    Wraps common vault, file, search, and workflow operations.
    
    for help goto:
    - https://help.solidworks.com/2023/english/api/epdmapi/Welcome-epdmapi.html?utm_source=chatgpt.com
    - https://github.com/BlueByteSystemsInc/SOLIDWORKS-PDM-API-SDK?utm_source=chatgpt.com
    - https://www.codestack.net/
    """
    
    vault_name : str = field(default=None, metadata={"description": ""})
    user : str = field(default=None)
    password : str = field(default=None)
    
    def __post_init__(self):
        super().__post_init__()
        self._vault = None
    
    def _on_install(self, agent :Agent = None):
        super()._on_install(agent)
        pythoncom.CoInitialize()
        self._vault = win32com.client.Dispatch(EDM_VAULT_OBJECT)
        if self.user:
            self._vault.Login(self.user, self.password, self.vault_name)
        else:    
            # Login to vault using current Windows credentials            
            self._vault.LoginAuto(self.vault_name, 0)
        if not self._vault.IsLoggedIn:
            raise ServiceException("Login failed")        
        return
    
    def _on_uninstall(self, agent=None):
        super()._on_uninstall(agent)
        if self._vault:
            self._vault.Logout()
        return
           
    def _on_start(self):
        return
    
    def _on_stop(self):
        return
    
    # ------------------------------------------------------------------
    # FILE ACCESS
    # ------------------------------------------------------------------

    def get_file_from_path(self, file_path: str):
        """Get IEdmFile5 object from full file path"""
        folder = None
        file = self._vault.GetFileFromPath(file_path, folder)
        return file

    def check_out(self, file_path: str, comment: str = ""):
        """Check out a file"""
        file = self.get_file_from_path(file_path)
        folder = self._vault.GetFolderFromPath(str(Path(file_path).parent))
        file.LockFile(folder.ID, 0, comment)

    def check_in(self, file_path: str, comment: str = ""):
        """Check in a file"""
        file = self.get_file_from_path(file_path)
        folder = self._vault.GetFolderFromPath(str(Path(file_path).parent))
        file.UnlockFile(folder.ID, comment)

    def undo_check_out(self, file_path: str):
        file = self.get_file_from_path(file_path)
        file.UndoLockFile(0)

    def get_latest_version(self, file_path: str):
        file = self.get_file_from_path(file_path)
        file.GetFileCopy(0)

    # ------------------------------------------------------------------
    # VARIABLES (Data Card)
    # ------------------------------------------------------------------

    def get_variable(self, file_path: str, variable_name: str, config: str = ""):
        file = self.get_file_from_path(file_path)
        return file.GetVar(variable_name, config)

    def set_variable(self, file_path: str, variable_name: str, value, config: str = ""):
        file = self.get_file_from_path(file_path)
        file.SetVar(variable_name, config, value)

    # ------------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------------

    def search_files(self, filename: str = "", variable_filters: dict = None):
        """
        Search for files by name and/or variable filters.
        Returns list of file paths.
        """
        search = self._vault.CreateSearch()
        search.FindFiles = True

        if filename:
            search.FileName = filename

        if variable_filters:
            for var, val in variable_filters.items():
                search.AddVariable(var, val)

        results = []
        result = search.GetFirstResult()

        while result:
            results.append(result.Path)
            result = search.GetNextResult()

        return results

    # ------------------------------------------------------------------
    # WORKFLOW / STATE
    # ------------------------------------------------------------------

    def get_current_state(self, file_path: str):
        file = self.get_file_from_path(file_path)
        return file.CurrentState.Name

    def change_state(self, file_path: str, transition_name: str, comment: str = ""):
        file = self.get_file_from_path(file_path)
        transitions = file.GetTransitions()

        for transition in transitions:
            if transition.Name == transition_name:
                file.ChangeState(transition.ID, comment)
                return

        raise Exception(f"Transition '{transition_name}' not found")

    # ------------------------------------------------------------------
    # FOLDER OPERATIONS
    # ------------------------------------------------------------------

    def get_folder(self, folder_path: str):
        return self._vault.GetFolderFromPath(folder_path)

    def create_folder(self, parent_folder_path: str, folder_name: str):
        parent = self.get_folder(parent_folder_path)
        parent.AddFolder(folder_name, 0)

    # ------------------------------------------------------------------
    # REFERENCES
    # ------------------------------------------------------------------

    def get_references(self, file_path: str):
        """Return list of referenced files"""
        file = self.get_file_from_path(file_path)
        tree = file.GetReferenceTree(0)
        refs = []

        pos = tree.GetFirstChildPosition()
        while pos:
            ref = tree.GetNextChild(pos)
            refs.append(ref.Path)

        return refs

    # ------------------------------------------------------------------
    # UTILITY
    # ------------------------------------------------------------------

    def is_checked_out(self, file_path: str):
        file = self.get_file_from_path(file_path)
        return file.IsLocked

    def get_version(self, file_path: str):
        file = self.get_file_from_path(file_path)
        return file.CurrentVersion
    
    def get_next_serial_number(self, serial_generator_name : str = VAULT_SERIAL_GENERATOR) -> str:
        # Create serial number utility
        util = self._vault.CreateUtility(5)  # 5 = EdmUtil_SerialNo
        ser_gen = util  # IEdmSerNoGen5 interface

        # Get next serial number
        next_number : str = ser_gen.GetNextSerialNumber(serial_generator_name)

        return next_number