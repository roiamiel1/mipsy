"""
mipsy setup.py
"""

from distutils.core import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = '(Extremely) basic MIPS32 assembler. See homepage for details.'

setup(
    name='mipsy',
    version='0.1.2',
    author='Nick Miller',
    author_email='ngmiller@iastate.edu',
    packages=['mipsy'],
    scripts=['bin/mipsy'],
    url='https://github.com/ngmiller/mips-assembler',
    license='LICENSE',
    description='MIPS32 assembler.',
    long_description=long_description,
    install_requires=[
        'bitstring>=3.1.2',
    ],
)