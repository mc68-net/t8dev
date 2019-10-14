from    testmc.m6502 import  Machine, Registers as R, Instructions as I
import  pytest

@pytest.fixture
def M():
    M = Machine()
    M.load('.build/obj/c64')
    return M

def test_invscr(M):
    S = M.symtab

    M.deposit(0x3FF, [0]*1026)
    M.call(S.invscr)

    assert 0x00 == M.byte(0x3FF)
    assert 0x80 == M.byte(0x400)
    assert 0x80 == M.byte(0x7FF)
    assert 0x00 == M.byte(0x800)
    assert 0x0800 == M.word(S.addr)
