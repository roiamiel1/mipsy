"""
mipsy.encoder
    Instruction encoder.

See README.md for usage and general information.
"""

# system imports
import bitstring

# application imports
from mipsy.arch import MIPS
from mipsy.util import LabelCache, ParseInfo


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
        'beq'   : ParseInfo(['rs', 'rt', 'label'], t.RI_type),
        'j'     : ParseInfo(['label'],            t.J_type),
        'jal'   : ParseInfo(['label'],            t.J_type),
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
        # ISA definitions
        self.mips = MIPS()

        # Label resolution cache
        self.label_cache = LabelCache()

    def encode_instruction(self, pc, instr):
        """
        Given an instruction string, generate the encoded bit string.
        PC (instruction index is used for branch label resolution)
        """
        data = instr.split()
        operation = data[0]

        try:
            mips_op_info = MIPS.operations[operation]
        except KeyError, e:
            raise RuntimeError('Unknown operation: {}'.format(operation))

        # Grab the parsing info from the assembler operations table
        # Generate the initial operand map using the specified tokenizer
        parse_info = self.operations[operation]
        encoding_map = parse_info.tokenizer(parse_info.tokens, ''.join(data[1:]))

        # Get the binary equivalents of the operands and MIPS operation information
        self.resolve_operands(encoding_map, operation, pc)

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

    def resolve_operands(self, encoding_map, operation, pc):
        """
        Converts generic register references (such as $t0, $t1, etc), immediate values, and jump addresses
        to their binary equivalents.
        """
        convert = Encoder.to_binary
        branch_replace = False
        jump_replace = False

        for operand, value in encoding_map.iteritems():
            if (operand == 'rs' or operand == 'rt' or operand == 'rd'):
                encoding_map[operand] = MIPS.registers[value]

            elif (operand == 'imm'):
                encoding_map[operand] = convert(int(value), MIPS.IMMEDIATE_SIZE)

            elif (operand == 'addr'):
                encoding_map[operand] = convert(int(value), MIPS.ADDRESS_SIZE)

            elif (operand == 'shamt'):
                encoding_map[operand] = convert(int(value), MIPS.SHAMT_SIZE)

            elif (operand == 'label'):
                label = encoding_map[operand]
                hit, index = self.label_cache.query(label)

                if not hit:
                    raise RuntimeError('No address found for label: {}'.format(label))

                if ((operation == 'beq') or (operation == 'bne')):
                    # Calculate the relative instruction offset. The MIPS ISA uses
                    # PC + 4 + (branch offset) to resolve branch targets.
                    if index > pc:
                        encoding_map[operand] = convert(index - pc - 1, MIPS.IMMEDIATE_SIZE)
                    elif index < pc:
                        encoding_map[operand] = convert((pc + 1) - index, MIPS.IMMEDIATE_SIZE)
                    else:
                        # Not sure why a branch would resolve to itself, but ok
                        # (PC + 4) - 4 = 
                        encoding_map[operand] = convert(-1, MIPS.IMMEDIATE_SIZE)

                    branch_replace = True

                elif ((operation == 'j') or (operation == 'jal')):
                    # Jump addresses are absolute
                    encoding_map[operand] = convert(index, MIPS.ADDRESS_SIZE)
                    jump_replace = True

        # Need to convert references to 'label' back to references the instruction
        # encoding string recognizes, otherwise we end up with the default value (zero)
        # This doesn't feel very clean, but working on a fix.
        if branch_replace:
            encoding_map['imm'] = encoding_map['label']
        elif jump_replace:
            encoding_map['addr'] = encoding_map['label']

    @staticmethod
    def to_binary(decimal, length):
        """
        Given a decimal, generate the binary equivalent string of
        given length.
        e.g. binary(2, 5) = 00010
        """
        b = bitstring.Bits(int=decimal, length=length)
        return b.bin

