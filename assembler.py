"""
Basic MIPS assembler
See README.md for usage and general information.
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


from lib import bitstring

import re
import argparse
import logging

logging.root.setLevel(logging.DEBUG)


class OpInfo(object):
    """
    Operation template to query against during encoding.
    This is the operation information immediately available upon reference
    to the MIPS reference card.
    """
    def __init__(self, format, opcode, funct):
        self.format = format
        self.opcode = opcode
        self.funct = funct


class ParseInfo(object):
    """
    Template that defines the token interpretation and the function to make those tokens.
    """
    def __init__(self, tokens, tokenizer):
        self.tokens = tokens
        self.tokenizer = tokenizer


class MIPS(object):
    """
    Stores general information and formatting for the MIPS32 ISA.
    Generates instruction instances for use in instruction encoding.
    """
    WORD_SIZE      = 32
    IMMEDIATE_SIZE = 16
    ADDRESS_SIZE   = 26
    SHAMT_SIZE     = 5

    INSTRUCTION_FORMATS = ['R', 'I', 'J']

    # Register name to 5-bit binary mapping
    # e.g. $t0 -> 1000 (8)
    registers = {
        '$zero' : '00000', '$t0' : '01000', '$s0' : '10000', '$t8' : '11000',
        '$at'   : '00001', '$t1' : '01001', '$s1' : '10001', '$t9' : '11001',
        '$v0'   : '00010', '$t2' : '01010', '$s2' : '10010', '$k0' : '11010',
        '$v1'   : '00011', '$t3' : '01011', '$s3' : '10011', '$k1' : '11011',
        '$a0'   : '00100', '$t4' : '01100', '$s4' : '10100', '$gp' : '11100',
        '$a1'   : '00101', '$t5' : '01101', '$s5' : '10101', '$sp' : '11101',
        '$a2'   : '00110', '$t6' : '01110', '$s6' : '10110', '$fp' : '11110',
        '$a3'   : '00111', '$t7' : '01111', '$s7' : '10111', '$ra' : '11111',
    }

    # Instruction to opcode mapping
    # Value is dictionary with instruction attribute access (instruction format, opcode, funct code (if applicable))
    operations = {
        'nop'   : OpInfo('R', '000000', '000000'),
        'add'   : OpInfo('R', '000000', '100000'),
        'addi'  : OpInfo('I', '001000', None),
        'and'   : OpInfo('R', '000000', '100100'),
        'beq'   : OpInfo('I', '000100', None),
        'j'     : OpInfo('J', '000010', None),
        'jal'   : OpInfo('J', '000011', None),
        'jr'    : OpInfo('R', '000000', '001000'),
        'lw'    : OpInfo('I', '100011', '100011'),
        'or'    : OpInfo('R', '000000', '100101'),
        'slt'   : OpInfo('R', '000000', '101010'),
        'sll'   : OpInfo('R', '000000', '000000'),
        'sw'    : OpInfo('I', '101011', None),
        'sub'   : OpInfo('R', '000000', '100010'),
    }

    class Instruction(object):
        """
        An instruction defines an encoding and a default operand map.
        Encoding is common across all instructions and is simply mapping the given
        operands in the operand map to the operand's encoding position.
        """
        def encode(self, encoding_map):
            """ Returns the final binary encoding, overriding the default operand values """
            self.encoding_map.update(encoding_map)
            return self.encoding.format(**(self.encoding_map))

    class R_Instruction(Instruction):
        def __init__(self):
            self.encoding = '{opcode}{rs}{rt}{rd}{shamt}{funct}'
            self.encoding_map = {
                'opcode': '000000',
                'rs': '00000',
                'rt': '00000',
                'rd': '00000',
                'shamt': '00000',
                'funct': '000000',
            }

    class I_Instruction(Instruction):
        def __init__(self):
            self.encoding = '{opcode}{rs}{rt}{imm}'
            self.encoding_map = {
                'opcode': '000000',
                'rs': '00000',
                'rt': '00000',
                'imm': '0000000000000000',
            }

    class J_Instruction(Instruction):
        def __init__(self):
            self.encoding = '{opcode}{addr}'
            self.encoding_map = {
                'opcode': '000000',
                'addr': '00000000000000000000000000',
            }

    def generate_instruction(self, instruction_format):
        instruction = None

        try:
            # Dynamically get an instruction instance and initialize with op_info
            instruction = getattr(self, '{}_Instruction'.format(instruction_format))()
        except AttributeError as e:
            raise RuntimeError('Invalid instruction type')

        return instruction


class Singleton(type):
    """
    Common singleton pattern utilizing Python's "metaclass" attribute.
    """
    _instances = {}
    def __call__(kls, *args, **kwargs):
        if kls not in kls._instances:
            kls._instances[kls] = super(Singleton, kls).__call__(*args, **kwargs)
        return kls._instances[kls]


class LabelCache(object):
    """
    Stores a cache of labels mapped to their instruction index.
    The cache data is shared across instances.
    """
    __metaclass__ = Singleton

    def __init__(self):
        self.cache = {}

    def query(self, label):
        """
        Returns (hit, index) tuple.
        hit is a boolean, signifying label presence in the cache
        index is an integer, the instruction index for the label entry
        """
        try:
            return True, self.cache[label]
        except KeyError, e:
            return False, 0

    def write(self, label, index):
        """
        Saves a new label, index mapping to the cache.
        Raises a RuntimeError on a conflict.
        """
        if label in self.cache:
            if self.cache[label] != index:
                error_message = 'cache_conflict on label: {} with index: {}\ncache dump: {}'.format(label, index, self.cache)
                raise RuntimeError(error_message)
        else:
            self.cache[label] = index

    def empty(self):
        self.cache.clear()


class Encoder(object):
    """
    Responsible for encoding individual instructions and querying the label cache.
    """

    class tokenizer(object):
        """
        Defines a 'list' of tokenizing functions used for varying instructions.
        Each 'tokenizer' returns a dictionary mapping the specified operands to their tokens
        from the instruction data (the portion of the instruction following the operation)

        instruction = (operation) (instruction_data) <-- here, we're only concerned with instruction_data
        """
        def map_operands(self, to_split, operands):
            """
            Helper method.
            Maps operands to the preprocessed instruction data string.
            """
            operand_values = to_split.split()

            if len(operands) != len(operand_values):
                raise RuntimeError('instruction contains too many operands')

            operand_map = {}
            for i in range(len(operands)):
                operand_map[operands[i]] = operand_values[i]

            return operand_map

        def RI_type(self, operands, instruction_data):
            """
            The RI_type tokenizer takes instructions with the format:
            (operation) [(operand1), (operand2), (operand3)]
            """
            to_split = instruction_data.replace(',', ' ')
            return self.map_operands(to_split, operands)

        def J_type(self, operands, instruction_data):
            """
            The J_type tokenizer takes jump (j, jal, jr) instructions
            with the format:
            (operation) [operand]
            """
            return self.map_operands(instruction_data, operands)

        def load_store(self, operands, instruction_data):
            """
            The load_store tokenizer takes instructions with the format:
            (operation) [operand1, (operand2)(operand3)]
            """
            # Clear out commas and the parenthesis surrounding the base register
            to_split = instruction_data.replace(',', ' ').replace('(', ' ').replace(')', ' ')
            return self.map_operands(to_split, operands)

        def nop(self, operands, instruction_data):
            """
            The nop tokenizer simply maps all the given operands to register $zero.
            """
            return {operand: '$zero' for operand in operands}

    # The assembler operation table defines the parsing rules
    # for a given instruction. The parsing rules are used to
    # map tokens in the instruction string to register address
    # and immediate value positions. (rs, rt, rd, etc)

    t = tokenizer()

    operations = {
        'nop'   : ParseInfo(['rd', 'rs', 'rt'],  t.nop),
        'add'   : ParseInfo(['rd', 'rs', 'rt'],  t.RI_type),
        'addi'  : ParseInfo(['rt', 'rs', 'imm'], t.RI_type),
        'and'   : ParseInfo(['rd', 'rs', 'rt'],  t.RI_type),
        'beq'   : ParseInfo(['rs', 'rt', 'imm'], t.RI_type),
        'j'     : ParseInfo(['addr'],            t.J_type),
        'jal'   : ParseInfo(['addr'],            t.J_type),
        'jr'    : ParseInfo(['rs'],              t.RI_type),
        'lw'    : ParseInfo(['rt', 'imm', 'rs'], t.load_store),
        'or'    : ParseInfo(['rd', 'rs', 'rt'],  t.RI_type),
        'slt'   : ParseInfo(['rd', 'rs', 'rt'],  t.RI_type),
        'sll'   : ParseInfo(['rd', 'rt', 'shamt'], t.RI_type),
        'sw'    : ParseInfo(['rt', 'imm', 'rs'], t.load_store),
        'sub'   : ParseInfo(['rd', 'rs', 'rt'],  t.RI_type),
        # TODO ...
    }

    def __init__(self):
        self.mips = MIPS()

    def encode_instruction(self, instr):
        """
        Given an instruction string, generate the encoded bit string.
        """
        data = instr.split()
        operation = data[0]
        mips_op_info = MIPS.operations[operation]

        # Grab the parsing info from the assembler operations table
        # Generate the initial operand map using the specified tokenizer
        parse_info = self.operations[operation]
        encoding_map = parse_info.tokenizer(parse_info.tokens, ''.join(data[1:]))

        # Get the binary equivalents of the operands and MIPS operation information
        self.resolve_operands(encoding_map)

        # Pull MIPS operation info into encoding map
        self.resolve_operation_info(encoding_map, mips_op_info)

        instruction = self.mips.generate_instruction(mips_op_info.format)
        return instruction.encode(encoding_map)

    def resolve_operation_info(self, encoding_map, mips_op_info):
        """
        Adds the predefined operation info (opcode, funct) to the current encoding map.
        """
        encoding_map['opcode'] = mips_op_info.opcode
        encoding_map['funct'] = mips_op_info.funct

    def resolve_operands(self, encoding_map):
        """
        Converts generic register references (such as $t0, $t1, etc), immediate values, and jump addresses
        to their binary equivalents.
        """
        convert = Encoder.to_binary

        for operand, value in encoding_map.iteritems():
            if (operand == 'rs' or operand == 'rt' or operand == 'rd'):
                encoding_map[operand] = MIPS.registers[value]

            elif (operand == 'imm'):
                encoding_map[operand] = convert(int(value), MIPS.IMMEDIATE_SIZE)

            elif (operand == 'addr'):
                encoding_map[operand] = convert(int(value), MIPS.ADDRESS_SIZE)

            elif (operand == 'shamt'):
                encoding_map[operand] = convert(int(value), MIPS.SHAMT_SIZE)

            else: pass

    @staticmethod
    def to_binary(decimal, length):
        """
        Given a decimal, generate the binary equivalent string of
        given length.
        e.g. binary(2, 5) = 00010
        """
        b = bitstring.Bits(int=decimal, length=length)
        return b.bin


class MIPSAssembler(object):
    """
    Responsible for file I/O and building the final instruction memory.
    Relies on the Encoder to build individual instruction bit strings.
    """

    def __init__(self):
        # Initialize and load command line args
        argparser = argparse.ArgumentParser(description='(Extremely) basic MIPS32 assembler.')

        argparser.add_argument('in_path')
        argparser.add_argument('-o', dest='out_path', default='out.bin')

        self.args = argparser.parse_args()

        # List of encoded instructions and their index (PC)
        self.instructions = []
        self.pc = 0

        # Label cache and record of instructions that need resolution.
        # If the label present in the instruction is not in the label cache
        # (i.e. cannot be encoded) we write to the instruction list and store
        # a reference back to later resolve those labels when they become available.
        self.label_cache = LabelCache()

        # label --> [list of instruction indices using label]
        # Entry is cleared when label address becomes available.
        self.resolve = {}

        # Instruction encoder
        self.encoder = Encoder()

    def run(self):
        # Regular expressions to match input against
        # If no match is made with these, we assume the current input line
        # is an instruction and attempt to parse as such
        regex = {
            'label': re.compile(r'[\w]+[ ]*:[ ]*[\r\n]+'),
            'label_instruction': re.compile(r'[\w]+[ ]*:[ ]*.+[\r\n]+')
        }

        with open(self.args.in_path) as f:
            file_content = f.readlines()
            f.close()

        # strip surrounding whitespace and match against regex
        for line in file_content:
            # Skip empty lines
            if line != '\n':
                if regex['label'].match(line):
                    # Hold PC constant on a label only line
                    self.process_label(line.strip())

                elif regex['label_instruction'].match(line):
                    self.process_label_instruction(line.strip())
                    self.pc += 1

                else:
                    self.process_instruction(line.strip())
                    self.pc += 1

    def process_label(self, line):
        """ Update label cache and keep instruction count constant. """
        logging.debug('found label: {}'.format(line))
        self.label_cache.write(line.replace(':', ''), self.pc)

    def process_label_instruction(self, line):
        """ Update label cache, pass instruction to encoder, increment instruction count. """
        logging.debug('found label-instruction combination: {}'.format(line))
        tokens = line.split(':')
        self.label_cache.write(tokens[0].strip(), self.pc)
        self.process_instruction(tokens[1].strip())

    def process_instruction(self, instr):
        """ Attempt to parse as an instruction using the encoder and save to the master instruction list. """
        # encoded, label, bitstring = self.encoder.encode_instruction(self.pc, instr)
        logging.debug('processing instruction: {}'.format(instr))
        self.instructions.append(instr)

    def write(self):
        # Check for unresolved instructions
        if self.resolve.keys():
            raise RuntimeError('Error: unresolved labels\n{}'.format(self.label_error()))

        # Write instruction memory to file
        # TODO: this can be customized using an output "formatter"
        out = open(self.args.out_path, 'w')
        for instruction in self.instructions:
            out.write('{}\n'.format(instruction))

        out.close()

    def label_error(self):
        """
        Helper method. Pretty prints label resolution error. (No label found)
        Format: "unresolved reference to 'label': instruction"
        """
        message = []
        for key, value in self.resolve.iteritems():
            message.append('\tunresolved reference to \'{}\': {}\n'.format(key, value[0]))

        return ''.join(message)


if __name__ == '__main__':
    assembler = MIPSAssembler()

    try:
        assembler.run()
        # assembler.write()
    except Exception, e:
        print e.message
