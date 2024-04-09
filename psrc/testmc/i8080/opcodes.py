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

def movmr(src):  return lambda m: movmr_(m, src)
def movrm(dest): return lambda m: movrm_(m, dest)
def inx(reg):   return lambda m: inxr(m, reg)
def dcx(reg):   return lambda m: dcxr(m, reg)

def add(reg):   return lambda m: addr(m, reg)
def _addm():    return lambda m: adcm(m)
def adc(reg):   return lambda m: addr(m, reg)
def _adcm():    return lambda m: adcm(m)
def sub(reg):   return lambda m: subr(m, reg)
def _subm():    return lambda m: subm(m)
def sbc(reg):   return lambda m: sbcr(m, reg)
def _sbcm():    return lambda m: sbcm(m)
def cmp(reg):   return lambda m: cmpr(m, reg)
def _cmpm():    return lambda m: cmpm(m)

def _and(reg):  return lambda m: andr(m, reg)
def _andm():    return lambda m: andm(m)
def _or(reg):   return lambda m: orr(m, reg)
def _orm():     return lambda m: orm(m)
def xor(reg):   return lambda m: xorr(m, reg)
def _xorm():    return lambda m: xorm(m)

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

    0x40: ('MOVbb', mov('b,b')),    0x50: ('MOVdb', mov('d,b')),
    0x41: ('MOVbc', mov('b,c')),    0x51: ('MOVdc', mov('d,c')),
    0x42: ('MOVbd', mov('b,d')),    0x52: ('MOVdd', mov('d,d')),
    0x43: ('MOVbe', mov('b,e')),    0x53: ('MOVde', mov('d,e')),
    0x44: ('MOVbh', mov('b,h')),    0x54: ('MOVdh', mov('d,h')),
    0x45: ('MOVbl', mov('b,l')),    0x55: ('MOVdl', mov('d,l')),
    0x46: ('MOVbm', movrm('b')),    0x56: ('MOVdm', movrm('d')),
    0x47: ('MOVba', mov('b,a')),    0x57: ('MOVda', mov('d,a')),
    0x48: ('MOVcb', mov('c,b')),    0x58: ('MOVeb', mov('e,b')),
    0x49: ('MOVcc', mov('c,c')),    0x59: ('MOVec', mov('e,c')),
    0x4A: ('MOVcd', mov('c,d')),    0x5A: ('MOVed', mov('e,d')),
    0x4B: ('MOVce', mov('c,e')),    0x5B: ('MOVee', mov('e,e')),
    0x4C: ('MOVch', mov('c,h')),    0x5C: ('MOVeh', mov('e,h')),
    0x4D: ('MOVcl', mov('c,l')),    0x5D: ('MOVel', mov('e,l')),
    0x4E: ('MOVcm', movrm('c')),    0x5E: ('MOVem', movrm('e')),
    0x4F: ('MOVca', mov('c,a')),    0x5F: ('MOVea', mov('e,a')),

    0x60: ('MOVhb', mov('h,b')),    0x70: ('MOVmb', movmr('b')),
    0x61: ('MOVhc', mov('h,c')),    0x71: ('MOVmc', movmr('c')),
    0x62: ('MOVhd', mov('h,d')),    0x72: ('MOVmd', movmr('d')),
    0x63: ('MOVhe', mov('h,e')),    0x73: ('MOVme', movmr('e')),
    0x64: ('MOVhh', mov('h,h')),    0x74: ('MOVmh', movmr('h')),
    0x65: ('MOVhl', mov('h,l')),    0x75: ('MOVml', movmr('l')),
    0x66: ('MOVhm', movrm('h')),    0x76: ('HLT',   invalid),
    0x67: ('MOVha', mov('h,a')),    0x77: ('MOVma', movmr('a')),
    0x68: ('MOVlb', mov('l,b')),    0x78: ('MOVab', mov('a,b')),
    0x69: ('MOVlc', mov('l,c')),    0x79: ('MOVac', mov('a,c')),
    0x6A: ('MOVld', mov('l,d')),    0x7A: ('MOVad', mov('a,d')),
    0x6B: ('MOVle', mov('l,e')),    0x7B: ('MOVae', mov('a,e')),
    0x6C: ('MOVlh', mov('l,h')),    0x7C: ('MOVah', mov('a,h')),
    0x6D: ('MOVll', mov('l,l')),    0x7D: ('MOVal', mov('a,l')),
    0x6E: ('MOVlm', movrm('l')),    0x7E: ('MOVam', movrm('a')),
    0x6F: ('MOVla', mov('l,a')),    0x7F: ('MOVaa', mov('a,a')),

    0x80: ('ADDb',  add('b')),      0x90: ('SUBx',  sub('x')),
    0x81: ('ADDc',  add('c')),      0x91: ('SUBx',  sub('x')),
    0x82: ('ADDd',  add('d')),      0x92: ('SUBx',  sub('x')),
    0x83: ('ADDe',  add('e')),      0x93: ('SUBx',  sub('x')),
    0x84: ('ADDh',  add('h')),      0x94: ('SUBx',  sub('x')),
    0x85: ('ADDl',  add('l')),      0x95: ('SUBx',  sub('x')),
    0x86: ('ADDm',  _addm()),       0x96: ('SUBx',  _subm()),
    0x87: ('ADDa',  add('a')),      0x97: ('SUBx',  sub('x')),
    0x88: ('ADCx',  adc('x')),      0x98: ('SBCx',  sbc('x')),
    0x89: ('ADCx',  adc('x')),      0x99: ('SBCx',  sbc('x')),
    0x8A: ('ADCx',  adc('x')),      0x9A: ('SBCx',  sbc('x')),
    0x8B: ('ADCx',  adc('x')),      0x9B: ('SBCx',  sbc('x')),
    0x8C: ('ADCx',  adc('x')),      0x9C: ('SBCx',  sbc('x')),
    0x8D: ('ADCx',  adc('x')),      0x9D: ('SBCx',  sbc('x')),
    0x8E: ('ADCx',  _adcm()),       0x9E: ('SBCx',  _sbcm()),
    0x8F: ('ADCx',  adc('x')),      0x9F: ('SBCx',  sbc('x')),

    0xA0: ('ANDx',  _and('x')),     0xB0: ('ORx',   _or('x')),
    0xA1: ('ANDx',  _and('x')),     0xB1: ('ORx',   _or('x')),
    0xA2: ('ANDx',  _and('x')),     0xB2: ('ORx',   _or('x')),
    0xA3: ('ANDx',  _and('x')),     0xB3: ('ORx',   _or('x')),
    0xA4: ('ANDx',  _and('x')),     0xB4: ('ORx',   _or('x')),
    0xA5: ('ANDx',  _and('x')),     0xB5: ('ORx',   _or('x')),
    0xA6: ('ANDx',  _andm()),       0xB6: ('ORx',   _orm()),
    0xA7: ('ANDx',  _and('x')),     0xB7: ('ORx',   _or('x')),
    0xA8: ('XORx',  xor('x')),      0xB8: ('CMPx',  cmp('x')),
    0xA9: ('XORx',  xor('x')),      0xB9: ('CMPx',  cmp('x')),
    0xAA: ('XORx',  xor('x')),      0xBA: ('CMPx',  cmp('x')),
    0xAB: ('XORx',  xor('x')),      0xBB: ('CMPx',  cmp('x')),
    0xAC: ('XORx',  xor('x')),      0xBC: ('CMPx',  cmp('x')),
    0xAD: ('XORx',  xor('x')),      0xBD: ('CMPx',  cmp('x')),
    0xAE: ('XORx',  _xorm()),       0xBE: ('CMPx',  _cmpm()),
    0xAF: ('XORa',  xor('a')),      0xBF: ('CMPx',  cmp('x')),

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
