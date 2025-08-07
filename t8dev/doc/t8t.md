t8t: Serial transfers and terminals
===================================

The `t8t` program does serial uploads, downloads and terminal connections
to various _boards,_ which may be SBCs, vintage computers and other devices
with a serial port. Default communications settings are saved under a board
name in configuration files; connections settings may also be specified
at the command line in which case any arbitrary board name can be used.

Some basic communications parameters such as baud rate also have internal
defaults if they are not specified in configuration or at the command line;
others, such as the local serial device to use for the connection, have no
default and must be specified.


Command-line Usage
------------------

Any parameters not specified at the command line will take default values
from the configuration files (see below) or use internal defaults, where
available. (Note that the `device` parameter has no default.) You can see
the exact parameters used for any particular board (including those passed
on the command line) with the `params` subcommand.

Basic command line usage is

    t8t [OPTION …] BOARD SUBCOMMAND [OPTION …] [ARGS]

Use `--help` or `-h` on the command line to get help. Giving `-h` before
the subcommand will print help for options common to all subcommands and
a list of the subcommands. Giving `-h` after a subcommand will print
help for that particular subcommand, including options specific to it.

Common options must always be given before the _board_ name;
subcommand-specific options must be given after _subcommand._

#### Common Options

These must appear before _subcommand._

- `--verbose`, `-v`: Explain to stdout what is being sent and how.
- `--device DEV`, `-d DEV`: Use _dev_ as the local serial device. This is
  typically a path such as `/dev/ttyUSB0` or `/dev/serial/by-id/…`. (No
  internal default.)
- `--baud N`, `-b N`: Set baud rate to _n._ (Internal default: `9600`).
- `--charbits C`, `-c C`: Set the number of bits per character to _c._ This
  generally must be in the range from 5 through 8. (Internal default: `8`)
- `--parity P`, `-p P`: Add a parity bit (in addition to the number of
  _charbits_) and set it using one of the following methods. (Internal
  default: `N`.)
  - `N`: no parity bit added.
  - `E`: even parity
  - `O`: odd parity
  - `0`: "mark" parity: the parity bit is always set to `0`.
  - `1`: "space" parity: the parity bit is always set to `1`.

### Informational Subcommands

* `devices`: List serial ports connected to the system. The _board_ parameter
  must be supplied, but is ignored and so can be any string (e.g. `-`).

* `list`: List board names defined in the configuration files. The _board_
  parameter must be supplied, but is ignored and so can be any string
  (e.g. `-`).

* `params`: Print out the communications parameters for the given board,
  including any values overridden on the command line. The board name need
  not be in a configuration file, in which case only command line
  parameters and, where not given, defaults will be shown.

  The first line will print the board name and, in parentheses after it,
  which configuration files ('user', 'local'), if any, contain parameter
  definitions. This will be followed by each parameter giving the source
  of the parameter, the name, and the value.

#### Terminal Mode

The `term` subcommand will start a terminal interface to the board. It uses
pyserial's [miniterm], but with a rather specific configuration designed to
make communications as transparent as possible. In particular, `t8t … term`
sends only a CR when you press Enter (or Ctrl-M), and will send an LF if
you press Ctrl-J (which the standard miniterm cannot do).

Otherwise this works just as miniterm. Typing Ctrl-] will exit; typing
Ctrl-T Ctrl-H will show a help menu. You can send a Ctrl-T or Ctrl-] by
preceding it with a Ctrl-T.

If you need some of the miniterm features that this does not support, you
can run miniterm directly with `python -m serial.tools.miniterm`; the `-h`
option will give help on the options.

#### Send Mode

The `send` subcommand will send _file_ to the board over the serial link.
Note that this _never_ reads from the serial link, so it's safe to use when
you have a `term` session running. (The `term` session might swallow output
from the board that `send` would be looking for if it wanted to read board
output.)

The following additional send options (which must be placed _after_ `send`
in the command line) are available:
- `--format FORMAT`, `-f FORMAT`: Use _format_ for data sent with `send`. A
  format parameter of `?` will list the available formats, which are:
  - `cr`: Read a text file; send lines with ASCII carriage return ($0D)
    line terminators.
  - `lf`: Read a text file; send lines with ASCII linefeed ($0A) line
    terminators.
  - `crlf`: Read a text file; send lines with ASCII CR+LF ($0A, $0D) line
    terminators.
  - `intel`: Read an ASL `.p` file; send [Intel HEX] format with ASCII CR
    ($0D) line terminators.
- `--line-delay MS`, `-l MS`: Wait for _ms_ milliseconds after sending each
  record or newline. Ignored with formats that do not send lines or records
  (use sufficient `--char-delay` instead).
- `--char-delay MS`, `-c MS`: Wait for _ms_ milliseconds after sending each
  character.

XXX The following does not work yet.

If the filename does not exist and has no extension, it will be tried again
after adding `.p` (the extension for ASL output files) to the end of the
filename.

Filenames that do not include a slash will, if not found in the current
working directory, be searched for in `$T8_PROJDIR/.build/BOARD/`, where
_board_ is the board name. E.g., if you are using board `kc85/m100` and
type `t8t send hello` it will first search the current working directory
for `hello` and `hello.p` and then search for those files again in
`$T8_PROJDIR/.build/kc85/m100/`.


Configuration Files
-------------------

Configuration files are in [TOML] format, with a section for each board name
containing communications parameters, all of which are optional. For
example:

    #   'kc85/m100' is the TRS-80 Model 100 version of the Kyocera 85 platform.
    #   Programs for this are found in the `exe/kc85/m100` directory.
    #   (That directory need not exist however.)
    ['kc85/m100']
    baud        = 19200
    charbits    = 7         # bits per character, generally 7 or 8
    parity      = 'E'       # parity: N=none, E=even, O=odd
    device      = '/dev/serial/by-id/usb-FTDI_USB__-__Serial-if00-port0'

Two configuration files are used:
- `$T8_PROJDIR/t8t.conf` is the _user_ configuration file; parameters
  from this are used for the given board name, if present and if not
  overridden by the local configuration file and/or command line
  parameters.
- `$T8_PROJDIR/.build/t8tf.conf` is the _local_ configuration file,
  generated by t8t. It is used to save board names and communications
  parameters previously given on the command line.

Command-line parameters always override any configuration files and, if not
present in or changed from the current configuration files, are saved in
the local configuration file.


<!-------------------------------------------------------------------->
[Intel HEX]: https://en.wikipedia.org/wiki/Intel_HEX
[TOML]: https://toml.io/en/v1.0.0
[miniterm]: https://pythonhosted.org/pyserial/tools.html#module-serial.tools.miniterm
