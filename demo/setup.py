from setuptools import setup


setup(
    name='gw-utils-demo-app',
    version='0.1.0',
    install_requires=['celery>=4', 'kombu'],
    packages=['gw_utils_demo_app']
)
