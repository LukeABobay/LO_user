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

# Define a smart path wrapper that falls back from /dat1 to /dat2
class SmartROMSPath:
    def __init__(self, primary_base, fallback_base):
        self.primary_base = Path(primary_base)
        self.fallback_base = Path(fallback_base)

    def resolve_path(self, subpath):
        """Returns full path from primary or fallback base, depending on existence."""
        primary_path = self.primary_base / subpath
        if primary_path.exists():
            return primary_path
        fallback_path = self.fallback_base / subpath
        return fallback_path

    def __truediv__(self, other):
        # Enable chaining of paths while preserving fallback logic
        return SmartROMSSubPath(self, Path(other))

    def __str__(self):
        return str(self.primary_base)

class SmartROMSSubPath:
    def __init__(self, smart_base, subpath):
        self.smart_base = smart_base  # SmartROMSPath instance
        self.subpath = subpath        # Path relative to base

    def __truediv__(self, other):
        return SmartROMSSubPath(self.smart_base, self.subpath / other)

    def __fspath__(self):
        return str(self.smart_base.resolve_path(self.subpath))

    def __str__(self):
        return str(self.smart_base.resolve_path(self.subpath))

    def __repr__(self):
        return f"SmartROMSSubPath({self.smart_base.resolve_path(self.subpath)})"

    def exists(self):
        return self.smart_base.resolve_path(self.subpath).exists()

    def glob(self, pattern):
        return list(self.smart_base.resolve_path(self.subpath).glob(pattern))

    def is_dir(self):
        return self.smart_base.resolve_path(self.subpath).is_dir()

    def is_file(self):
        return self.smart_base.resolve_path(self.subpath).is_file()

    def open(self, *args, **kwargs):
        return self.smart_base.resolve_path(self.subpath).open(*args, **kwargs)


# -------------------------------------------------------------------

# defaults that should work on all machines
parent = Path(__file__).absolute().parent.parent
LO = parent / 'LO'
LOo = parent / 'LO_output'
LOu = parent / 'LO_user'
data = parent / 'LO_data'

# This is where the ROMS source code, makefiles, and executables are
roms_code = parent / 'LiveOcean_roms'

# Integration support for LO_traps
traps_name = 'traps00'

# Default values for roms_out paths
roms_out = parent / 'LO_roms'
roms_out1 = Path('/BLANK')
roms_out2 = Path('/BLANK')
roms_out3 = Path('/BLANK')
roms_out4 = Path('/BLANK')

# These are for mox and klone (Hyak)
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

# Environment-specific configuration
if (str(HOME) == '/home/bobayl') and ('DESKTOP' in HOSTNAME):
    lo_env = 'lb_pc'

elif (str(HOME) == '/home/parker') and ('perigee' in HOSTNAME):
    lo_env = 'pm_perigee'
    roms_out1 = Path('/agdat1/parker/LO_roms')
    roms_out2 = Path('/agdat2/parker/LO_roms')
    roms_out3 = Path('/data1/auroral/LO_roms')
    roms_out4 = Path('/data2/parker/LiveOcean_roms/output')

elif (str(HOME) == '/home/bobayl') and ('apogee' in HOSTNAME):
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

# Final dictionary
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
Ldir0['remote_user'] = remote_user
Ldir0['remote_machine'] = remote_machine
Ldir0['remote_dir0'] = remote_dir0
Ldir0['local_user'] = local_user
Ldir0['traps_name'] = traps_name
