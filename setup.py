#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages

setup(
    name='python-zeppelin',
    author='Wendy Fu',
    author_email='wfu@mozilla.com',
    description='Converts Zeppelin JSON files to Markdown. Executes Zeppelin notebooks in command line.',
    version='1.5',
    keywords='zeppelin notebook converter markdown executor api',
    url='https://github.com/comloo/python-zeppelin',
    entry_points={
    	'console_scripts': [
    		'zeppelin-convert = zeppelin.cli.convert:main',
    		'zeppelin-execute = zeppelin.cli.execute:main'
    	],
    },
    packages=find_packages(),
    install_requires=['cairosvg', 'python-dateutil', 'requests>=2.18.1'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
