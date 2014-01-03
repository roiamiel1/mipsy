"""
mipsy.util
    Common classes/functions.

See README.md for usage and general information.
"""


class OpInfo(object):
    """
    Operation template to query against during encoding.
    This is the operation information immediately available upon reference
    to the MIPS reference card.
    """
    def __init__(self, format, opcode, funct):
        self.format = format
        self.opcode = opcode
        self.funct = funct


class ParseInfo(object):
    """
    Template that defines the token interpretation and the function to make those tokens.
    """
    def __init__(self, tokens, tokenizer):
        self.tokens = tokens
        self.tokenizer = tokenizer


class Singleton(type):
    """
    Common singleton pattern utilizing Python's "metaclass" attribute.
    """
    _instances = {}
    def __call__(kls, *args, **kwargs):
        if kls not in kls._instances:
            kls._instances[kls] = super(Singleton, kls).__call__(*args, **kwargs)
        return kls._instances[kls]


class LabelCache(object):
    """
    Stores a cache of labels mapped to their instruction index.
    The cache data is shared across instances.
    """
    __metaclass__ = Singleton

    def __init__(self):
        self.cache = {}

    def query(self, label):
        """
        Returns (hit, index) tuple.
        hit is a boolean, signifying label presence in the cache
        index is an integer, the instruction index for the label entry
        """
        try:
            return True, self.cache[label]
        except KeyError, e:
            return False, 0

    def write(self, label, index):
        """
        Saves a new label, index mapping to the cache.
        Raises a RuntimeError on a conflict.
        """
        if label in self.cache:
            if self.cache[label] != index:
                error_message = 'cache_conflict on label: {} with index: {}\ncache dump: {}'.format(label, index, self.cache)
                raise RuntimeError(error_message)
        else:
            self.cache[label] = index

    def empty(self):
        self.cache.clear()

