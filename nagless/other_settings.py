"""Import settings from a few other places

These are overlay settings files that add or modify the settings in the main settings.py

"""

import platform

# Settings particular to this host.
# For a host named xyz01.example.com, create a file xyz01_example_com.py
host_name = platform.node().replace('.', '_').replace('-', '_')

try:
    exec "from %s import *" % host_name
except ImportError, e:
    pass

# Last resort (good for dev machines): import settings that aren't in the repo.
try:
    from local import *
except ImportError, e:
    pass

