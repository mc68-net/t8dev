' cli.t8dev emulator commands '

from    importlib  import import_module

####################################################################

suitenames = [ 'CSCP', 'Linapple', 'OpenMSX', 'RunCPM', 'VICE', 'VirtualT', ]

__all__ = ['setargs_emulator', 'SUITES'] + suitenames

#   Import all Suites that are to small to deserve their own separate file.
from    t8dev.cli.t8dev.emulator.other  import *
#   Import remaining suites.
for suitename in suitenames:
    if not (suitename in globals()):
        m = import_module(f'{__name__}.{suitename.lower()}')
        globals()[suitename] = getattr(m, suitename)

SUITES = dict([ (name, globals()[name]) for name in suitenames ])

def setargs_emulator(spgroup):
    pemu = spgroup.add_parser('emulator', aliases=['emulate', 'emu', 'em'],
        help='run an emulator')
    suitegroup = pemu.add_subparsers(dest='suite', required=True,
        title='Emulator suites', metavar='', help='')
    for sc in SUITES.values():
        p = suitegroup.add_parser(sc.suitename(), help=sc.suitedesc)
        p.set_defaults(func=run_emulator(sc))
        sc.setargparser(p)

def run_emulator(suiteclass):
    '   XXX This seems a bit of a hack.... '
    def run(args): e = suiteclass(args); return e.run()
    return run

####################################################################
#   Set up list of emulators
