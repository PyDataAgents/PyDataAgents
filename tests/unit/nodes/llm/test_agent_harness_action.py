from pydag.nodes.llm.AgentHarnessAction import AgentHarnessAction
from pydag.utils.FileUtils import FileUtils


def test_create_random_folders():
    wd = FileUtils.user_home() + "\\Downloads\\test\\harness\\"
    FileUtils.create_dir(wd)
    
    f=10
    
    aha = AgentHarnessAction(
        harness="codex",
        prompt=f"create {f} random folders in the working directory",
        working_directory=wd
    )
    aha.install()
    
    aha.execute()
    
    print(aha.get_data())
    
    fos = FileUtils.list_folders(wd)
    
    assert len(fos) == f, f"Expected {f} folders to be created, but found {len(fos)}"