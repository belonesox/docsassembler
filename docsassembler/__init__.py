"""
DocStruct
=========

   DocStruct is a Python package for documentation building.  

"""
#
import sys
if sys.version_info[:2] < (3, 5):
    print("Python version 3.5 or later is required." %  sys.version_info[:2])
    sys.exit(-1)
del sys

from .actions        import *
from .docstructenvironment  import *
from .scanners       import *
from .projectdb      import *
from .remarks        import *
from .mydepends      import *
from .lib import *
