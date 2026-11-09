import enum
import os
import shutil
import subprocess
from dataclasses import dataclass, field

from pydag.agents.Agent import Agent
from pydag.nodes.NodeException import NodeException
from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode

class SupportedHarnessCLI(str, enum.Enum):
    CODEX = "codex"
    # Add other supported harnesses here as needed

@dataclass
class AgentHarnessAction(BufferNode, Action):
    """Execute a literal prompt once, or a parent-buffer ``prompt_key`` per row.

    Only Codex is supported. Install the CLI separately, make ``codex`` available
    on PATH, and configure authentication for the account running the DataAgent.
    ``working_directory`` must exist and be accessible; installation checks the
    executable and directory, but does not authenticate or install the harness.
    Setup: https://learn.chatgpt.com/docs/codex/cli
    Automation authentication: https://learn.chatgpt.com/docs/non-interactive-mode

    Each invocation writes one row containing stdout, stderr, and exit_code.
    ``output_keys`` may rename stdout only (empty means ``stdout``). Stdout is
    the raw JSONL event stream from ``codex exec --json``, not just its answer.
    """

    harness : str = field(default=SupportedHarnessCLI.CODEX.value, metadata={"description": "agent harness to execute"})
    prompt : str = field(default=None, metadata={"description": "literal prompt to execute once; mutually exclusive with prompt_key"})
    working_directory : str = field(default=None, metadata={"description": "existing, accessible working directory for the agent harness process"})
    prompt_key : str = field(default=None, metadata={"description": "parent-buffer key containing a non-empty string prompt per row; mutually exclusive with prompt"})
    output_keys : list[str] = field(default_factory=list, metadata={"description": "optional single stdout destination key; empty defaults to stdout (raw JSONL); stderr and exit_code are reserved"})
    
    def _on_install(self, agent : Agent = None):
        if (self.prompt is None) == (self.prompt_key is None):
            raise NodeException("Configure exactly one of prompt or prompt_key")
        if self.prompt is not None:
            self._validate_prompt(self.prompt)
        if self.prompt_key is not None and (not isinstance(self.prompt_key, str) or not self.prompt_key.strip()):
            raise NodeException("prompt_key must be a non-empty string")
        if not isinstance(self.output_keys, list) or len(self.output_keys) > 1:
            raise NodeException("output_keys must be empty or contain one stdout destination key")
        if self.output_keys:
            key = self.output_keys[0]
            if not isinstance(key, str) or not key.strip() or key in {"stderr", "exit_code"}:
                raise NodeException("stdout destination must be a non-empty string other than stderr or exit_code")
        if self.harness != SupportedHarnessCLI.CODEX.value:
            raise NodeException(f"Unsupported harness: {self.harness}")
        if shutil.which(self.harness) is None:
            raise NodeException(f"Harness '{self.harness}' must be installed and executable on PATH")
        if not self.working_directory or not os.path.isdir(self.working_directory):
            raise NodeException("working_directory must be an existing directory")
        if not os.access(self.working_directory, os.R_OK | os.X_OK):
            raise NodeException("working_directory must be accessible")
        super()._on_install(agent)
    
    def _on_execute(self):
        prompts = [self.prompt]
        if self.prompt_key is not None:
            prompts = []
            for row in self.get_parent_data(by_rows=True):
                if self.prompt_key not in row:
                    raise NodeException(f"Missing configured prompt_key '{self.prompt_key}' in parent data")
                prompts.append(row[self.prompt_key])
        for prompt in prompts:
            self._validate_prompt(prompt)

        stdout_key = self.output_keys[0] if self.output_keys else "stdout"
        for prompt in prompts:
            try:
                with self._execute_codex(prompt, self.working_directory) as process:
                    stdout, stderr = process.communicate()
            except OSError as exc:
                raise NodeException(f"Could not execute harness '{self.harness}': {exc}") from exc
            self.add_data({stdout_key: stdout, "stderr": stderr, "exit_code": process.returncode})

    @staticmethod
    def _validate_prompt(prompt: str) -> None:
        if not isinstance(prompt, str) or not prompt.strip():
            raise NodeException("prompt must be a non-empty string")

    @staticmethod
    def _execute_codex(prompt: str, project_dir: str) -> subprocess.Popen:        
        return subprocess.Popen(
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

