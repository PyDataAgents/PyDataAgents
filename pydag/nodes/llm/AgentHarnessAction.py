import enum
import os
import shutil
import subprocess
from dataclasses import dataclass, field

from pydag.agents.Agent import Agent
from pydag.nodes.NodeException import NodeException
from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode
from pydag.utils.JsonUtils import JsonUtils

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

    Each invocation writes one row. Text mode stores the final answer under
    ``output_keys[0]`` (default ``stdout``). JSON mode extracts all configured
    keys from a complete JSON object, preserving values including null and arrays.
    Extra fields are ignored; invalid output raises NodeException before publication.
    """

    harness : str = field(default=SupportedHarnessCLI.CODEX.value, metadata={"description": "agent harness to execute"})
    prompt : str = field(default=None, metadata={"description": "literal prompt to execute once, or per row when instruction_key is configured; mutually exclusive with prompt_key"})
    working_directory : str = field(default=None, metadata={"description": "existing, accessible working directory for the agent harness process"})
    prompt_key : str = field(default=None, metadata={"description": "parent-buffer key containing a non-empty string prompt per row; mutually exclusive with prompt"})
    instruction : str = field(default=None, metadata={"description": "literal instructions for answer rules, format, style, constraints, and priorities; defaults to empty; mutually exclusive with instruction_key when non-empty"})
    instruction_key : str = field(default=None, metadata={"description": "parent-buffer key containing string instructions per row; mutually exclusive with non-empty instruction"})
    output_keys : list[str] = field(default_factory=list, metadata={"description": "text: optional single stdout destination; json: required answer fields; stderr and exit_code are reserved"})
    output_mode: str = field(default="text", metadata={"description": "text stores the complete answer; json extracts required output_keys from a JSON object without changing the prompt"})
    
    def _on_install(self, agent : Agent = None):
        if (self.prompt is None) == (self.prompt_key is None):
            raise NodeException("Configure exactly one of prompt or prompt_key")
        if self.prompt is not None:
            self._validate_prompt(self.prompt)
        if self.prompt_key is not None and (not isinstance(self.prompt_key, str) or not self.prompt_key.strip()):
            raise NodeException("prompt_key must be a non-empty string")
        if self.instruction is not None and not isinstance(self.instruction, str):
            raise NodeException("instruction must be a string")
        if self.instruction_key is not None:
            if self.instruction:
                raise NodeException("Configure either instruction or instruction_key, not both")
            if not isinstance(self.instruction_key, str) or not self.instruction_key.strip():
                raise NodeException("instruction_key must be a non-empty string")
        if self.output_mode not in ("text", "json"):
            raise NodeException("output_mode must be either 'text' or 'json'")
        if self.output_mode == "text" and (not isinstance(self.output_keys, list) or len(self.output_keys) > 1):
            raise NodeException("output_keys must be empty or contain one stdout destination key")
        if self.output_mode == "text" and self.output_keys:
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
        if self.output_mode == "json":
            if not isinstance(self.output_keys, list) or not self.output_keys or not isinstance(self.output_keys[0], str):
                raise NodeException("JSON output_keys must be a non-empty list of strings")
            buffer = self.get_buffer()
            if {"stderr", "exit_code", getattr(buffer, "timestamps_key", "timestamps"), getattr(buffer, "index_key", "index")}.intersection(self.output_keys):
                raise NodeException("JSON output keys must not use reserved diagnostic or buffer metadata names")
    
    def _on_execute(self):
        rows = self.get_parent_data(by_rows=True) if self.prompt_key is not None or self.instruction_key is not None else [{}]
        prompts = []
        for row in rows:
            for key, name in ((self.prompt_key, "prompt_key"), (self.instruction_key, "instruction_key")):
                if key is not None and key not in row:
                    raise NodeException(f"Missing configured {name} '{key}' in parent data")
            prompt = row[self.prompt_key] if self.prompt_key is not None else self.prompt
            instruction = row[self.instruction_key] if self.instruction_key is not None else (self.instruction or "")
            self._validate_prompt(prompt)
            if not isinstance(instruction, str):
                raise NodeException("instruction must be a string")
            prompts.append(f"Instruction:\n{instruction}\n\nPrompt:\n{prompt}" if instruction else prompt)

        for prompt in prompts:
            try:
                with self._execute_codex(self.working_directory) as process:
                    stdout, stderr = process.communicate(input=prompt)
            except OSError as exc:
                raise NodeException(f"Could not execute harness '{self.harness}': {exc}") from exc
            if self.output_mode == "json":
                if process.returncode != 0:
                    raise NodeException(f"Harness '{self.harness}' failed with exit code {process.returncode}")
                try:
                    result = JsonUtils.extract_fields(stdout, self.output_keys)
                except ValueError as exc:
                    raise NodeException(str(exc)) from exc
                # One-element columns keep JSON arrays in a single buffer row.
                self.add_data({key: [value] for key, value in result.items()})
            else:
                self.add_data({self.output_keys[0] if self.output_keys else "stdout": stdout})

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

