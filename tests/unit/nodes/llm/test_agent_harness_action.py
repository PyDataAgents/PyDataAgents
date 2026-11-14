

import os

from pydag.nodes.llm.AgentHarnessAction import AgentHarnessAction
from pydag.utils.FileUtils import FileUtils


def test_random_folder_instruction():    
    action = AgentHarnessAction(
        harness="codex",
        prompt="create 10 random folders in the given working directory",
        instruction="the folders names should be uuid's.",
        working_directory=FileUtils.user_home() + os.sep + "Downloads" + os.sep + "test",
    )
    action.install()
    action.execute()