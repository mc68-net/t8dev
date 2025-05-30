''' analyze-cmt - analysis of attempts to read CMT audio files
 
    This has various options that attempt different interprations and analyses
    of CMT data at the various levels up to bytes: pulse widths/baud rates,
    mark/space, the bitstream, and then byte framing.
'''

from    argparse import ArgumentParser
from    functools import partial
from    itertools import chain
import  math
import  statistics
import  sys
import  wave

from    cmtconv.analyze import *
import  cmtconv.audio as au, cmtconv.logging as lg

parseint = partial(int, base=0)     # Parse an int recognizing 0xNN etc.

def parse_args():
    p = ArgumentParser(description='''
            Analyse tape format audio''',
        epilog='''
        ''')
    a = p.add_argument
    a('-r', '--report-bauds', action='store_true' ) # count cycles per well-known baud rates
    a(      '--baud', type=float, default=1200)
    a('-g', '--gradient-factor',type=float, default=0.5)
    a('-t', '--tolerance',type=float, default=0.25)
    a('-d', '--dump-pulses', action='store_true')
    a('-l', '--pulse-length-stats', action='store_true')
    a('-b', '--bitstream', type=str, help=\
        "BITSTREAM='line' for one symbol per line; "
        "'char' for just the 0/1 symbols on one line")
    a('-B', '--bytes', action='store_true')
    a('-m', '--mark-baud', type=int, default=2400)
    a('--mark-pulses', type=int, default=2, help=\
        'number of mark-baud pulses for a single mark bit')
    a('-s', '--space-baud', type=int, default=1200)
    a('--space-pulses', type=int, default=2, help=\
        'number of space-baud pulses for a single space bit')
    a('--start', default='m')
    a('--stop', default='ss')
    a('--reverse-bits', action='store_true', help=\
        'decode LSB first rather than MSB first')
    a('--invert-bits', action='store_true')
    a('-p', '--to-pulses', action='store_true')
    a('-P', '--from-pulses', action='store_true')
    a('-w','--save-wav', action='store_true')
    a('-v', '--verbose', action='count', default=0)

    a('input', help="input file ('-' for stdin)")
    a('output', help="output file ('-' for stdout)")

    args = p.parse_args()
    lg.set_verbosity(args.verbose)

    if args.input == '-':               args.input = sys.stdin.buffer
    else:                               args.input = open(args.input, 'br')
    if args.output == '-':              args.output = sys.stdout.buffer
    elif args.output is not None:       args.output = open(args.output, 'bw')

    def to_mark_space(s):
        res = tuple()
        for c in s:
            if c == 'm': res += (1,)
            elif c == 's': res += (0,)
            else: raise ValueError('Start/stop bit must be \'m\' or \'s\'')
        return res

    # FIXME: tolerance
    tol =  args.tolerance
    args.pulse_decoder = au.PulseDecoder(args.mark_baud, args.mark_pulses,
        args.space_baud, args.space_pulses,
        args.invert_bits, args.reverse_bits,
        to_mark_space(args.start), to_mark_space(args.stop),
        (tol, tol), (tol, tol))

    args.pulse_encoder = au.Encoder(
        args.mark_baud, args.mark_pulses,
        args.space_baud, args.space_pulses,
        args.invert_bits, args.reverse_bits,
        to_mark_space(args.start), to_mark_space(args.stop),
        )

    return args

def report_bauds(args, pulses):
    bauds = list(reversed(sorted(
        baud_rates(args.baud) + baud_rates(args.baud * 1.5))))
    tol = args.tolerance
    durs = [ (  b,
                (1.0 + math.log(1.0 - tol)) * 0.5/b,
                (1.0 + math.log(1.0 + tol)) * 0.5/b
            ) for b in bauds ]
    buckets = dict( (b, []) for b in bauds )
    buckets['low'] = []
    buckets['high'] = []
    buckets['unknown'] = []

    # classify each pulse width and add to relevant bucket
    for (_,_, dur) in pulses:
        if dur < durs[0][1]:
            buckets['low'].append(dur)
        elif dur > durs[-1][2]:
            buckets['high'].append(dur)
        else:
            found = False
            for (b,l,h) in durs:
                if dur >= l and dur <= h:
                    buckets[b].append(dur)
                    found = True
                    break
            if not found:
                buckets['unknown'].append(dur)
    # calc stats
    def calc_stats(ws):
        c = len(ws)
        if c > 1:
            return (c, statistics.mean(ws), statistics.stdev(ws))
        elif c > 0:
            return (c, statistics.mean(ws), None)
        else:
            return (c, None, None)

    stats = { k : calc_stats(ws) for k, ws in buckets.items() }

    def width(baud):
        try:
            return "{:4.2f}us".format(1e6 * (0.5 / float(baud)))
        except:
            return "-"

    # Report
    print("{:>16} {:>8} {:>13} {:>13}".format("Width us / Baud", "Count", "Mean us", "Stdev us"))
    for baud in chain([ 'low' ], reversed(bauds), ['high', 'unknown']):
        (c, m, s) = stats[baud]
        if m is None:   m_ = ""
        else:           m_ = "{:>6.3f}".format(1e6 * m)
        if s is None:   s_ = ""
        else:           s_ = "{:>6.3f}".format(1e6 * s)
        baud_ = "{} /{:>5}".format(width(baud), baud)
        print("{:>16} {:>8} {:>13} {:>13}".format(baud_, c, m_, s_))


