'''

    For N80.ROM
        n80=foo.bin
        n80=@6000:bar.bin
        n80=@6000:file:bar.bin
        n80=@6000:file://tmp/bar.bin
        n80=https://gitlab.com/…/-/raw/main/rom/80/N80_102.bin
        n80=@0000:https://gitlab.com/…/-/raw/main/rom/80/N80_102.bin
        n80=@aslp:baz.p       # ASL output file w/internal offset info

    Downloaded ROM cache:
        .download/rom/https/gitlab.com/…/-/raw/main/rom/80/N80_102.bin

    Terminology:
        pathspec    /foo/bar
        urlspec     file://foo/bar
        loadspec    @1234:file://foo/bar
        patchspec   name=@1234:file://foo/bar

'''

from    pathlib  import Path

class RomImage:
    ''' XXX image of a ROM
        XXX uses ROM address space (not CPU), i.e., starting at $0000
    '''

    def __init__(self, name, loadspec=None, doload=True):
        self.name  = name
        self.url   = None
        self.path  = None
        self.image = b''
        if loadspec is not None:  self.set_loadspec(loadspec)
        if self.path and doload:  self.load()

    def set_loadspec(self, loadspec):
        self.url = 'XXX'
        self.path = Path('/XXX')

    def writefile(self, path):
        ' Write this binary image to the given filename. '
        with open(path, 'wb') as f:  self.writefd(f)

    def writefd(self, fd):
        ' Write this binary image to the given file descriptor. '
        fd.write(self.image)

    def load(self, cache=True):
        '''  Load the data from the `loadspec` passed to `__init__()` or
            `set_loadspec()` into this `RomImage`.

            If `cache` is `False` and `self.url` is set, we download the
            data from that URL, otherwise we load the data from `self.path`.

            If `cache` is `True`, we first attempt to load the data from
            `self.path`. If that file does not exist, we download the data
            from `self.url` and write a copy to `self.path`.

            XXX offset
        '''
        if not cache:
            if self.url:  self.download()
            else:         self.readfile()
        elif self.path.exists():
            self.readfile()
        else:
            self.download()
            self.writefile(self.path)

    def readfile(self):
        with open(self.path, 'rb') as f:  self.image = f.read()

    def download(self):
        ...

    def patches(self, patchspecs):
        ''' XXX takes name=... specs
            XXX return whether we used any? Or don't care?
        '''


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
