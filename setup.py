"""Setup for the durable function module."""
import pathlib
import os
import shutil
import subprocess
import sys
import glob

from setuptools import setup, find_packages
from distutils.command import build


def _gen_grpc():
    root = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))
    proto_root_dir = \
        root / 'azure' / 'durable_functions' / 'grpc' / 'protobuf'
    proto_src_dir = proto_root_dir
    staging_root_dir = root / 'build' / 'protos'
    staging_dir = staging_root_dir
    build_dir = staging_dir

    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    shutil.copytree(proto_src_dir, build_dir)

    subprocess.run([
        sys.executable, '-m', 'grpc_tools.protoc',
        '-I', str(proto_src_dir),
        '--python_out', str(staging_root_dir),
        '--grpc_python_out', str(staging_root_dir),
        os.sep.join((str(proto_src_dir),
                     'DurableRpc.proto')),
    ], check=True, stdout=sys.stdout, stderr=sys.stderr,
        cwd=staging_root_dir)

    compiled = glob.glob(str(staging_dir / '*.py'))

    if not compiled:
        print('grpc_tools.protoc produced no Python files',
              file=sys.stderr)
        sys.exit(1)

    # Not sure if we need this line that will copy both the
    # proto and py generated
    # files in the proto root dir
    for f in compiled:
        shutil.copy(f, proto_root_dir)


class BuildModule(build.build):
    """Used to build the module."""

    def run(self, *args, **kwargs):
        """Execute the build.

        :param args:
        :param kwargs:
        """
        _gen_grpc()
        super().run(*args, **kwargs)


setup(
    name='azure-functions-durable',
    packages=find_packages(exclude=("tests", "samples")),
    version='1.0.1ab',
    description='Durable Functions Support For Python Functionapp',
    license='MIT',
    setup_requires=[
        'grpcio~=1.22.0',
        'grpcio-tools~=1.22.0'
    ],
    install_requires=[
        'grpcio~=1.22.0',
        'grpcio-tools~=1.22.0',
        'azure-functions>=1.2.0',
        'python-dateutil==2.8.0',
        'requests==2.22.0',
        'aiohttp==3.6.2',
        'furl==2.1.0'
    ],
    include_package_data=True,
    cmdclass={
        'build': BuildModule
    },
    test_suite='tests'
)
