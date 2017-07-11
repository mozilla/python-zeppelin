#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages

setup(
    name='python-zeppelin',
    author='Wendy Fu',
    author_email='wfu@mozilla.com',
    description='Converts Zeppelin JSON files to Markdown',
    version='1.2',
    keywords='zeppelin notebook converter markdown',
    url='https://github.com/comloo/python-zeppelin',
    entry_points={
    	'console_scripts': [
    		'zeppelin-convert = zeppelin.cli.convert:main',
    		'zeppelin-execute = zeppelin.cli.execute:main'
    	],
    },
    packages=find_packages(),
    install_requires=['pytest-runner', 'cairosvg', 'python-dateutil', 'requests>=2.18.1'],
    tests_require=['pytest']
)
