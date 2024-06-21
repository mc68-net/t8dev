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
    ''' XXX image of a ROM
        XXX uses ROM address space (not CPU), i.e., starting at $0000
    '''

    def __init__(self, name, loadspec=None, doload=True):
        self.name       = name
        self.url        = None
        self.path       = None
        self.startaddr  = 0x0000
        self.image      = b''
        if loadspec is not None:  self.set_loadspec(loadspec)
        if self.path and doload:  self.load()

    LOADSPEC = re.compile(r'(@[0-9A-Fa-f]+:)?(.*)')
    SCHEME   = re.compile(r'^[A-Za-z][A-Za-z0-9+.-]*:')

    def set_loadspec(self, loadspec):
        ''' Given a *loadspec*, set:
            - `startaddr` to the start address given in the loadspec,
              or $0000 if not present.
            - `url` to the URL given in the loadspec, if present
            - `path` to the local path at which we cache the data
              downloaded from that URL, or the given path if it's
              not a URL, and
        '''
        addr, rhs = self.LOADSPEC.fullmatch(loadspec).group(1, 2)
        if addr:
            self.startaddr = int(addr[1:-1], 16)
        if self.SCHEME.match(rhs):
            self.url = rhs
            self.path = self.cache_file(self.url)
        else:
            self.path = rhs

    def cache_file(self, url):
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
        p = urlparse(url)
        c = ['rom-image', p.scheme, p.hostname ]
        if p.port: c.append(p.port)
        c += p.path.strip('/').split('/')
        return path.download(*c)

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
        try:
            with urlopen(self.url) as response:
                self.image = response.read()
        except HTTPError as ex:
            err(f'{ex} for {filename!r} from {self.url!r}')

    def patches(self, patchspecs):
        ''' XXX takes name=... specs
            XXX return whether we used any? Or don't care?
        '''
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
