#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages

setup(
    name='zeppelin-converter',
    author='Wendy Fu',
    author_email='wfu@mozilla.com',
    description='Converts Zeppelin JSON files to Markdown',
    keywords='zeppelin converter markdown',
    url='https://github.com/comloo/zeppelin-converter',
    packages=find_packages(),
    data_files=[('sample_notebooks',
                ['data/test.json', 'data/test2.json',
                 'data/test3.json', 'data/test4.json',
                 'data/test5.json', 'data/test6.json'])],
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
