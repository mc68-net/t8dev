''' t8t: Serial transfer and terminal support
'''

from    t8dev  import path
from    t8dev.cli  import exits

import  serial                  # https://pythonhosted.org/pyserial/
from    serial  import Serial, SerialException
from    serial.tools.list_ports  import comports
import  serial.tools.miniterm as miniterm

from    pathlib  import Path
from    functools  import partial
from    time  import sleep
import  os, sys
import  termios
import  argparse
import  toml

####################################################################
#   Main and argument parsing.

PROG = Path(sys.argv[0]).name

def main():
    args = parseargs()
    conf = Config(args.board, args)
    exit(args.func(conf))

def parseargs(args=None):
    parser = argparse.ArgumentParser(
        description='t8t serial transfer/terminal program')
    am = parser.add_argument            # main args

    am('-d', '--device',
        help='Device to use for connection, e.g., `/dev/ttyUSB0`')
    am('-b', '--baud', type=int, help='baud rate')
    am('-c', '--charbits', metavar='C', type=int,
        help='bits per character (5-8)')
    am('-p', '--parity', choices=('N', 'E', 'O', '0', '1'),
        help='parity: N=none, E=even, O=odd, 0=mark, 1=space')
    am('board', help='name of board to connect')
    subparsers = parser.add_subparsers(title='subcommands', required=True)

    p_send = subparsers.add_parser('send', help='send a file to the board')
    p_send.set_defaults(func=cmd_send)
    formats = ('cr', 'lf', 'crlf')
    an = p_send.add_argument       # `as` is a keyword
    an('-f', '--send-format', metavar='FMT', choices=SEND_FORMATS.keys(),
        help='format for sending data; use `?` to list formats')
    an('-l', '--line-delay', metavar='M', type=int,
        help='delay M milliseconds after sending each line or record')
    an('-c', '--char-delay', metavar='M', type=int,
        help='delay M milliseconds after sending each character')
    an('file', nargs='?', help='file to send (stdin if not specified)')

    p_term = subparsers.add_parser('term',
        help='start a terminal connected to the board')
    p_term.set_defaults(func=cmd_term)
    at = p_term.add_argument

    p_params = subparsers.add_parser('params',
        help='show configuration for the given board')
    p_params.set_defaults(func=cmd_params)

    p_list = subparsers.add_parser('list', help='list known boards')
    p_list.set_defaults(func=cmd_list)

    p_devices = subparsers.add_parser('devices',
        help='list local serial devices')
    p_devices.set_defaults(func=cmd_devices)

    p_pyserial = subparsers.add_parser('pyserial',
        help='show pyserial information')
    p_pyserial.set_defaults(func=cmd_pyserial, help=argparse.SUPPRESS)

    return parser.parse_args(args)

####################################################################
#   Commands.

def cmd_pyserial(_conf):
    print(f'pySerial version {serial.VERSION}')
    print(f'BAUDRATES: {Serial.BAUDRATES}')
    print(f'BYTESIZES: {Serial.BYTESIZES}')
    print(f' PARITIES: {Serial.PARITIES}')
    print(f' STOPBITS: {Serial.STOPBITS}')
    return 0

def cmd_devices(_conf):
    #   https://pythonhosted.org/pyserial/tools.html#module-serial.tools.list_ports
    for p in sorted(comports(include_links=True)):
        print(f'{p.name} ({p.device}):')
        print(f'  desc: {p.description}')
        print(f'  hwid: {p.hwid}')
        if p.vid is not None:
            vendor_string = f'vendor={p.vid:04X} ({p.manufacturer})'
            product_string = f'product={p.pid:04X} ({p.product})'
            print(f'   USB:', vendor_string, product_string)
        print()
        #   `p.interface` doesn't seem useful.
    return 0

def cmd_list(conf):
    print(', '.join(sorted(conf.boards())))
    return 0

def cmd_params(conf):
    sources = []
    if conf.local: sources.append('local')
    if conf.user: sources.append('user')

    print(f'Board: {conf.board}  ({", ".join(sources)})')
    for p in conf.PARAMS:
        value, sourcename = conf.getparam(p)
        print(f'  {"("+sourcename+")":>10}  {p+":":12} {value!s}')
    return 0

