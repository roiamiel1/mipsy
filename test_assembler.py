"""
Basic tests for the assembler.
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
import assembler


class ProgramTests(unittest.TestCase):
    """
    Tests assembler output against full program input.
    Need a valid (master) file to compare against.
    """
    def run_test(self, in_path, master_path):
        with open(master_path) as f:
            master = f.readlines()
            f.close()

        with open(in_path) as f:
            output = f.readlines()
            f.close()

        self.assertEqual(len(master), len(output),
            msg='Lengths of master file and output are not equal.')

        for i in range(len(output)):
            if output[i] != master[i]:
                self.fail('instr: {} output encoding: {} != master encoding: {}'.format(i, output[i], master[i])) 

        self.assertTrue(True)

    def test_bubblesort_no_labels(self):
        """
        Tests against a bubblesort program that works for a VHDL MIPS32 implementation.
        """
        self.run_test('testing/bubblesort_out.txt', 'testing/bubblesort_out_master.txt')

    def test_bubblesort_labels(self):
        self.run_test('testing/bubblesort_labels_out.txt', 'testing/bubblesort_out_master.txt')


class LabelCacheTests(unittest.TestCase):
    """
    Tests basic functionality of the label cache.
    """
    cache = assembler.LabelCache()

    def setUp(self):
        self.cache.empty()

    def test_write(self):
        self.cache.write('sort', 20)
        self.cache.write('L1', 16)

        self.assertTrue('sort' in self.cache.cache)
        self.assertTrue('L1' in self.cache.cache)

        self.assertEqual(20, self.cache.cache['sort'])
        self.assertEqual(16, self.cache.cache['L1'])

    def test_write_conflict(self):
        self.cache.write('sort', 20)
        self.assertRaises(RuntimeError, self.cache.write, *['sort', 50])

    def test_miss(self):
        hit, index = self.cache.query('sort')
        self.assertFalse(hit)
        self.assertEqual(0, index)

    def test_hit(self):
        self.cache.write('sort', 20)
        self.cache.write('L1', 16)

        hit, index = self.cache.query('sort')
        self.assertTrue(hit)
        self.assertEqual(20, index)

        hit, index = self.cache.query('L1')
        self.assertTrue(hit)
        self.assertEqual(16, index)

    def test_data(self):
        """ Ensure data is consistant across instances. """
        # write in c1, read in c2
        c1 = assembler.LabelCache()
        c1.write('sort', 20)

        c2 = assembler.LabelCache()
        hit, index = c2.query('sort')
        self.assertTrue(hit)
        self.assertEqual(20, index)

        # write in c2, read in c1
        c2.write('L1', 50)
        hit, index = c1.query('L1')
        self.assertTrue(hit)
        self.assertEqual(50, index)

        self.assertDictEqual(c1.cache, c2.cache)
        self.assertDictEqual(c1.cache, self.cache.cache)


class EncoderTests(unittest.TestCase):
    """
    Expected results come from the mipshelper.com instruction converter.
    (Please, let me know if there is a better source.)
    """

    error_message = 'encode value: {} for instruction: {} does not match expected: {}'
    encoder = assembler.Encoder()

    def run_test(self, instr, expected, pc=0):
        """
        Encodes the given instruction string and cross-references the output
        with the expected bit string.
        """
        result = self.encoder.encode_instruction(pc, instr)
        self.assertEqual(expected, result, msg=self.error_message.format(result, instr, expected))

    def test_nop(self):
        self.run_test('nop', '00000000000000000000000000000000')

    def test_add(self):
        self.run_test('add $t0, $t1, $t2', '00000001001010100100000000100000')
        self.run_test('add $s0, $s1, $s2', '00000010001100101000000000100000')

    def test_addi(self):
        self.run_test('addi $s2, $s3, 4', '00100010011100100000000000000100')
        self.run_test('addi $s0, $s0, -20', '00100010000100001111111111101100')

    def test_and(self):
        self.run_test('and $s3, $t2, $t4', '00000001010011001001100000100100')

    def test_beq(self):
        self.encoder.label_cache.write('else', 20)
        self.run_test('beq $t0, $t1, else', '00010001000010010000000000001001', pc=10)

    def test_j(self):
        self.encoder.label_cache.write('sort', 4)
        self.run_test('j sort', '00001000000000000000000000000100')

    def test_jal(self):
        self.encoder.label_cache.write('L1', 12)
        self.run_test('jal L1', '00001100000000000000000000001100')

    def test_jr(self):
        self.run_test('jr $ra', '00000011111000000000000000001000')

    def test_lw(self):
        self.run_test('lw $a0, 4($zero)', '10001100000001000000000000000100')
        self.run_test('lw $s3, 8($t1)', '10001101001100110000000000001000')
        self.run_test('lw $a1, 28($zero)', '10001100000001010000000000011100')

    def test_or(self):
        self.run_test('or $t0, $a0, $a1', '00000000100001010100000000100101')

    def test_slt(self):
        self.run_test('slt $t0, $s4, $s5', '00000010100101010100000000101010')

    def test_sll(self):
        self.run_test('sll $t1, $t1, 4', '00000000000010010100100100000000')

    def test_sw(self):
        self.run_test('sw $t5, 4($t1)', '10101101001011010000000000000100')

    def test_sub(self):
        self.run_test('sub $s3, $t0, $t1', '00000001000010011001100000100010')
