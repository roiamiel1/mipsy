"""
Testing regular expression matching expectations.
"""

import unittest
import re


class RegularExpressionTests(unittest.TestCase):
    """
    Expected results come from the mipshelper.com instruction converter.
    (Please, let me know if there is a better source.)
    """

    label_test = r'(?P<label>[\w]+)[ ]*:[ ]*(?P<instruction>.*)'
    label_test_regex = re.compile(label_test, re.IGNORECASE)

    def run_test(self, r, test_string):
        """ Assert a match with the test string on the given (compiled) regular expression object. """
        match = r.match(test_string)
        self.assertIsNotNone(match,
            msg='given string: \"{}\" did not match RE: {}'.format(test_string, r.pattern))
        return match

    def run_test_negative(self, r, test_string):
        """ Assert a non-match with the test string on the given (compiled) regular expression object. """
        match = r.match(test_string)
        self.assertIsNone(match,
            msg='given string: \"{}\" did match RE: {}'.format(test_string, r.pattern))
        return match

    def test_label_match(self):
        label = 'sort'
        instruction = 'addi $s0, $s0, -20'
        r = self.label_test_regex

        match = self.run_test(r, 'sort:addi $s0, $s0, -20')
        self.assertEqual(label, match.group('label'))
        self.assertEqual(instruction, match.group('instruction'))

        match = self.run_test(r, 'sort:  addi $s0, $s0, -20')
        self.assertEqual(label, match.group('label'))
        self.assertEqual(instruction, match.group('instruction'))

        match = self.run_test(r, 'sort  :addi $s0, $s0, -20')
        self.assertEqual(label, match.group('label'))
        self.assertEqual(instruction, match.group('instruction'))

        match = self.run_test(r, 'sort  :  addi $s0, $s0, -20')
        self.assertEqual(label, match.group('label'))
        self.assertEqual(instruction, match.group('instruction'))

        match = self.run_test(r, 'sort:')
        self.assertEqual(label, match.group('label'))
        self.assertEqual('', match.group('instruction'))

        match = self.run_test(r, 'sort : ')
        self.assertEqual(label, match.group('label'))
        self.assertEqual('', match.group('instruction'))

    def test_label_non_match(self):
        label = 'sort'
        instruction = 'addi $s0, $s0 -20'
        r = self.label_test_regex

        self.run_test_negative(r, 'sort')
        self.run_test_negative(r, 'sort   ')
        self.run_test_negative(r, ':sort:')
        self.run_test_negative(r, ' : sort:')
        self.run_test_negative(r, 'addi $s0, $s0, -20')
        self.run_test_negative(r, 'sort addi $s0, $s0, -20')

