#
#
from .pm.main import ProGantt
from .spreadsheet.xl_main import Spreadsheet
from .dataframe.dframe import DataFrame
from .criticalpath.criticalpath import Node
#

#__all__ = "interface"


# constants

__major__ = 0.  # for major interface/format changes
__minor__ = 1  # for minor interface/format changes
__release__ = 0  # for tweaks, bug-fixes, or development

__version__ = '%d.%d.%d' % (__major__, __minor__, __release__)

#__author__ = 'Salvador Vargas-Ortega'
#__license__ = 'MIT'
#__author_email__ = 'svortega@gmail.com'
#__maintainer_email__ = 'fem2ufo_users@googlegroups.com'
#__url__ = 'http://fem2ufo.readthedocs.org'
#__downloadUrl__ = "http://bitbucket.org/svortega/fem2ufo/downloads"

#



