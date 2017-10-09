from setuptools import setup


setup(
    name='gw-utils-demo-app',
    version='0.1.0',
    install_requires=['celery>=4', 'kombu', 'girder-client'],
    packages=['gw_utils_demo_app']
)
