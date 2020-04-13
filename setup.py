"""Setup for the durable function module."""
import pathlib
import os
import shutil
import subprocess
import sys
import glob

from setuptools import setup, find_packages
from distutils.command import build

with open("README.md", "r") as fh:
    long_description = fh.read()

class BuildModule(build.build):
    """Used to build the module."""

    def run(self, *args, **kwargs):
        """Execute the build.

        :param args:
        :param kwargs:
        """
        super().run(*args, **kwargs)


setup(
    name='azure-functions-durable',
    packages=find_packages(exclude=("tests", "samples","scripts")),
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='Durable Functions For Python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Environment :: Web Environment',
        'Development Status :: 4 - Beta',
    ],
    license='MIT',
    python_requires='>=3.6,<4',
    install_requires=[
        'azure-functions>=1.2.0',
        'aiohttp>=3.6.2',
        'requests==2.*',
        'python-dateutil>=2.8.0',
        'furl>=2.1.0'
    ],
    extra_requires=[
        'flake8==3.7.8',
        'flake8-docstrings==1.5.0',
        'pytest==5.3.2',
        'python-dateutil==2.8.0',
        'requests==2.22.0',
        'jsonschema==3.2.0',
        'aiohttp==3.6.2',
        'azure-functions>=1.2.0',
        'nox==2019.11.9',
        'furl==2.1.0',
        'pytest-asyncio==0.10.0'
    ],
    include_package_data=True,
    cmdclass={
        'build': BuildModule
    },
    test_suite='tests'
)
