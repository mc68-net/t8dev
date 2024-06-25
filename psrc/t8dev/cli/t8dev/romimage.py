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
from    urllib.request  import HTTPError, urlopen
from    urllib.parse  import urlparse
import  re
import  t8dev.path as path

class RomImage:
    ''' A `RomImage` is a sequence of bytes always starting at address $0000.
        (That is the first address in the *ROM,* these are not necessarily
        the addresses to which the ROM is mapped in the system's memory, if
        indeed it is mapped into the CPU's address space at all.)

        Each `RomImage` has an initial `source` (a URL or a path to a file)
        whence it is loaded at a given offset; it then may be patched from
        further sources each of which is loaded at its own offset.
    '''

    def __init__(self, name, loadspec=None, doload=True):
        self.name       = name
        self.image      = bytearray()
        if loadspec is not None:
            if doload:  self.load(*self.parse_loadspec(loadspec))

    LOADSPEC = re.compile(r'(@[0-9A-Fa-f]+:)?(.*)')
    SCHEME   = re.compile(r'^[A-Za-z][A-Za-z0-9+.-]*:')

    @staticmethod
    def parse_loadspec(loadspec):
        ''' Given a `loadspec` in the format ``[@hhhh:]path-or-URL``, return
            the startaddr (hex digits _hhhh_ above; $0000 if not present)
            and the path or URL.
        '''
        addr, rhs = RomImage.LOADSPEC.fullmatch(loadspec).group(1, 2)
        if addr:
            return (int(addr[1:-1], 16), rhs)
        else:
            return (0, rhs)

    @staticmethod
    def cache_file(url):
        ''' Given a URL return a (hopefully) unique filesystem path in which
            to cache the downloaded ROM image.

            There are two instances that can cause collisions that we
            (currently) don't deal with:

            1. We remove any leading and trailing slashes to avoid "blank"
               path components, but this also strips information about
               whether it was a relative or absolute path, which can create
               collisions.

            2. We entirely ignore any URL parameters, and so collide if we
               are downloading something such as ``/rom/foo?ver=1.1``
               versus ``ver=1.2``.

            Both of these problems We ignore for the moment because they
            are difficult to handle and relatively unlikely and hard to
            handle.
        '''
        u = urlparse(url)
        c = ['rom-image', u.scheme, u.hostname ]
        if u.port: c.append(u.port)
        c += u.path.strip('/').split('/')
        p = path.download(*c, mkdir=False)
        p.parent.mkdir(exist_ok=True, parents=True)
        return p

    def set_image(self, offset, bs):
        ' Set our in-memory image bytes starting at `offset` to bytes `bs`. '
        if offset > len(self.image):
            self.image += b'\x00' * (offset - len(self.image))
        self.image[offset:offset+len(bs)] = bs

    def writefile(self, path):
        ' Write this binary image to the given filename. '
        with open(path, 'wb') as f:  self.writefd(f)

    def writefd(self, fd):
        ' Write this binary image to the given file descriptor. '
        fd.write(self.image)

    def readfile(self, startaddr, path):
        with open(path, 'rb') as f:  self.set_image(startaddr, f.read())

    def load(self, offset, source, cache=True):
        ''' Load the data from `source` (a URL or path) into this RomImage,
            at offset `offset`.

            If `cache` is `False` or if `source` is a file, a load from
            `source` will always be done.

            If `cache` is `True` and `source` is a URL, the data will be
            taken from `cache_file(source)` if that file exists. If it
            doesn't exist, the downloaded data will be saved in
            `cache_file(source)`.
        '''
        if not self.SCHEME.match(str(source)):      # is path to a file?
            self.readfile(offset, source)
            return

        if cache:
            cf = self.cache_file(source)
            if cf.exists():
                self.readfile(self.startaddr, cf)
                return

        try:
            with urlopen(source) as response:
                romdata = response.read()
                self.set_image(offset, romdata)
        except HTTPError as ex:
            err(f'{ex} for {source!r}')
        if cache:
            with open(cf, 'wb') as f: f.write(romdata)

    def patches(self, patchspecs):
        ''' XXX takes name=... specs
            XXX return whether we used any? Or don't care?
        '''
        return
        raise NotImplementedError('patches()')


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
