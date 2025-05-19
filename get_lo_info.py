"""
This is the one place where you set the path structure of the LO code.
The info is stored in the dict Ldir.

All paths are pathlib.Path objects.

This program is meant to be loaded as a module by Lfun which then adds more
entries to the Ldir dict based on which model run you are working on.

Users should copy this to LO_user/get_lo_info.py, edit as needed, and make it into
their own GitHub repo.
"""
import os
from pathlib import Path

# Define a smart ROMS path that falls back if the primary path doesn't exist
class SmartROMSPath:
    def __init__(self, primary_base, fallback_base):
        self.primary_base = Path(primary_base)
        self.fallback_base = Path(fallback_base)

    def __truediv__(self, subpath):
        primary_path = self.primary_base / subpath
        if primary_path.exists():
            return primary_path
        else:
            fallback_path = self.fallback_base / subpath
            return fallback_path

# defaults that should work on all machines
parent = Path(__file__).absolute().parent.parent
LO = parent / 'LO'
LOo = parent / 'LO_output'
LOu = parent / 'LO_user'
data = parent / 'LO_data'

# This is where the ROMS source code, makefiles, and executables are
roms_code = parent / 'LiveOcean_roms'

# This is a new piece of information, to help with integration of
# Aurora Leeson's new LO_traps repo, 2023.11.03.
traps_name = 'traps00'

# These are places where the ROMS history files are kept
roms_out = parent / 'LO_roms'
roms_out1 = Path('/BLANK')  # default, will be set by host check
roms_out2 = Path('/BLANK')
roms_out3 = Path('/BLANK')
roms_out4 = Path('/BLANK')

# these are for mox and klone, other hyak mackines
remote_user = 'BLANK'
remote_machine = 'BLANK'
remote_dir0 = 'BLANK'
local_user = 'BLANK'

# default for linux machines
which_matlab = '/usr/local/bin/matlab'

HOME = Path.home()
try:
    HOSTNAME = os.environ['HOSTNAME']
except KeyError:
    HOSTNAME = 'BLANK'

# debugging
# print('** from get_lo_info.py **')
# print('HOME = ' + str(HOME))
# print('HOSTNAME = ' + HOSTNAME)

if (str(HOME) == '/home/bobayl') & ('DESKTOP' in HOSTNAME):
    lo_env = 'lb_pc'

elif (str(HOME) == '/home/parker') & ('perigee' in HOSTNAME):
    lo_env = 'pm_perigee'
    roms_out1 = Path('/agdat1/parker/LO_roms')
    roms_out2 = Path('/agdat2/parker/LO_roms')
    roms_out3 = Path('/data1/auroral/LO_roms')
    roms_out4 = Path('/data2/parker/LiveOcean_roms/output')

elif (str(HOME) == '/home/bobayl') & ('apogee' in HOSTNAME):
    lo_env = 'lb_apogee'
    roms_out1 = SmartROMSPath('/dat1/parker/LO_roms', '/dat2/parker/LO_roms')
    roms_out2 = Path('/dat2/parker/LO_roms')

elif (str(HOME) == '/usr/lusers/pmacc'):
    lo_env = 'pm_mox'
    remote_user = 'parker'
    remote_machine = 'apogee.ocean.washington.edu'
    remote_dir0 = '/dat1/parker'
    local_user = 'pmacc'

elif ((str(HOME) == '/mmfs1/home/pmacc') or (str(HOME) == '/mmfs1/home/darrd')):
    lo_env = 'pm_klone'
    remote_user = 'parker'
    remote_machine = 'apogee.ocean.washington.edu'
    remote_dir0 = '/dat1/parker'
    local_user = 'pmacc'

Ldir0 = dict()
Ldir0['lo_env'] = lo_env
Ldir0['parent'] = parent
Ldir0['LO'] = LO
Ldir0['LOo'] = LOo
Ldir0['LOu'] = LOu
Ldir0['data'] = data
Ldir0['roms_code'] = roms_code
Ldir0['roms_out'] = roms_out
Ldir0['roms_out1'] = roms_out1
Ldir0['roms_out2'] = roms_out2
Ldir0['roms_out3'] = roms_out3
Ldir0['roms_out4'] = roms_out4
Ldir0['which_matlab'] = which_matlab
#
Ldir0['remote_user'] = remote_user
Ldir0['remote_machine'] = remote_machine
Ldir0['remote_dir0'] = remote_dir0
Ldir0['local_user'] = local_user
#
Ldir0['traps_name'] = traps_name
