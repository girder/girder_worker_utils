import os
import re

from setuptools import find_packages, setup

with open('requirements.in') as f:
    install_requires = f.readlines()

setup(
    name='girder-worker-utils',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
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
