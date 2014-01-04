"""
mipsy setup.py
"""

from distutils.core import setup

setup(
    name='mipsy',
    version='0.1.1',
    author='Nick Miller',
    author_email='ngmiller@iastate.edu',
    packages=['mipsy'],
    scripts=['bin/mipsy'],
    url='https://github.com/ngmiller/mips-assembler',
    license='LICENSE',
    description='MIPS32 assembler.',
    install_requires=[
        'bitstring>=3.1.2',
    ],
)