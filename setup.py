from setuptools import setup, find_packages

setup(
    name="flowagent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
