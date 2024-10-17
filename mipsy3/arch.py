"""
mipsy.arch
    ISA definitions.

See README.md for usage and general information.
"""

# application imports
from mipsy3.util import OpInfo


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

