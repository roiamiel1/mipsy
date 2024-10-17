"""
mipsy.encoder
    Instruction encoder.

See README.md for usage and general information.
"""

# system imports
import re
import bitstruct
import bitstring
from dataclasses import dataclass
from enum import Enum, EnumMeta
from typing import List, Optional

from mipsy3.arch import MIPS


class DirectValueMeta(EnumMeta):
    "Metaclass that allows for directly getting an enum attribute"
    def __getattribute__(cls, name):
        value = super().__getattribute__(name)
        if isinstance(value, cls):
            value = value.value
        return value


class Opcode(Enum, metaclass=DirectValueMeta):
    NOP = "nop"
    ADD = "add"
    ADDI = "addi"
    AND = "and"
    BEQ = "beq"
    J = "j"
    JAL = "jal"
    JR = "jr"
    LW = "lw"
    OR = "or"
    SLT = "slt"
    SLL = "sll"
    SW = "sw"
    SUB = "sub"


class OpArg(Enum, metaclass=DirectValueMeta):
    RD = "rd"
    RS = "rs"
    RT = "rt"
    IMM = "imm"
    SHAMT = "shamt"
    LABEL = "label"


class OpFormat(Enum, metaclass=DirectValueMeta):
    R = "R" # Registers
    I = "I" # Immediate
    J = "J" # Jump


class Regs(Enum, metaclass=DirectValueMeta):
    ZERO = "$zero"
    AT = "$at"
    V0 = "$v0"
    V1 = "$v1"
    A0 = "$a0"
    A1 = "$a1"
    A2 = "$a2"
    A3 = "$a3"
    T0 = "$t0"
    T1 = "$t1"
    T2 = "$t2"
    T3 = "$t3"
    T4 = "$t4"
    T5 = "$t5"
    T6 = "$t6"
    T7 = "$t7"
    S0 = "$s0"
    S1 = "$s1"
    S2 = "$s2"
    S3 = "$s3"
    S4 = "$s4"
    S5 = "$s5"
    S6 = "$s6"
    S7 = "$s7"
    T8 = "$t8"
    T9 = "$t9"
    K0 = "$k0"
    K1 = "$k1"
    GP = "$gp"
    SP = "$sp"
    FP = "$fp"
    RA = "$ra"


@dataclass
class OpInfo(object):
    format: OpFormat
    opcode_code: int
    funct_code: Optional[int]
    args: List[OpArg]

class LabelIndex(object):
    def __init__(self):
        self._label_to_index = {}

    def __getitem__(self, key, default_value=None):
        return self._label_to_index.get(key, default=default_value)

    def __setitem__(self, key, value):
        assert key not in self._label_to_index, f"Key: `{key}` already exists"
        self._label_to_index[key] = value

    def clear(self):
        self._label_to_index.clear()


