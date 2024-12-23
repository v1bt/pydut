from setuptools import setup, find_packages

setup(
    name='pydut',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests==2.32.3',
        'beautifulsoup4==4.12.3',
        'tempmail-lol==3.0.0',
        'websocket-client==1.8.0',
    ],
    url='https://github.com/v1bt/pydut',
    license='MIT',
    author='virtualbyte',
    author_email='judong1094@gmail.com',
    description='playentry.org에 대한 관리 패키지',
)
