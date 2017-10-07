import os
import re

from setuptools import find_packages, setup

init = os.path.join(os.path.dirname(__file__), 'girder_worker_utils', '__init__.py')
with open(init) as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

with open('requirements.in') as f:
    install_requires = f.readlines()

setup(
    name='girder-worker-utils',
    version=version,
    description='Helper utilities for the Girder Worker',
    author='Kitware, Inc.',
    author_email='kitware@kitware.com',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5'
    ],
    install_requires=install_requires,
    packages=find_packages(
        exclude=('tests.*', 'tests')
    ),
    zip_safe=False
)
