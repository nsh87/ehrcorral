#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'jellyfish',
    'backport_collections',
    'numpy',
    'pylev',
]

test_requirements = [
   'fake-factory',
   'unittest2',
   'sphinx',
   'sphinx_rtd_theme',
]

setup(
    name='EHRcorral',
    version='0.0.3',
    description="EHRcorral cross-matches and links electronic medical records for the purpose of de-duplication",
    long_description=readme + '\n\n' + history,
    author="Nikhil Haas",
    author_email='nikhil@nikhilhaas.com',
    url='https://github.com/nsh87/ehrcorral',
    packages=[
        'ehrcorral',
    ],
    package_dir={'ehrcorral': 'ehrcorral'},
    include_package_data=True,
    package_data={'ehrcorral': ['*.json']},
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='record linkage ehr patient matching',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    use_2to3=True
)
