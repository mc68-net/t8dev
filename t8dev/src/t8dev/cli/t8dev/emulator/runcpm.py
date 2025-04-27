' RunCPM is a CP/M emulator that uses the host filesystem. '

from    pathlib  import Path
from    shutil  import  copyfile
from    zipfile  import ZipFile

from    t8dev.cli.t8dev.emulator.suite  import Suite
from    t8dev.cli.t8dev.shared  import vprint
from    t8dev.cli.t8dev.util  import cwd
from    t8dev.cpm  import compile_submit
import  t8dev.path  as path
import  t8dev.run  as run

class RunCPM(Suite):
    #   XXX This requires that RunCPM be in the path. We should check this
    #   and suggest `t8dev buildtoolset RunCPM` if it's not present.

    suitedesc = 'RunCPM CP/M 2.x emulator'

    @classmethod
    def setargparser(cls, parser):
        parser.add_argument('-a', '--autorun', action='store_true',
            help='automatically run the .COM file given as first argument')
        parser.add_argument('file', nargs='*',
            help='file to copy to A: drive')

    def run(self):
        #   XXX We use `=X` to specify option X, because `-X' will be
        #   consumed by the t8dev options parser. We need to get that
        #   options parser to use subcommands that can have their own
        #   separate options.
        self.emudir = path.build('emulator', self.suitename())
        self.setup_emudir(self.args.autorun)
        with cwd(self.emudir):
            #   RunCPM clears the screen on start, as well as doing other
            #   less annoying bits termios terminal manipulation. Set the
            #   terminal type to `dumb` so that it doesn't do this.
            run.tool('RunCPM', envupdate={ 'TERM': 'dumb' })

    def setup_emudir(self, autorun=False):
        #   Set up drives.
        A0, B0, C0, D0 = drives = tuple( Path(f'./{d}/0') for d in 'ABCD' )
        with cwd(self.emudir):
            for drive in drives:  drive.mkdir(exist_ok=True, parents=True)

        #   Copy specified files to drive A.
        for file in map(Path, self.args.file):
           self.copycpmfile(file, A0)

        #   Copy standard CP/M commands to drive C, if they are present.
        #   These can be installed with `t8dev buildtoolset osimg`.
        for file in path.tool('src/osimg/cpm/2.2/').glob('*'):
           self.copycpmfile(file, C0)

        #   Copy RunCPM-supplied commands to drive D, if present.
        #   Note that this would be _required_ in order to get EXIT.COM
        #   if we were buildiing with a different CCP, which we might
        #   well want to do at some point.
        file = path.tool('src/RunCPM/DISK/A0.ZIP')
        if file.exists(): self.copycpmzip(file, D0, subdir='A/0/')

        #   Build `$$$.SUB` file if we're auto-running the first argument.
        if autorun:
            #   Using XXX.COM to run a program in RunCPM often works, but
            #   not always; e.g. `TMON100.COM` can't seem to find that
            #   file, while `TMON100` works. So make sure we drop `.COM`.
            commands = [Path(self.args.file[0]).stem.upper(), 'EXIT']
            vprint(1, 'RunCPM', f'autorun: {commands}')
            subdata = compile_submit(commands)
            with open(self.emudir.joinpath(A0, '$$$.SUB'), 'wb') as f:
                f.write(subdata)

    def copycpmfile(self, src:Path, dir:Path):
        ''' Copy `src` to the `dir` directory under `self.emudir`.

            This converts filenames to all upper-case because, while RunCPM
            will show lower-case filenames (as upper case) in a directory
            listing, it will not find them if you try to run them as
            commands. This will blindly overwrite existing files, which can
            cause a different file to be overwritten if you run this with
            filenames differing only in case.

            We copy instead of creating a symlink so that files modified in
            the emulator can be compared with the originals.
        '''
        dest = Path(dir, src.name.upper())
        vprint(1, 'RunCPM', f'{str(dest):>16} ← {path.pretty(src)}')
        copyfile(src, self.emudir.joinpath(dest))

    def copycpmzip(self, src:Path, dir:Path, subdir:str=''):
        ''' Copy all files from the ZIP file `src` to the `dir` directory
            under `self.emudir`. This upper-cases the filenames in
            the same way that `copycpmfile` does.

            If `subdir` is given, only files underneath that directory in
            the ZIP file will be extracted, and that directory prefix will
            be removed from the extracted file. (Note that this is a `str`,
            not a `Path`, and you must include a trailing slash.)
        '''
        if subdir.startswith('/'): subdir = subdir[1:]
        assert subdir.endswith('/')
        vprint(1, 'RunCPM', f'{str(dir):>15}/ ← {path.pretty(src)}')
        with ZipFile(src) as zf:
            for entry in zf.infolist():
                if len(entry.filename) <= len(subdir): continue
                if not entry.filename.startswith(subdir): continue
                exfname = entry.filename[len(subdir):]
                vprint(2, 'RunCPM', f'extracting [{subdir}]{exfname}')
                with open(self.emudir.joinpath(dir, exfname), 'wb') as f:
                    f.write(zf.read(entry))