def cmd_term(conf):
    if os.name != 'posix':
        exits.err(f'{PROG}: term is supported only on POSIX systems')
    try:
        #   XXX Consider serial.serial_for_url()?
        ser = conf.serial()
        #   XXX set up DTR/RTS stuff here, like Miniterm main()?
        ser.open()
        filters = ['direct']
       #filters = ['debug']
        mt = miniterm.Miniterm(ser, echo=False,
            eol='lf',   # CR is passed straight through w/PosixRawConsole
            filters=filters)
        mt.console = PosixRawConsole()
        mt.raw = True
        #   This seems to be a bug fixed in an unreleased version of
        #   pyserial: `self.raw` applies to received characters, but not to
        #   transmitted ones.
        mt.set_tx_encoding('ISO-8859-1')  # transparent encoding
        mt.start()
        #   Wait for threads to terminate. Miniterm main() itself does
        #   this in a more sophisticated way; not sure if we need that.
        mt.join()
    except SerialException as ex:
        exits.err(f'{PROG}: {ex.strerror}')
    return 0

####################################################################
#   Send command

def cmd_send(conf):
    if '?' == conf.args.send_format:
        send_formats(conf)
        return 0

    #   We must (re-) check the format here because while the command line
    #   argument is checked, the config file argument (if that's used instead)
    #   is not.
    format, _ = conf.getparam('send_format')
    if format is None:
        exits.err(f'{PROG}: send_format must be specfied', exitcode=2)
    send_func, _ = SEND_FORMATS.get(format, (None, None))
    if send_func is None:
        exits.err(f'{PROG}: bad send_format: {format}', exitcode=2)

    if conf.args.file is None:  fp = sys.stdin.buffer
    else:                       fp = send_openfile(conf)
    ser = conf.serial()
    ser.open()
    return send_func(conf, fp, ser)

def send_openfile(conf):
    ''' Find and open in binary mode `conf.args.file`. If it exists as
        an absolute or relative path, it will be opened as-is, otherwise
        a search in the board binary path, based on the board's `srcdir`,
        will be done.
    '''
    #   XXX does not yet search based on `srcdir`.
    filename = conf.args.file
    try:
        return open(filename, 'rb')
    except OSError as ex:
        exits.err(f'{PROG}: {ex.strerror}: {path.pretty(filename)!r}')

def send_formats(conf):
    print('Send formats:')
    for name, fnhelp in SEND_FORMATS.items():
        print(f' {name:>8}  {fnhelp[1]}')

def send_fmt_bin(conf, fp, ser):
    line_delay, _ = conf.getparam('line_delay')
    if line_delay != 0:
        exits.warn(
            f'{PROG}: line_delay={line_delay} not valid in bin mode: ignored')
    char_delay, _ = conf.getparam('char_delay')
    char_delay /= 1000      # param vals in milliseconds

    while True:
        c = fp.read(1)
        if c == b'': break
        ser.write(c)
        sleep(char_delay)
    return 0

def send_fmt_text(lineterm, conf, fp, ser):
    line_delay, _ = conf.getparam('line_delay')
    char_delay, _ = conf.getparam('char_delay')
    line_delay /= 1000; char_delay /= 1000      # param vals in milliseconds
    while True:
        line = fp.readline()
        if line == b'': break   # in bin mode '\n' retained, so empty = EOF
        if char_delay == 0:
            ser.write(line[0:-1])
        else:
            for c in line[0:-1]:
                ser.write(bytes([c]))
                sleep(char_delay)
        ser.write(lineterm)
        sleep(line_delay)
    return 0

def send_fmt_intelhex(conf, fp, ser):
    return 99

SEND_FORMATS = {
    '?':        (None, 'List formats'),
    'bin':      (send_fmt_bin, 'Read file as binary and send as-is'),
    'cr':       (partial(send_fmt_text, b'\r'),
                'Read LF-terminated lines and send wtih CR line terminators'),
    'lf':       (partial(send_fmt_text, b'\n'),
                'Read LF-terminated lines and send wtih LF line terminators'),
    'crlf':     (partial(send_fmt_text, b'\r\n'),
                'Read LF-terminated lines and send wtih CR+LF line terminators'),
    'intel':    (send_fmt_intelhex, 'Intel Hex with CR after each record')
}

####################################################################
#   Configuration

