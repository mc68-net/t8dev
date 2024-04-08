''' Opcode and instruction mappings.
'''

#   XXX Much (aside from OPCODES) duplicated from testmc.mc6800.opcodes;
#   pull up to testmc.generic.opcodes?

from    testmc.i8080.opimpl  import *

__all__ = ( 'OPCODES', 'Instructions', 'InvalidOpcode' )

####################################################################
#   Functions that return functions that take a Machine and
#   and execute the correct opcode for the given parameter.

def mvi(dst):
    return lambda m: movir(m, dst)

def mov(dst_src):
    dst, src = dst_src.split(',')
    return lambda m: movrr(m, dst, src)

def movm(src):  return lambda m: movmr(m, src)
def inx(reg):   return lambda m: inxr(m, reg)
def dcx(reg):   return lambda m: dcxr(m, reg)

####################################################################
#   Map opcodes to opcode mnemonics and implementations.
#   See `Instructions` below for mnemonic naming.

OPCODES = {

    0x00: (None,    invalid),       0x10: (None,    invalid),
    0x01: ('LXIb',  lxib),          0x11: ('LXId',  lxid),
    0x02: (None,    invalid),       0x12: (None,    invalid),
    0x03: ('INXbc', inx('bc')),     0x13: ('INXde', inx('de')),
    0x04: (None,    invalid),       0x14: (None,    invalid),
    0x05: (None,    invalid),       0x15: (None,    invalid),
    0x06: ('MVIb',  mvi('b')),      0x16: ('MVId',  mvi('d')),
    0x07: (None,    invalid),       0x17: (None,    invalid),
    0x08: (None,    invalid),       0x18: (None,    invalid),
    0x09: (None,    invalid),       0x19: (None,    invalid),
    0x0A: (None,    invalid),       0x1A: (None,    invalid),
    0x0B: ('DCXbc', dcx('bc')),     0x1B: ('DCXde', dcx('de')),
    0x0C: (None,    invalid),       0x1C: (None,    invalid),
    0x0D: (None,    invalid),       0x1D: (None,    invalid),
    0x0E: ('MVIc',  mvi('c')),      0x1E: ('MVIe',  mvi('e')),
    0x0F: (None,    invalid),       0x1F: (None,    invalid),

    0x20: (None,    invalid),       0x30: (None,    invalid),
    0x21: ('LXIh',  lxih),          0x31: ('LXIs',  lxis),
    0x22: (None,    invalid),       0x32: ('STA',   sta),
    0x23: ('INXhl', inx('hl')),     0x33: ('INXsp', inx('sp')),
    0x24: (None,    invalid),       0x34: (None,    invalid),
    0x25: (None,    invalid),       0x35: (None,    invalid),
    0x26: ('MVIh',  mvi('h')),      0x36: ('MVIl',  mvi('h')),
    0x27: (None,    invalid),       0x37: (None,    invalid),
    0x28: (None,    invalid),       0x38: (None,    invalid),
    0x29: (None,    invalid),       0x39: (None,    invalid),
    0x2A: (None,    invalid),       0x3A: (None,    invalid),
    0x2B: ('DCXhl', dcx('hl')),     0x2B: ('DCXsp', dcx('sp')),
    0x2C: (None,    invalid),       0x3C: (None,    invalid),
    0x2D: (None,    invalid),       0x3D: (None,    invalid),
    0x2E: (None,    invalid),       0x3E: ('MVIa',  mvi('a')),
    0x2F: (None,    invalid),       0x3F: (None,    invalid),

    0x40: (None,    invalid),       0x50: (None,    invalid),
    0x41: (None,    invalid),       0x51: (None,    invalid),
    0x42: (None,    invalid),       0x52: (None,    invalid),
    0x43: (None,    invalid),       0x53: (None,    invalid),
    0x44: (None,    invalid),       0x54: (None,    invalid),
    0x45: (None,    invalid),       0x55: (None,    invalid),
    0x46: (None,    invalid),       0x56: (None,    invalid),
    0x47: ('MOVba', mov('b,a')),    0x57: ('MOVda', mov('d,a')),
    0x48: (None,    invalid),       0x58: (None,    invalid),
    0x49: (None,    invalid),       0x59: (None,    invalid),
    0x4A: (None,    invalid),       0x5A: (None,    invalid),
    0x4B: (None,    invalid),       0x5B: (None,    invalid),
    0x4C: (None,    invalid),       0x5C: (None,    invalid),
    0x4D: (None,    invalid),       0x5D: (None,    invalid),
    0x4E: (None,    invalid),       0x5E: (None,    invalid),
    0x4F: ('MOVca', mov('c,a')),    0x5F: ('MOVea', mov('e,a')),

    0x60: (None,    invalid),       0x70: ('MOVmb', movm('b')),
    0x61: (None,    invalid),       0x71: ('MOVmc', movm('c')),
    0x62: (None,    invalid),       0x72: ('MOVmd', movm('d')),
    0x63: (None,    invalid),       0x73: ('MOVme', movm('e')),
    0x64: (None,    invalid),       0x74: ('MOVmh', movm('h')),
    0x65: (None,    invalid),       0x75: ('MOVml', movm('l')),
    0x66: (None,    invalid),       0x76: (None,    invalid),
    0x67: (None,    invalid),       0x77: ('MOVma', movm('a')),
    0x68: (None,    invalid),       0x78: (None,    invalid),
    0x69: (None,    invalid),       0x79: (None,    invalid),
    0x6A: (None,    invalid),       0x7A: (None,    invalid),
    0x6B: (None,    invalid),       0x7B: (None,    invalid),
    0x6C: (None,    invalid),       0x7C: (None,    invalid),
    0x6D: (None,    invalid),       0x7D: (None,    invalid),
    0x6E: (None,    invalid),       0x7E: (None,    invalid),
    0x6F: (None,    invalid),       0x7F: (None,    invalid),

    0x80: (None,    invalid),       0x90: (None,    invalid),
    0x81: (None,    invalid),       0x91: (None,    invalid),
    0x82: (None,    invalid),       0x92: (None,    invalid),
    0x83: (None,    invalid),       0x93: (None,    invalid),
    0x84: (None,    invalid),       0x94: (None,    invalid),
    0x85: (None,    invalid),       0x95: (None,    invalid),
    0x86: (None,    invalid),       0x96: (None,    invalid),
    0x87: (None,    invalid),       0x97: (None,    invalid),
    0x88: (None,    invalid),       0x98: (None,    invalid),
    0x89: (None,    invalid),       0x99: (None,    invalid),
    0x8A: (None,    invalid),       0x9A: (None,    invalid),
    0x8B: (None,    invalid),       0x9B: (None,    invalid),
    0x8C: (None,    invalid),       0x9C: (None,    invalid),
    0x8D: (None,    invalid),       0x9D: (None,    invalid),
    0x8E: (None,    invalid),       0x9E: (None,    invalid),
    0x8F: (None,    invalid),       0x9F: (None,    invalid),

    0xA0: (None,    invalid),       0xB0: (None,    invalid),
    0xA1: (None,    invalid),       0xB1: (None,    invalid),
    0xA2: (None,    invalid),       0xB2: (None,    invalid),
    0xA3: (None,    invalid),       0xB3: (None,    invalid),
    0xA4: (None,    invalid),       0xB4: (None,    invalid),
    0xA5: (None,    invalid),       0xB5: (None,    invalid),
    0xA6: (None,    invalid),       0xB6: (None,    invalid),
    0xA7: (None,    invalid),       0xB7: (None,    invalid),
    0xA8: (None,    invalid),       0xB8: (None,    invalid),
    0xA9: (None,    invalid),       0xB9: (None,    invalid),
    0xAA: (None,    invalid),       0xBA: (None,    invalid),
    0xAB: (None,    invalid),       0xBB: (None,    invalid),
    0xAC: (None,    invalid),       0xBC: (None,    invalid),
    0xAD: (None,    invalid),       0xBD: (None,    invalid),
    0xAE: (None,    invalid),       0xBE: (None,    invalid),
    0xAF: ('XRAa',  xraa),          0xBF: (None,    invalid),

    0xC0: (None,    invalid),       0xD0: (None,    invalid),
    0xC1: (None,    invalid),       0xD1: (None,    invalid),
    0xC2: (None,    invalid),       0xD2: (None,    invalid),
    0xC3: (None,    invalid),       0xD3: (None,    invalid),
    0xC4: (None,    invalid),       0xD4: (None,    invalid),
    0xC5: (None,    invalid),       0xD5: (None,    invalid),
    0xC6: (None,    invalid),       0xD6: (None,    invalid),
    0xC7: (None,    invalid),       0xD7: (None,    invalid),
    0xC8: (None,    invalid),       0xD8: (None,    invalid),
    0xC9: ('RET',   ret),           0xD9: (None,    invalid),
    0xCA: (None,    invalid),       0xDA: (None,    invalid),
    0xCB: (None,    invalid),       0xDB: (None,    invalid),
    0xCC: (None,    invalid),       0xDC: (None,    invalid),
    0xCD: (None,    invalid),       0xDD: (None,    invalid),
    0xCE: (None,    invalid),       0xDE: (None,    invalid),
    0xCF: (None,    invalid),       0xDF: (None,    invalid),

    0xE0: (None,    invalid),       0xF0: (None,    invalid),
    0xE1: (None,    invalid),       0xF1: (None,    invalid),
    0xE2: (None,    invalid),       0xF2: (None,    invalid),
    0xE3: (None,    invalid),       0xF3: (None,    invalid),
    0xE4: (None,    invalid),       0xF4: (None,    invalid),
    0xE5: (None,    invalid),       0xF5: (None,    invalid),
    0xE6: (None,    invalid),       0xF6: (None,    invalid),
    0xE7: (None,    invalid),       0xF7: (None,    invalid),
    0xE8: (None,    invalid),       0xF8: (None,    invalid),
    0xE9: (None,    invalid),       0xF9: (None,    invalid),
    0xEA: (None,    invalid),       0xFA: (None,    invalid),
    0xEB: (None,    invalid),       0xFB: (None,    invalid),
    0xEC: (None,    invalid),       0xFC: (None,    invalid),
    0xED: (None,    invalid),       0xFD: (None,    invalid),
    0xEE: (None,    invalid),       0xFE: (None,    invalid),
    0xEF: (None,    invalid),       0xFF: (None,    invalid),

}

####################################################################
#   Map instructions to opcodes

class InstructionsClass:
    def __getitem__(self, key):
        ' Return the opcode value for the given opcode name. '
        return getattr(self, key)

#   Add all opcode names as attributes to InstructionsClass.
for opcode, (mnemonic, f) in OPCODES.items():
    if mnemonic is not None:
        setattr(InstructionsClass, mnemonic, opcode)

Instructions = InstructionsClass()