# FIXME: add leader detection that works
# for formats that use repeating mark or space instead of
# an actual pattern of bytes

def dump_pulses(args, pulses):
    pd = args.pulse_decoder
    idx = None
    i = 0
    for e in pulses:
        if pd.classify_pulse(e) in [au.PULSE_MARK, au.PULSE_SPACE]:
            idx = i
            break
        i += 1
    if idx is None:
        return
    # start dumping them
    while idx < len(pulses):
        e = pulses[idx]
        c = pd.classify_pulse(pulses[idx])
        p = 'X'
        if c == au.PULSE_MARK: p = 'M'
        elif c == au.PULSE_SPACE: p ='S'
        print('{:012.6f}, {}, {:09.3f}, {}'.format(e[0], p, 1e6 * e[2], e[1]))
        idx += 1


def dump_pulse_length_stats(args, pulses):
    # Create histogram for run lengths
    buckets = dict( (i, 0) for i in range(0,33) )
    buckets['>'] = 0

    b = args.baud
    tol = args.tolerance
    low = (1.0 + math.log(1.0 - tol)) * 0.5/b
    high = (1.0 + math.log(1.0 + tol)) * 0.5/b
    idx = 0
    n = len(pulses)
    while idx < n:
        dur = pulses[idx][2]
        if dur >= low and dur <= high:
            c = 0
            while idx < n and dur >= low and dur <= high:
                c += 1
                idx += 1
                if idx < n:
                    dur = pulses[idx][2]
            if c > 32:
                buckets['>'] += 1
            else:
                buckets[c] += 1
        else:
            idx += 1

    # Report
    print('Run lengths for baud {}'.format(b))
    print('{:>12} {:>8}'.format('Run Length', 'Count'))
    for l in chain(range(0,33), '>'):
        c = buckets[l]
        print('{:>12} {:>8}'.format(l, c))

def dump_bitstream(args, pulses):
    valid = ('line', 'char')
    if args.bitstream not in valid:
        raise ValueError("bitstream must be in {}".format(valid))
    pd = args.pulse_decoder
    # read until mark/space
    idx = None
    i = 0
    for e in pulses:
        if pd.classify_pulse(e) in [au.PULSE_MARK, au.PULSE_SPACE]:
            idx = i
            break
        i += 1
    if idx is None:
        return
    # start dumping them
    while idx < len(pulses):
        e = pulses[idx]
        c = pd.classify_pulse(pulses[idx])
        if args.bitstream == 'char':
            if c == au.PULSE_MARK:      print('1', end='')
            elif c == au.PULSE_SPACE:   print('0',end='')
            else:                       print('x',end='')
        else:
            if c == au.PULSE_MARK:
                print('{}, {:012.6f}, 1, {:09.3f}, {}'
                      .format(idx, e[0], 1e6 * e[2], e[1]))
            elif c == au.PULSE_SPACE:
                print('{}, {:012.6f}, 0, {:09.3f}, {}'
                      .format(idx, e[0], 1e6 * e[2], e[1]))
            else:
                print('{}, {:012.6f}, X, {:09.3f}, {}'
                      .format(idx, e[0], 1e6 * e[2], e[1]))
        if c == au.PULSE_MARK:          idx += args.mark_pulses
        elif c == au.PULSE_SPACE:       idx += args.space_pulses
        else:                           idx += 1
    print()

