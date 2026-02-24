from dataclasses import dataclass, field
import os
import psutil


from ..Action import Action


@dataclass
class OSKillProcessAction(Action):
    """ `Node` that kills a specified OS process by its executable name.

    """
    
    executable : str = field(default=None, metadata={"description": "The executable to kill, e.g. 'python.exe'"})    
          
    def _on_execute(self):
        # Terminate the process if it's still running
        process_name = self.executable.rsplit(os.sep, maxsplit=1)[-1]
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                proc.kill()