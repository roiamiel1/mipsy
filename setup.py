"""
mipsy setup.py
"""

from distutils.core import setup

setup(
    name='mipsy',
    version='0.1.0',
    author='Nick Miller',
    author_email='ngmiller@iastate.edu',
    packages=['mipsy', 'mipsy.test'],
    scripts=['bin/mipsy'],
    url='http://pypi.python.org/pypi/mipsy/',
    license='LICENSE',
    decription='MIPS32 assembler.',
    install_requires=[
        'bitstring >= 3.1.2',
    ],
)