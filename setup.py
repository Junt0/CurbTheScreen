#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='CurbTheScreen',
    version='0.1.0',
    description='Software to have a better relationship with technology',
    author_email='kalin.kochnev@gmail.com',
    packages=find_packages(),

    # https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-dependencies
    install_requires=[
        'psutil==5.6.7',
        'pytest==5.3.5',
        'pathlib2==2.3.5'
    ],

)
