from setuptools import setup, find_packages
 
setup(
    name="PyDataGrabber",
    version="0.0.1",
    packages=find_packages("src", exclude=["tests"]),
    package_dir = {"": "src"}
)