class Encoder(object):
    _INST_TEST = re.compile(r"( *)(?P<opcode>\w*)( *)(?P<args>[A-Za-z0-9 ,\[\]\+]*)", re.IGNORECASE)

    _FORMAT_TO_STRUCT = {
        OpFormat.R: ">u6u5u5u5u5u6",
        OpFormat.I: ">u6u5u5s16",
        OpFormat.J: ">u6s26",
    }

    _FORMAT_TO_OP_ARGS = {
        OpFormat.R: [OpArg.RS, OpArg.RT, OpArg.RD, OpArg.SHAMT],
        OpFormat.I: [OpArg.RS, OpArg.RT, OpArg.IMM],
        OpFormat.J: [OpArg.LABEL],
    }

    _OPCODES_TO_OP_INFO = {
        Opcode.NOP:  OpInfo(OpFormat.R, 0x00, 0x00, [OpArg.RD, OpArg.RS, OpArg.RT]),
        Opcode.ADD:  OpInfo(OpFormat.R, 0x00, 0x20, [OpArg.RD, OpArg.RS, OpArg.RT]),
        Opcode.ADDI: OpInfo(OpFormat.I, 0x08, None, [OpArg.RT, OpArg.RS, OpArg.IMM]),
        Opcode.AND:  OpInfo(OpFormat.R, 0x00, 0x24, [OpArg.RD, OpArg.RS, OpArg.RT]),
        Opcode.BEQ:  OpInfo(OpFormat.I, 0x04, None, [OpArg.RS, OpArg.RT, OpArg.LABEL]),
        Opcode.J:    OpInfo(OpFormat.J, 0x02, None, [OpArg.LABEL]),
        Opcode.JAL:  OpInfo(OpFormat.J, 0x03, None, [OpArg.LABEL]),
        Opcode.JR:   OpInfo(OpFormat.R, 0x00, 0x08, [OpArg.RS]),
        Opcode.LW:   OpInfo(OpFormat.I, 0x23, None, [OpArg.RT, OpArg.IMM, OpArg.RS]),
        Opcode.OR:   OpInfo(OpFormat.R, 0x00, 0x25, [OpArg.RD, OpArg.RS, OpArg.RT]),
        Opcode.SLT:  OpInfo(OpFormat.R, 0x00, 0x2a, [OpArg.RD, OpArg.RS, OpArg.RT]),
        Opcode.SLL:  OpInfo(OpFormat.R, 0x00, 0x00, [OpArg.RD, OpArg.RT, OpArg.SHAMT]),
        Opcode.SW:   OpInfo(OpFormat.I, 0x2b, None, [OpArg.RT, OpArg.IMM, OpArg.RS]),
        Opcode.SUB:  OpInfo(OpFormat.R, 0x00, 0x22, [OpArg.RD, OpArg.RS, OpArg.RT]),
    }

    _REGS_TO_CODE = {
        Regs.ZERO: 0, 
        Regs.AT: 1,
        Regs.V0: 2,
        Regs.V1: 3,
        Regs.A0: 4,
        Regs.A1: 5,
        Regs.A2: 6,
        Regs.A3: 7,
        Regs.T0: 8,
        Regs.T1: 9,
        Regs.T2: 10,
        Regs.T3: 11,
        Regs.T4: 12,
        Regs.T5: 13,
        Regs.T6: 14,
        Regs.T7: 15,
        Regs.S0: 16,
        Regs.S1: 17,
        Regs.S2: 18,
        Regs.S3: 19,
        Regs.S4: 20,
        Regs.S5: 21,
        Regs.S6: 22,
        Regs.S7: 23,
        Regs.T8: 24,
        Regs.T9: 25,
        Regs.K0: 26,
        Regs.K1: 27,
        Regs.GP: 28,
        Regs.SP: 29,
        Regs.FP: 30,
        Regs.RA: 31
    }

    def encode_instruction(self, pc, inst, label_index: LabelIndex):
        match = Encoder._INST_TEST.match(inst)

        if not match:
            return

        opcode = match.group('opcode').lower().strip() 
        args = list(filter([x.strip() for x in match.group('args').replace(",", " ").split()]))

        assert opcode in Encoder._OPCODES_TO_OP_INFO, f"Unknown opcode: {opcode}"
        opinfo = Encoder._OPCODES_TO_OP_INFO[opcode]
        
        assert len(opinfo.args) == len(args), "Args count unmatch requeird"
        args_values = dict(zip(opinfo.args, args))

        # TODO: translate registers to numbers

        encoding_values = [opinfo.opcode_code]
        for op_arg in Encoder._FORMAT_TO_OP_ARGS[opinfo.format]:
            if op_arg == OpArg.LABEL:
                encoding_values.append(label_index[args_values[OpArg.LABEL]])
            else:
                encoding_values.append(args_values.get(op_arg, 0))

        if opinfo.format == OpFormat.R:
            encoding_values.append(opinfo.funct_code or 0)

        return bitstruct.pack(Encoder._FORMAT_TO_STRUCT[opinfo.format], *encoding_values)
