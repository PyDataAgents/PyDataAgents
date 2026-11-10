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
    """Execute a literal prompt once, or key-based inputs per parent-buffer row.

    ``instruction`` defaults to an empty string; alternatively, ``instruction_key``
    supplies instructions per row. Non-empty instructions are prepended under an
    ``Instruction:`` section, followed by the ``Prompt:`` section.

    Only Codex is supported. Install the CLI separately, make ``codex`` available
    on PATH, and configure authentication for the account running the DataAgent.
    ``working_directory`` must exist and be accessible; installation checks the
    executable and directory, but does not authenticate or install the harness.
    Setup: https://learn.chatgpt.com/docs/codex/cli
    Automation authentication: https://learn.chatgpt.com/docs/non-interactive-mode

    Each invocation writes one row containing stdout, stderr, and exit_code.
    ``output_keys`` may rename stdout only (empty means ``stdout``). Stdout is
    the final agent answer as text; progress and diagnostics remain in stderr.
    """

    harness : str = field(default=SupportedHarnessCLI.CODEX.value, metadata={"description": "agent harness to execute"})
    prompt : str = field(default=None, metadata={"description": "literal prompt to execute once, or per row when instruction_key is configured; mutually exclusive with prompt_key"})
    working_directory : str = field(default=None, metadata={"description": "existing, accessible working directory for the agent harness process"})
    prompt_key : str = field(default=None, metadata={"description": "parent-buffer key containing a non-empty string prompt per row; mutually exclusive with prompt"})
    instruction : str = field(default="", metadata={"description": "literal instructions for answer rules, format, style, constraints, and priorities; defaults to empty; mutually exclusive with instruction_key when non-empty"})
    instruction_key : str = field(default=None, metadata={"description": "parent-buffer key containing string instructions per row; mutually exclusive with non-empty instruction"})
    output_keys : list[str] = field(default_factory=list, metadata={"description": "optional single final-answer destination key; empty defaults to stdout; stderr and exit_code are reserved"})
    
    def _on_install(self, agent : Agent = None):
        if (self.prompt is None) == (self.prompt_key is None):
            raise NodeException("Configure exactly one of prompt or prompt_key")
        if self.prompt is not None:
            self._validate_prompt(self.prompt)
        if self.prompt_key is not None and (not isinstance(self.prompt_key, str) or not self.prompt_key.strip()):
            raise NodeException("prompt_key must be a non-empty string")
        if not isinstance(self.instruction, str):
            raise NodeException("instruction must be a string")
        if self.instruction_key is not None:
            if self.instruction:
                raise NodeException("Configure either instruction or instruction_key, not both")
            if not isinstance(self.instruction_key, str) or not self.instruction_key.strip():
                raise NodeException("instruction_key must be a non-empty string")
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
        rows = self.get_parent_data(by_rows=True) if self.prompt_key is not None or self.instruction_key is not None else [{}]
        prompts = []
        for row in rows:
            for key, name in ((self.prompt_key, "prompt_key"), (self.instruction_key, "instruction_key")):
                if key is not None and key not in row:
                    raise NodeException(f"Missing configured {name} '{key}' in parent data")
            prompt = row[self.prompt_key] if self.prompt_key is not None else self.prompt
            instruction = row[self.instruction_key] if self.instruction_key is not None else self.instruction
            self._validate_prompt(prompt)
            if not isinstance(instruction, str):
                raise NodeException("instruction must be a string")
            prompts.append(f"Instruction:\n{instruction}\n\nPrompt:\n{prompt}" if instruction else prompt)

        stdout_key = self.output_keys[0] if self.output_keys else "stdout"
        for prompt in prompts:
            try:
                with self._execute_codex(self.working_directory) as process:
                    stdout, stderr = process.communicate(input=prompt)
            except OSError as exc:
                raise NodeException(f"Could not execute harness '{self.harness}': {exc}") from exc
            self.add_data({stdout_key: stdout})

    @staticmethod
    def _validate_prompt(prompt: str) -> None:
        if not isinstance(prompt, str) or not prompt.strip():
            raise NodeException("prompt must be a non-empty string")

    @staticmethod
    def _execute_codex(project_dir: str) -> subprocess.Popen:
        # Omit --json so stdout contains only the final answer; progress stays on stderr.
        return subprocess.Popen(
            [
                shutil.which("codex") or "codex", "exec", "--skip-git-repo-check",
                "--sandbox", "workspace-write",
                "-",  # Read multiline prompts from stdin, including through Windows .cmd wrappers.
            ],
            cwd=project_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

