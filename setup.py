'''Setup doggone CLI to be used as stand-alone executatble'''
from setuptools import setup, find_packages

setup(
    name="doggone",
    version="0.1",
    package_dir={"": "src"},  # This tells setuptools the root package is under src/
    packages=find_packages(where="src"),  # Find packages under src
    install_requires=[
        "click",
        "pulumi",
        "pulumi_oci",
        "oci",
    ],
    entry_points="""
        [console_scripts]
        doggone=doggone.cli:cli
    """,
)
