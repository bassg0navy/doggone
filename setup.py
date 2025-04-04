'''Setup doggone CLI to be used as stand-alone executatble'''
from setuptools import setup, find_packages

setup(
    name="doggone",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "click",
        "pulumi",
        "pulumi_oci",
        "oci",
    ],
    entry_points="""
        [console_scripts]
        doggone=doggone:cli
    """,
)
