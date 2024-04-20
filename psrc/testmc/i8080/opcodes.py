''' Opcode and instruction mappings.

    Generally we tend toward Z80 assembly mnemonics and syntax unless
    there's some reason that 8080 works better for a particular opcode.

    We use upper case for the "base" mnemonic, and lower case for register
    names. `i` refers to "immediate data," not the interrupt vector base
    register.
'''

#   XXX Much (aside from OPCODES) duplicated from testmc.mc6800.opcodes;
#   pull up to testmc.generic.opcodes?

from    testmc.i8080.opimpl  import *

__all__ = ( 'OPCODES', 'Instructions', 'InvalidOpcode' )

####################################################################
#   Functions that return functions that take a Machine and
#   and execute the correct opcode for the given parameter.
#
#   Our convention is that these start with `_` to avoid conflicts
#   with the functions from `opimpl` that actually do the work.


def _jpf(flag):     return lambda m: jp_f(m, flag)
def _jpnf(flag):    return lambda m: jp_nf(m, flag)
def _rst(addr):     return lambda m: rst(m, addr)

def _push(regs):    return lambda m: push(m, regs)
def  _pop(regs):    return lambda m:  pop(m, regs)
def _callf(flag):   return lambda m: call_f(m, flag)
def _callnf(flag):  return lambda m: call_nf(m, flag)
def _retf(flag):    return lambda m: ret_f(m, flag)
def _retnf(flag):   return lambda m: ret_nf(m, flag)

def _ldi(dst):      return lambda m: ld_ri(m, dst)
def _ld(dst_src):   return lambda m: ld_rr(m, *dst_src.split(','))
def _ldmr(src):     return lambda m: ld_mr(m, src)
def _ldrm(dest):    return lambda m: ld_rm(m, dest)

def _and(reg):      return lambda m: and_r(m, reg)
def _or(reg):       return lambda m: or_r(m, reg)
def _xor(reg):      return lambda m: xor_r(m, reg)

def _incr(reg):     return lambda m: inc_r(m, reg)
def _decr(reg):     return lambda m: dec_r(m, reg)
def _inx(reg):      return lambda m: inx_r(m, reg)
def _dcx(reg):      return lambda m: dcx_r(m, reg)

def _add(reg):      return lambda m: add_r(m, reg)
def _adc(reg):      return lambda m: adc_r(m, reg)
def _sub(reg):      return lambda m: sub_r(m, reg)
def _sbc(reg):      return lambda m: sbc_r(m, reg)
def _cmp(reg):      return lambda m: cmp_r(m, reg)
def _addhl(reg):    return lambda m: add_hlrr(m, reg)

####################################################################
#   Map opcodes to opcode mnemonics and implementations.
#   See `Instructions` below for mnemonic naming.
#
#   Mnemonic suffixes:
#   • [abcdehl]: data in register (or register pair if two letters)
#   • m: (hl), memory from address in hl
#   • p: (nnnn) immediate address ("pointer")
#   • q: (rr) address in register pair

