"""Setup for the durable function module."""
import pathlib
import os
import shutil
import subprocess
import sys

from glob import glob
from setuptools import setup, find_packages
from distutils.command import build

with open("README.md", "r",  encoding="utf8") as fh:
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
    packages=find_packages(exclude=[
        "tests",
        "samples",
        "scripts",
        "azure"
    ]),
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author="Azure Functions team at Microsoft Corp.",
    author_email="azurefunctions@microsoft.com",
    keywords="azure functions azurefunctions python serverless workflows durablefunctions",
    url="https://github.com/Azure/azure-functions-durable-python",
    description='Durable Functions For Python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Environment :: Web Environment',
        'Development Status :: 5 - Production/Stable',
    ],
    license='MIT',
    python_requires='>=3.10,<4',
    install_requires=[
        'azure-functions>=1.12.0',
        'aiohttp>=3.14.1',
        'requests>=2.33.0,<3',
        'python-dateutil>=2.8.0',
        'furl>=2.1.0',
        'opentelemetry-api>=1.32.1',
        'opentelemetry-sdk>=1.32.1'
    ],
    extra_requires=[
        'flake8==7.1.1',
        'flake8-docstrings==1.7.0',
        'pytest==9.0.3',
        'python-dateutil==2.8.0',
        'requests==2.33.0',
        'jsonschema==4.25.1',
        'azure-functions>=1.2.0',
        'nox==2019.11.9',
        'furl==2.1.0',
        'pytest-asyncio==1.4.0'
    ],
    include_package_data=True,
    data_files= [
        ('_manifest', list(filter(os.path.isfile, glob('_manifest/**/*', recursive=True)))),
    ],
    cmdclass={
        'build': BuildModule
    },
    test_suite='tests'
)