def dump_bytes(args, pulses):
    pd = args.pulse_decoder
    # FIXME add mark/space only leader
    # Find start bit patterm
    (idx, _) = pd.next_mark(pulses, 0)
    #lg.v3('Mark at {}', pulses[idx][0])
    print('Mark at {} - {}'.format(idx, pulses[idx][0]))

    idx = pd.next_space(pulses, idx, 1)
    print('Space at {} - {}'.format(idx, pulses[idx][0]))

    print('Searching from {} - {}'.format(idx, pulses[idx][0]))

    # Attempt to read a byte and keep trying until we get a byte
    byte_read = False
    while not byte_read and idx < len(pulses):
        try:
            i = idx
            (idx, b) = pd.read_byte(pulses, idx)
            byte_read = True
            print('Byte read at {} - {}: {:02x}'.format(i, pulses[i][0], b))
        except Exception as ex:
            idx += 1
    c = '.' if b<32 or b>127 else chr(b)
    print('{} {:012.6f}, {:02x}, {}'.format(idx, pulses[idx][0], b, c))
    # Keep reading bytes until we can't
    err = 0
    while idx < len(pulses):
        try:
            (idx, b) = pd.read_byte(pulses, idx)
            if err > 0:
                print(
                    '{} - {:012.6f}, failed to read byte for previous {} pulses'.format(idx, pulses[idx][0], err))
                err=0
            c = '.' if b<32 or b>127 else chr(b)
            print('{}, {:012.6f}, {:02x}, {}'.format(idx, pulses[idx][0], b, c))
        except Exception as ex:
            err += 1
            idx += 1
    return None

# def convert_to_pulses(args, pulses):

# def convert_from_pulses():

# save pulses
def save_pulses(args, pulses, sample_dur):
    tau = 1.0 / 44100.0
    for e in pulses:
        lvl = 0x00
        if e[1] > 0: lvl = 0x01
        elif e[1] < 0: lvl = 0xff
        q = int(e[2] / tau)
        q0 = (q // 256 // 256) % 256
        q1 = (q // 256) % 256
        q2 = q % 256
        args.output.write(bytearray( (lvl, q0, q1, q2)))

# load pulses
def load_pulses(args):
    tau = 1.0 / 44100.0
    i = 0
    pulses = []
    bs = None
    while bs is None or len(bs) != 0:
        bs = args.input.read(4)
        if len(bs) == 0: break
        lvl = 0
        if bs[0] == 0xff: lvl = -1
        elif bs[1] == 0x01: lvl = 1
        q = 256 * 256 * bs[1]
        q += 256 * bs[2]
        q += bs[3]
        pulses.append( (i * tau, lvl, q * tau ) )
        i =+ q
    return pulses

# save wav from pulses
def save_wav(args, pulses, sample_dur):
    #pulse_widths = [ e[2] for e in pulses ]
    pulses_ = [ (e[2], e[1]) for e in pulses ]
    amp = 64
    mid = 128
    samples = au.pulses_to_samples2( (au.sound(pulses_),) , sample_dur,
        mid-amp, mid, mid+amp)
    w = wave.open(args.output,'wb')
    w.setnchannels(1)
    w.setsampwidth(1)
    w.setframerate(44100)
    w.writeframes(bytes(samples))

def main():
    args = parse_args()
    print(args)
    if args.from_pulses:
        pulses = load_pulses(args)
        sample_dur = 1.0 / 44100.0
    else:
        w = wave.open(args.input, 'rb')
        if w.getnchannels() != 1 or w.getsampwidth() != 1:
            raise ValueError('Only mono 8-bit wav files are supported')
        rate = w.getframerate()
        n_samples = w.getnframes()
        samples = w.readframes(n_samples)
        sample_dur = 1.0 / rate
        #pulses = au.samples_to_pulses(samples, sample_dur)
        pulses = au.samples_to_pulses_via_edge_detection(
            samples, sample_dur, args.gradient_factor)
        pulses = au.filter_clicks(pulses, sample_dur)
        if args.to_pulses:
            save_pulses(args, pulses, sample_dur)
    if args.report_bauds:
        report_bauds(args, pulses)
    if args.dump_pulses:
        dump_pulses(args, pulses)
    if args.pulse_length_stats:
        dump_pulse_length_stats(args, pulses)
    if args.bitstream:
        dump_bitstream(args, pulses)
    if args.bytes:
        dump_bytes(args, pulses)
    if args.save_wav:
        save_wav(args, pulses, sample_dur)
