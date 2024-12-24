from setuptools import setup, find_namespace_packages

setup(
    name="flowagent",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
)
