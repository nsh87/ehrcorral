from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from jellyfish import soundex, nysiis, metaphone
from .metaphone import doublemetaphone as dmetaphone


def first_letter(name):
    """A simple name compression that returns the first letter of the name.

    Args:
        name (str): A forename, surname, or other name.

    Returns:
        (str): The upper case of the first letter of the name
    """
    return name[0].upper() if name else ''
