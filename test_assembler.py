"""
Basic tests for the assembler.
Author: Nick Miller, ngmiller@iastate.edu
"""

import unittest
import assembler


class AssemblerTest(unittest.TestCase):
    """
    Expected results come from the mipshelper.com instruction converter.
    (Please, let me know if there is a better source.)
    """

    error_message = 'encode value: {} for instruction: {} does not match expected: {}'
    assembler = assembler.MIPSAssembler()

    def run_test(self, instr, expected):
        """
        Encodes the given instruction string and cross-references the output
        with the expected bit string.
        """
        result = self.assembler.encode_instruction(instr)
        self.assertEqual(expected, result, msg=self.error_message.format(result, instr, expected))

    def test_nop(self):
        self.run_test('nop', '00000000000000000000000000000000')

    def test_add(self):
        self.run_test('add $t0, $t1, $t2', '00000001001010100100000000100000')

    def test_addi(self):
        self.run_test('addi $s2, $s3, 4', '00100010011100100000000000000100')
        self.run_test('addi $s0, $s0, -20', '00100010000100001111111111101100')

    def test_lw(self):
        self.run_test('lw $a0, 4($zero)', '10001100000001000000000000000100')
        self.run_test('lw $s3, 8($t1)', '10001101001100110000000000001000')
