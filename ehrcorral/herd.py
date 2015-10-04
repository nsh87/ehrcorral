"""Base class for a herd - a group of records"""


class Herd():
    """You need:
    - validate names (check for commas, weird chars, convert to unicode/ascii?)
        * remove Mrs, PhD, Ms., etc.
        * check for commas, weird chars
        * convert to unicode/ascii?
    - validate that you only have certain field names in the incoming dict
    - parse names into first, last, prefix, suffix
    """
    pass
