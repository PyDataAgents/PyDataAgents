from setuptools import setup, find_packages
 
setup(
    name="PyDataGrabber",
    version="0.1",
    packages=find_packages("pydatagrabber", exclude=["tests"])
)