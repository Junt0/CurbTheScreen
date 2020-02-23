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
        'Click==7.0',
        'Flask==1.1.1',
        'itsdangerous==1.1.0',
        'Jinja2==2.11.1',
        'MarkupSafe==1.1.1',
        'numpy==1.16.4',
        'psutil==5.6.7',
        'Werkzeug==0.16.0',
        'pytest==5.3.5',
        'pathlib2==2.3.5'
    ],

)
