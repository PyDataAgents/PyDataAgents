from dataclasses import dataclass, field
import os
import subprocess

import psutil

from ...agents.Agent import Agent
from ..BufferNode import BufferNode
from ..Action import Action


@dataclass
class OSProcessAction(Action, BufferNode):
    
    executable : str = field(default=None, metadata={"description": "The executable to run, e.g., 'python.exe'"})    
    arguments : list = field(default_factory=list, metadata={"description": "List of arguments to pass to the executable"})
    extract_keys : list = field(default_factory=list, metadata={"description": "List of keys to extract from the parent buffers data and pass as arguments"})
    detached : bool = field(default=True, metadata={"description": "Whether to run the process in a detached state"})
           
    def execute(self):
        cmd : list[str] = None
        if self.detached:
            cmd = ["cmd.exe", "/k", self.executable]
        else:
            cmd = [self.executable]
        if len(self.arguments) > 0:
            cmd = cmd + self.arguments
        elif len(self.extract_keys) > 0:
            args = []
            for k in self.extract_keys:
                for parent in self.parents:
                    if isinstance(parent, BufferNode):
                        data = parent.buffer.data()
                        if k in data:
                            v = data[k]
                            args.append(str(v[0]))
            cmd = cmd + args
        
        if self.detached:
            subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            self.buffer.push({"stdout": result.stdout, "stderr": result.stderr})
    
    def uninstall(self, agent : Agent = None):
        super().uninstall(agent)
        # Terminate the process if it's still running
        process_name = self.executable.rsplit(os.sep, maxsplit=1)[-1]
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                proc.kill()