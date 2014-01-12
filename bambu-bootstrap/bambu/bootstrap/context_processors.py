import warnings

warnings.warn('bootstrap.context_processors has been deprecated. Use bootstrap.v2.context_processors instead.')
from bambu.bootstrap.v2.context_processors import *