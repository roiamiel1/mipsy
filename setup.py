"""
mipsy setup.py
"""

from distutils.core import setup

setup(
    name='mipsy',
    version='0.1.3',
    author='Nick Miller',
    author_email='ngmiller@iastate.edu',
    packages=['mipsy'],
    scripts=['bin/mipsy'],
    url='https://github.com/ngmiller/mips-assembler',
    license='MIT',
    description='MIPS32 assembler.',
    long_description='(Extremely) basic MIPS32 assembler. See github page for details.',
    install_requires=[
        'bitstring>=3.1.2',
    ],
)