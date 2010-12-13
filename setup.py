# -*- coding: utf-8 -*-
# Copyright (c) 2010 Michael Howitz
# See also LICENSE.txt

import os.path
import setuptools

def read(*path_elements):
    return "\n\n" + file(os.path.join(*path_elements)).read()

version = '1.0.0dev'

setuptools.setup(
    name='Products.DTMLTeX',
    version=version,
    description="Zope 2 product to create PDF files using DTML file",
    long_description=(
        '.. contents::' +
        read('README.txt') +
        read('TODO.txt') +
        read('CHANGES.txt')
        ),
    keywords='svg',
    author='Marian Kelc, Christian Theune, Thomas Lotze',
    author_email='mail@gocept.com',
    url='http://code.gocept.com',
    license='ZPL 2.1',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        ],
    packages=setuptools.find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        ],
    extras_require = dict(
        test=[
            'zope.testing',
            ],
        ),
    )
