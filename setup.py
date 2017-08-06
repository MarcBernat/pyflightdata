#!/usr/bin/env python

from distutils.core import setup

setup(
    name='pyflightdata',
    version='0.4.3',
    description='Get flight data from websites by making HTTP calls',
    long_description='Please visit https://github.com/supercoderz/pyflightdata && https://github.com/MarcBernat/pyflightdata for more details',
    author='Narahari Allamraju, Marc Bernat'
    url='https://github.com/supercoderz/pyflightdata, https://github.com/MarcBernat/pyflightdata', 
    packages=['pyflightdata'],
    install_requires=[
        'lxml',
        'requests',
        'beautifulsoup4',
        'jsonpath-rw'],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3',
    ])
