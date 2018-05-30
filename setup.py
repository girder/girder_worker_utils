import os

from setuptools import find_packages, setup

with open('requirements.in') as f:
    install_requires = f.readlines()


def prerelease_local_scheme(version):
    """Return local scheme version unless building on master in CircleCI.

    This function returns the local scheme version number
    (e.g. 0.0.0.dev<N>+g<HASH>) unless building on CircleCI for a
    pre-release in which case it ignores the hash and produces a
    PEP440 compliant pre-release version number (e.g. 0.0.0.dev<N>).

    """

    from setuptools_scm.version import get_local_node_and_date

    if 'CIRCLE_BRANCH' in os.environ and \
       os.environ['CIRCLE_BRANCH'] == 'master':
        return ''
    else:
        return get_local_node_and_date(version)


setup(
    name='girder-worker-utils',
    use_scm_version={'local_scheme': prerelease_local_scheme},
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