OPCODES = {

    0x00: ('NOP',    nop),          0x10: (None,    invalid),
    0x01: ('LXIb',   lxib),         0x11: ('LXId',  lxid),
    0x02: ('LDqbca', ld_qbca),      0x12: ('LDqdea',ld_qdea),
    0x03: ('INXbc', _inx('bc')),    0x13: ('INXde',_inx('de')),
    0x04: ('INCb',  _incr('b')),    0x14: ('INCd',  _incr('d')),
    0x05: ('DECb',  _decr('b')),    0x15: ('DECd',  _decr('d')),
    0x06: ('LDbi',  _ldi('b')),     0x16: ('LDdi',  _ldi('d')),
    0x07: ('RLCA',   rlca),         0x17: ('RLA',    rla),
    0x08: (None,    invalid),       0x18: (None,    invalid),
    0x09: ('ADDhlbc',_addhl('bc')), 0x19: ('ADDhlde',_addhl('de')),
    0x0A: ('LDaqbc', ld_aqbc),      0x1A: ('LDaqde', ld_aqde),
    0x0B: ('DCXbc', _dcx('bc')),    0x1B: ('DCXde', _dcx('de')),
    0x0C: ('INCc',  _incr('c')),    0x1C: ('INCe',  _incr('e')),
    0x0D: ('DECc',  _decr('c')),    0x1D: ('DECe',  _decr('e')),
    0x0E: ('LDci',  _ldi('c')),     0x1E: ('LDei',  _ldi('e')),
    0x0F: ('RRCA',   rrca),         0x1F: ('RRA',    rra),

    0x20: (None,    invalid),       0x30: (None,    invalid),
    0x21: ('LXIh',  lxih),          0x31: ('LXIs',  lxis),
    0x22: ('LDxhl',  ld_xhl),       0x32: ('STA',   ld_xa),
    0x23: ('INXhl', _inx('hl')),    0x33: ('INXsp', _inx('sp')),
    0x24: ('INCh',  _incr('h')),    0x34: ('INCm',   inc_m),
    0x25: ('DECh',  _decr('h')),    0x35: ('DECm',   dec_m),
    0x26: ('LDhi',  _ldi('h')),     0x36: ('LDmi',   ld_mi),
    0x27: ('DAA',    daa),          0x37: ('SCF',    scf),
    0x28: (None,    invalid),       0x38: (None,    invalid),
    0x29: ('ADDhlhl',_addhl('hl')), 0x39: ('ADDhlsp',_addhl('sp')),
    0x2A: ('LDhlx',  ld_hlx),       0x3A: ('LDax',  ld_ax),
    0x2B: ('DCXhl', _dcx('hl')),    0x3B: ('DCXsp', _dcx('sp')),
    0x2C: ('INCl',  _incr('l')),    0x3C: ('INCa',  _incr('a')),
    0x2D: ('DECl',  _decr('l')),    0x3D: ('DECa',  _decr('a')),
    0x2E: ('LDli',  _ldi('l')),     0x3E: ('LDai',  _ldi('a')),
    0x2F: ('CPL',    cpl),          0x3F: ('CCF',    ccf),

    0x40: ('MOVbb', _ld('b,b')),    0x50: ('MOVdb', _ld('d,b')),
    0x41: ('MOVbc', _ld('b,c')),    0x51: ('MOVdc', _ld('d,c')),
    0x42: ('MOVbd', _ld('b,d')),    0x52: ('MOVdd', _ld('d,d')),
    0x43: ('MOVbe', _ld('b,e')),    0x53: ('MOVde', _ld('d,e')),
    0x44: ('MOVbh', _ld('b,h')),    0x54: ('MOVdh', _ld('d,h')),
    0x45: ('MOVbl', _ld('b,l')),    0x55: ('MOVdl', _ld('d,l')),
    0x46: ('MOVbm', _ldrm('b')),    0x56: ('MOVdm', _ldrm('d')),
    0x47: ('MOVba', _ld('b,a')),    0x57: ('MOVda', _ld('d,a')),
    0x48: ('MOVcb', _ld('c,b')),    0x58: ('MOVeb', _ld('e,b')),
    0x49: ('MOVcc', _ld('c,c')),    0x59: ('MOVec', _ld('e,c')),
    0x4A: ('MOVcd', _ld('c,d')),    0x5A: ('MOVed', _ld('e,d')),
    0x4B: ('MOVce', _ld('c,e')),    0x5B: ('MOVee', _ld('e,e')),
    0x4C: ('MOVch', _ld('c,h')),    0x5C: ('MOVeh', _ld('e,h')),
    0x4D: ('MOVcl', _ld('c,l')),    0x5D: ('MOVel', _ld('e,l')),
    0x4E: ('MOVcm', _ldrm('c')),    0x5E: ('MOVem', _ldrm('e')),
    0x4F: ('MOVca', _ld('c,a')),    0x5F: ('MOVea', _ld('e,a')),

    0x60: ('MOVhb', _ld('h,b')),    0x70: ('MOVmb', _ldmr('b')),
    0x61: ('MOVhc', _ld('h,c')),    0x71: ('MOVmc', _ldmr('c')),
    0x62: ('MOVhd', _ld('h,d')),    0x72: ('MOVmd', _ldmr('d')),
    0x63: ('MOVhe', _ld('h,e')),    0x73: ('MOVme', _ldmr('e')),
    0x64: ('MOVhh', _ld('h,h')),    0x74: ('MOVmh', _ldmr('h')),
    0x65: ('MOVhl', _ld('h,l')),    0x75: ('MOVml', _ldmr('l')),
    0x66: ('MOVhm', _ldrm('h')),    0x76: ('HLT',    invalid),
    0x67: ('MOVha', _ld('h,a')),    0x77: ('MOVma', _ldmr('a')),
    0x68: ('MOVlb', _ld('l,b')),    0x78: ('MOVab', _ld('a,b')),
    0x69: ('MOVlc', _ld('l,c')),    0x79: ('MOVac', _ld('a,c')),
    0x6A: ('MOVld', _ld('l,d')),    0x7A: ('MOVad', _ld('a,d')),
    0x6B: ('MOVle', _ld('l,e')),    0x7B: ('MOVae', _ld('a,e')),
    0x6C: ('MOVlh', _ld('l,h')),    0x7C: ('MOVah', _ld('a,h')),
    0x6D: ('MOVll', _ld('l,l')),    0x7D: ('MOVal', _ld('a,l')),
    0x6E: ('MOVlm', _ldrm('l')),    0x7E: ('MOVam', _ldrm('a')),
    0x6F: ('MOVla', _ld('l,a')),    0x7F: ('MOVaa', _ld('a,a')),

    0x80: ('ADDb',  _add('b')),     0x90: ('SUBb', _sub('b')),
    0x81: ('ADDc',  _add('c')),     0x91: ('SUBc', _sub('c')),
    0x82: ('ADDd',  _add('d')),     0x92: ('SUBd', _sub('d')),
    0x83: ('ADDe',  _add('e')),     0x93: ('SUBe', _sub('e')),
    0x84: ('ADDh',  _add('h')),     0x94: ('SUBh', _sub('h')),
    0x85: ('ADDl',  _add('l')),     0x95: ('SUBl', _sub('l')),
    0x86: ('ADDm',   add_m),        0x96: ('SUBm',  sub_m),
    0x87: ('ADDa',  _add('a')),     0x97: ('SUBa', _sub('a')),
    0x88: ('ADCb',  _adc('b')),     0x98: ('SBCb', _sbc('b')),
    0x89: ('ADCc',  _adc('c')),     0x99: ('SBCc', _sbc('c')),
    0x8A: ('ADCd',  _adc('d')),     0x9A: ('SBCd', _sbc('d')),
    0x8B: ('ADCe',  _adc('e')),     0x9B: ('SBCe', _sbc('e')),
    0x8C: ('ADCh',  _adc('h')),     0x9C: ('SBCh', _sbc('h')),
    0x8D: ('ADCl',  _adc('l')),     0x9D: ('SBCl', _sbc('l')),
    0x8E: ('ADCm',   adc_m),        0x9E: ('SBCm',  sbc_m),
    0x8F: ('ADCa',  _adc('a')),     0x9F: ('SBCa', _sbc('a')),

    0xA0: ('ANDb',  _and('b')),     0xB0: ('ORb',   _or('b')),
    0xA1: ('ANDc',  _and('c')),     0xB1: ('ORc',   _or('c')),
    0xA2: ('ANDd',  _and('d')),     0xB2: ('ORd',   _or('d')),
    0xA3: ('ANDe',  _and('e')),     0xB3: ('ORe',   _or('e')),
    0xA4: ('ANDh',  _and('h')),     0xB4: ('ORh',   _or('h')),
    0xA5: ('ANDl',  _and('l')),     0xB5: ('ORl',   _or('l')),
    0xA6: ('ANDm',   and_m),        0xB6: ('ORm',    or_m),
    0xA7: ('ANDa',  _and('a')),     0xB7: ('ORa',   _or('a')),
    0xA8: ('XORb',  _xor('b')),     0xB8: ('CMPb',  _cmp('b')),
    0xA9: ('XORc',  _xor('c')),     0xB9: ('CMPc',  _cmp('c')),
    0xAA: ('XORd',  _xor('d')),     0xBA: ('CMPd',  _cmp('d')),
    0xAB: ('XORe',  _xor('e')),     0xBB: ('CMPe',  _cmp('e')),
    0xAC: ('XORh',  _xor('h')),     0xBC: ('CMPh',  _cmp('h')),
    0xAD: ('XORl',  _xor('l')),     0xBD: ('CMPl',  _cmp('l')),
    0xAE: ('XORm',   xor_m),        0xBE: ('CMPm',   cmp_m),
    0xAF: ('XORa',  _xor('a')),     0xBF: ('CMPa',  _cmp('a')),

    0xC0: ('RETnz', _retnf('Z')),   0xD0: ('RETnc', _retnf('C')),
    0xC1: ('POPbc', _pop('bc')),    0xD1: ('POPde', _pop('de')),
    0xC2: ('JPnz',  _jpnf('Z')),    0xD2: ('JPnc',  _jpnf('C')),
    0xC3: ('JP',     jp),           0xD3: (None,    invalid),
    0xC4: ('CALLnz',_callnf('Z')),  0xD4: ('CALLnc', _callnf('C')),
    0xC5: ('PUSHbc',_push('bc')),   0xD5: ('PUSHde',_push('de')),
    0xC6: ('ADDi',   add_i),        0xD6: ('SUBi',   sub_i),
    0xC7: ('RST00', _rst(0x00)),    0xD7: ('RST10', _rst(0x10)),
    0xC8: ('RETz',  _retf('Z')),    0xD8: ('RETc',  _retf('C')),
    0xC9: ('RET',   ret),           0xD9: (None,    invalid),
    0xCA: ('JPz',   _jpf('Z')),     0xDA: ('JPc',   _jpf('C')),
    0xCB: (None,    invalid),       0xDB: (None,    invalid),
    0xCC: ('CALLz', _callf('Z')),   0xDC: ('CALLc', _callf('C')),
    0xCD: ('CALL',   call),         0xDD: (None,    invalid),
    0xCE: ('ADCi',   adc_i),        0xDE: ('SBCi',   sbc_i),
    0xCF: ('RST08', _rst(0x08)),    0xDF: ('RST18', _rst(0x18)),

    0xE0: ('RETpo', _retnf('P')),   0xF0: ('RETp',  _retnf('S')),
    0xE1: ('POPhl', _pop('hl')),    0xF1: ('POPaf',  popaf),
    0xE2: ('JPpo',  _jpnf('P')),    0xF2: ('JPp',   _jpnf('S')),
    0xE3: ('EXsthl', ex_sthl),      0xF3: ('DI',     di),
    0xE4: ('CALLpo',_callnf('P')),  0xF4: ('CALLp', _callnf('S')),
    0xE5: ('PUSHhl',_push('hl')),   0xF5: ('PUSHaf', pushaf),
    0xE6: ('ANDi',   and_i),        0xF6: ('ORi',    or_i),
    0xE7: ('RST20', _rst(0x20)),    0xF7: ('RST28', _rst(0x28)),
    0xE8: ('RETpe', _retf('P')),    0xF8: ('RETm',  _retf('S')),
    0xE9: ('JPhl',   jp_hl),        0xF9: ('LDsphl', ld_sphl),
    0xEA: ('JPpe',  _jpf('P')),     0xFA: ('JPm',   _jpf('S')),
    0xEB: ('EX_dehl',ex_dehl),      0xFB: ('EI',     ei),
    0xEC: ('CALLpe',_callf('P')),   0xFC: ('CALLn', _callf('S')),
    0xED: (None,    invalid),       0xFD: (None,    invalid),
    0xEE: ('XORi',   xor_i),        0xFE: ('CMPi',   cmp_i),
    0xEF: ('RST30', _rst(0x30)),    0xFF: ('RST38', _rst(0x38)),

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
