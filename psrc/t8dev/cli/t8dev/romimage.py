

class RomImage:
    ''' XXX image of a ROM
        XXX uses ROM address space (not CPU), i.e., starting at $0000
    '''

    def __init__(self, name, source=None):
        ...

    def writefile(self, path):
        ...

    def patches(self, patchspecs):
        '''  XXX takes name=... specs
        '''
        ...


'''
            dlrom = romsrcdir.joinpath(filename)
            if not dlrom.exists():
                try:
                    with urlopen(url) as response:
                        with open(dlrom, 'wb') as f:
                            self.padrom(emulator, filename, f)
                            copyfileobj(response, f)
                except HTTPError as ex:
                    err(f'{ex} for {filename!r} from {url!r}')
            copyfile(dlrom, self.emudir(filename))

    def romsrcdir(self, *components, mkdir=True):
        return path.download(
            'emulator/rom', self.suitename(), *components, mkdir=mkdir)

def test_romsrcdir():
    t = CSCP([])
    assert str(t.romsrcdir('unit-test', 'romsrcdir', mkdir=False)) \
        .endswith('/.download/emulator/rom/cscp/unit-test/romsrcdir')

    def padrom(self, emulator, filename, f):
        """ Certain files for certain emulators in the CSCP suite need to
            have padding in front of the ROM data because they're sort of
            pretending that it's a different kind of ROM (one that doesn't
            even exist for the original machine, in the case of the PC-8001
            "kanji ROM"). For the moment we just special case each instance
            here, but if we detect a pattern we may be able to generalise
            this.
        """
        if emulator == 'pc8001':
            if filename == 'KANJI1.ROM':
                f.write(b'\x00' * 0x1000)
'''
