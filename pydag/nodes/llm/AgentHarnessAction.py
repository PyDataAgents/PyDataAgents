import enum
import subprocess
from dataclasses import dataclass, field
import json

from pydag.agents.Agent import Agent
from pydag.nodes.NodeException import NodeException
from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode

class SupportedHarnessCLI(str, enum.Enum):
    CODEX = "codex"
    # Add other supported harnesses here as needed

@dataclass
class AgentHarnessAction(BufferNode, Action):
    """ An `BufferNode` that executes CLI based agent harness instructions (codex, or similar).
    This is useful for creating complex behaviors by chaining together multiple actions.
    """

    harness : str = field(default=SupportedHarnessCLI.CODEX.value, metadata={"description": "agent harness to execute"})
    prompt : str = field(default=None, metadata={"description": "prompt to send to the agent harness"})
    working_directory : str = field(default=None, metadata={"description": "working directory for the agent harness process"})
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if not self.prompt:
            raise NodeException("AgentHarnessAction requires a prompt to be specified")
        if not self.working_directory:
            raise NodeException("AgentHarnessAction requires a working_directory to be specified")
    
    def _on_execute(self):
        process : subprocess.Popen = None
        match self.harness:
            case SupportedHarnessCLI.CODEX.value:
                process = self._execute_codex(self.prompt, self.working_directory)
            case _:
                raise NodeException(f"Unsupported harness: {self.harness}")
        
        lines: list[str] = []
        for line in process.stdout:
            lines.append(line)

        self.add_data({"stdout": "\n".join(lines)})
        
        lines = []
        for line in process.stderr:
            lines.append(line)
        self.add_data({"stderr": "\n".join(lines)})

        process.wait()
        
        self.add_data({"exit_code": process.returncode})
        
    @staticmethod
    def _execute_codex(prompt: str, project_dir: str) -> subprocess.Popen:        
        process = subprocess.Popen(
            [
                "codex", "exec", "--skip-git-repo-check",
                "--json",
                "--sandbox", "workspace-write",
                prompt,
            ],
            cwd=project_dir,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        return process