class Config:
    ''' This stores and searches the configuration information for
        a board and, additionally, the full config files.
    '''

    PARAMS = (
        'device',       # local serial port device
        'baud',         # 300, 1200, …, 9600, 19200, …
        'charbits',     # 5, 6, 7, 8
        'parity',       # N, E, O, 0 (mark), 1 (space)
        'send_format',
        'line_delay',   # send command record delay in ms
        'char_delay',   # send command byte delay in ms
    )
    ' Valid parameter names in the order they are generally read/used. '

    PARAM_DEFAULTS = {
        'baud':         9600,
        'charbits':     8,
        'parity':       'N',
        'line_delay':   0,
        'char_delay':   0,
    }
    ' Internal default values for each parameter. '

    def __init__(self, board, args):
        self.board          = board
        self.args           = args
        self.conf_local     = self.readconf(path.build('t8t.conf'))
        self.local          = self.conf_local.get(board, {})
        self.conf_user      = self.readconf(path.proj('t8t.conf'))
        self.user           = self.conf_user.get(board, {})

    def boards(self):
        return (*self.conf_user.keys(), *self.conf_local.keys())

    def getparam(self, param):
        ''' Return a (parameter value, source name) tuple for `board`,
            taking the first value found from the command line parameters,
            the local config, the default config and the internal default
            values. Returns `None` if the parameter is not specified and
            has no internal default value.
        '''
        if param not in self.PARAMS:
            raise KeyError(f'Unknown comm param: {param}')
        sources = (
            ('args',    vars(self.args)),
            ('local',   self.local),
            ('user',    self.user),
            ('default', self.PARAM_DEFAULTS),
        )
        for sourcename, source in sources:
            value = source.get(param, None)
            if value is not None:  return (value, sourcename)
        return (None, 'default')

    @staticmethod
    def readconf(confpath):
        if not confpath.exists():
            return {}           # non-existent file is considered empty
        try:
            return toml.load(confpath)
        except Exception as ex:
            #   This is almost certainly bad input from the user, so we want
            #   a nice error message rather than a stack trace.
            exits.err(f'{PROG}: {path.pretty(confpath)}: {ex!s}',
                exitcode=3)

    def serial(self):
        ''' Return an unopened serial.Serial object initialised with these
            configuration parameters.
        '''
        P = lambda name: self.getparam(name)[0]

        parity = P('parity')
        if   parity == '0':  parity = 'S'   # 0 = space parity
        elif parity == '1':  parity = 'M'   # 1 = mark parity

        exception = None
        try:
            s = Serial(port=None,       # do not open immediately
                baudrate=P('baud'),
                bytesize=P('charbits'),
                parity=parity,
                stopbits=1,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False,
                #  XXX timeouts?
                )
            #   This does not re-open the port because that happens only
            #   when the port is already open and the port is being changed.
            s.port = P('device')
            return s
        except SerialException as ex:
            #   Maybe we need a debug mode that shows the actual exception.
            exits.err(f'{PROG}: {ex.strerror}')

####################################################################

#   XXX Who knows what this subclass does if miniterm.Console is not
#   the POSIX one. But ideally miniterm should be tweaked to have
#   an `--eol raw` mode.
class PosixRawConsole(miniterm.Console):
    ''' This subclass of `miniterm.Console` changes only one thing: it
        disables CR to newline translation on input. This allows the
        console to distinguish between CR and LF inputs, rather than
        treating both as a newline.

        This is a partial fix for miniterm's inability to send both CR and
        LF, as opposed to always sending the `--eol` sequence when either
        is received on the terminal. Setting `--eol=lf` will then send the
        bare CR received when the user types Enter or Ctrl-M, and LF when
        the user types Ctrl-J (or presses the 'Line Feed' key should she be
        lucky enough to have one).

        (This assumes that the Enter key sends CR, as Return did on old
        terminals such as the ADM-3A and VT-100, but that's generally
        what it does on most systems.)

        This almost certainly breaks on non-POSIX systems. If we want it to
        work on Windows, we likely need to do a different version for that
        along the lines of what's done in `serial.tools.miniterm`.

        Issue #804_ suggests fixing this in pyserial itself, if and when
        that appears in a release we can drop this code.

        .. _#804: https://github.com/pyserial/pyserial/issues/804
    '''
    def setup(self):
        super().setup()
        tc = termios.tcgetattr(self.fd)
        #   https://manpages.debian.org/bookworm/manpages-dev/termios.3.en.html
        #   https://docs.python.org/3/library/termios.html#termios.tcgetattr
        #   0=iflag, 1=oflag, 2=cflag, 3=lflag, 4=ispeed, 5=ospeed, 6=cc
        tc[0] = tc[0] & ~termios.ICRNL
        termios.tcsetattr(self.fd, termios.TCSANOW, tc)
