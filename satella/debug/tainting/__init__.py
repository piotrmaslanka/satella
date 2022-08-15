from .environment import TaintingEnvironment
from .tainteds import TaintedObject, taint, access_tainted

__all__ = ['TaintingEnvironment', 'TaintedObject', 'taint', 'access_tainted']
