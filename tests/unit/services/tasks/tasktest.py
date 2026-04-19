from pydag.services.tasks.TaskRunnerService import task

@task
def hello(name) -> dict[str, str]:
    return {"greeting": f"Hello {name}"}

@task
def goodbye(name) -> dict[str, str]:
    return {"next": f"let's meet some other time, {name}"}

@task
def count(s : str) -> int:
    return len(s)