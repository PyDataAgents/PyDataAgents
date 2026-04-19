from pydag.services.tasks.TaskRunnerService import task

@task
def hello(name):
    return {"greeting": f"Hello {name}"}

@task
def goodbye(name):
    return {"next": f"let's meet some other time, {name}"}