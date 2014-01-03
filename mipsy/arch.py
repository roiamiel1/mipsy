"""
mipsy.arch
    ISA definitions.

See README.md for usage and general information.
"""

# application imports
from mipsy.util import OpInfo


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

