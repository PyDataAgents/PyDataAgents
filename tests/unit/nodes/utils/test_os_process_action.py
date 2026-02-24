import subprocess


from pydag.nodes.utils.OSKillProcessAction import OSKillProcessAction
from pydag.nodes.utils.OSProcessAction import OSProcessAction


def test_000():
    pa = OSProcessAction(executable="python.exe", arguments=["--version"], detached=False)
    pa.install()
    pa.execute()
    
    print(pa.get_buffer().data())
     
    pa.uninstall()
    
def test_010():
    pa = OSProcessAction(executable="C:\\Program Files\\influxdb2-2.7.12-windows\\influxd.exe", detached=True)
    pa.install()
    pa.execute()
    pa.uninstall()
    
    
def test_020():
    subprocess.Popen("start notepad.exe", shell=True)
    
def test_021():
    subprocess.Popen(["cmd.exe", "/k", "C:\\Program Files\\influxdb2-2.7.12-windows\\influxd.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    
def test_030():
    pka = OSKillProcessAction(executable="notepad.exe")
    pka.install()
    pka.execute()