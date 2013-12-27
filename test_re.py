"""
Testing regular expression matching expectations.
"""

__license__ = """
The MIT License (MIT)

Copyright (c) 2013 Nick Miller (ngmiller@iastate.edu)

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

__author__ = 'Nick Miller, ngmiller@iastate.edu'
__version__ = '0.0.1'


import unittest
import re


class RegularExpressionTests(unittest.TestCase):
    """
    Expected results come from the mipshelper.com instruction converter.
    (Please, let me know if there is a better source.)
    """

    # Label followed by instruction
    # e.g. 'sort: addi $s0, $s0, -20'
    label_instruction = r'[\w]+[ ]*:[ ]*.+[\r\n]+'

    # Label on separate line
    # e.g. 'sort:'
    label = r'[\w]+[ ]*:[ ]*[\r\n]+'

    # Instruction
    # TODO, may need RE for each instruction format? (R, I, J)
    instr = r''

    def run_test(self, r, test_string):
        """ Assert a match with the test string on the given (compiled) regular expression object. """
        self.assertIsNotNone(r.match(test_string),
            msg='given string: \"{}\" did not match RE: {}'.format(test_string, r.pattern))

    def run_test_negative(self, r, test_string):
        """ Assert a non-match with the test string on the given (compiled) regular expression object. """
        self.assertIsNone(r.match(test_string),
            msg='given string: \"{}\" did match RE: {}'.format(test_string, r.pattern))

    def test_label_instr(self):
        r = re.compile(self.label_instruction, re.IGNORECASE)

        self.run_test(r, 'sort:addi $s0, $s0, $s0, -20\n')
        self.run_test(r, 'sort:  addi $s0, $s0, -20\n')
        self.run_test(r, 'sort  :addi $s0, $s0, -20\n')
        self.run_test(r, 'sort  :  addi $s0, $s0, -20\n')

        self.run_test_negative(r, 'sort addi $s0, $s0, -20\n')
        self.run_test_negative(r, 'sort, addi $s0, $s0, -20\n')
        self.run_test_negative(r, 'sort:\n')

    def test_label(self):
        r = re.compile(self.label, re.IGNORECASE)

        self.run_test(r, 'sort:\n')
        self.run_test(r, 'sort   :\n')
        self.run_test(r, 'sort:   \n')
        self.run_test(r, 'sort   :   \n')

        self.run_test_negative(r, 'sort\n')
        self.run_test_negative(r, 'sort   \n')
        self.run_test_negative(r, ':sort:\n')
        self.run_test_negative(r, ' : sort:\n')

