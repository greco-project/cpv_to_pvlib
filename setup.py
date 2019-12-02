#! /usr/bin/env python

from setuptools import setup, find_packages
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='cpvtopvlib',
    author='Inia Steinbach',
    author_email='inia.steinbach@rl-institut.de',
    description='A cpv module that could be added to pvlib.',
    namespace_package=['cpvtopvlib'],
    long_description=read('README.rst'),
    packages=find_packages(),
    package_dir={'cpvtopvlib': 'cpvtopvlib'},
    extras_require={
          'dev': ['sphinx', 'sphinx_rtd_theme', 'requests']},
    install_requires=[
        'pvlib >= 0.6.3',
        'pandas >= 0.24.1',
        'numpy',
        'matplotlib'])