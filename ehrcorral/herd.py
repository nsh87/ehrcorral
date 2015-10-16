# -*- coding: utf-8 -*-
"""Contains core classes and functions for defining populations and acting upon
them.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import namedtuple

PROFILE_FIELDS = (
    'forename',
    'middle_name',
    'present_surname'
    'birth_surname'
    'suffix',
    'address',
    'sex',
    'gender',
    'ssn',
    'birth_year',
    'birth_month',
    'birth_day',
    'blood_type',
)


META_FIELDS = (
    'person',  # Unique to this individual, which can be changed if match found
    'accession',  # Unique number in entire herd to identify this record
)


PHONEMES = (
    'soundex',
    'nysiis',
    'metaphone',
    'dmetaphone',
)


class Profile(namedtuple('Profile', PROFILE_FIELDS)):
    __slots__ = ()  # Prevent per-instance dictionaries to reduce memory


class Meta(namedtuple('Meta', META_FIELDS)):
    __slots__ = ()


class Record(object):
    """A Record contains identifying information about a patient, as well as
    generated phonemic and meta information.
    """
    def __init__(self):
        self.profile = None
        self._meta = None
        self._block = None


class Herd(object):
    """A collection of :py:class:`.Record`s with methods for interacting with
    and linking records in the herd.
    """
    def __init__(self):
        self.population = ()

    def __str__(self):
        population = self.population
        if len(population) > 6:
            return "[\n  {},\n  {},\n  {}\n...,\n  {},\n  {}\n]".format(
                population[0],
                population[1],
                population[2],
                population[-2],
                population[-1]
            )
        else:
            return str(population)

    def populate(self, records):
        """Sets the Herd's sub-population.

        Args:
            records (list, tuple): A list or tuple of :py:class:`._Record`s
        """
        if not isinstance(records, (tuple, list)):
            raise ValueError("Expected a tuple or list.")
        if isinstance(records, list):
            records = tuple(records)
        self.population = records

    def explode(self, blocking='dmetaphone'):
        """Generates primary and exploded phonemic blocking codes for each
        Record.

        The primary blocking code uses the current surname and first forename
        and exploded blocking codes use various combinations of birth surname,
        first surname, and middle name.
        """
        if blocking not in PHONEMES:
            raise ValueError("Blocking method be one of {}.".format(PHONEMES))



def gen_record(data):
    """Generate a :py:class:`.Record` which can be used to populate a
    :py:class:`Herd`.

    In addition to extracting the profile information for

    Args:
        data (dict): A dictionary containing at least one of fields in
            :py:data::PROFILE_FIELDS.

    Returns:
        A object of class :py:class:`.Record`.
    """
    fields = [data.get(field, '') for field in PROFILE_FIELDS]
    profile = Profile._make(fields)
    if profile.forename == '' or profile.present_surname == '':
        raise ValueError("A forename and present_surname must be supplied.")
    record = Record()
    record.profile = profile
    return record


