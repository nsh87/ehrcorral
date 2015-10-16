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

    You need:
    - validate names (check for commas, weird chars, convert to unicode/ascii?)
        * remove Mrs, PhD, Ms., etc.
        * check for commas, weird chars
        * convert to unicode/ascii?
    - validate that you only have certain field names in the incoming dict
    - parse names into first, last, prefix, suffix

    need to make separate .csv's for each region
    get male and female names and combine
    only use the No. 1, No. 2, and No. 3 names
    download whatever is in the first <a> (some names will be left out)
    split by / and add to list
    split by , and add to list
    split by ( and remove whatever comes after the opening parenthesis
              then convert everything to ASCII (i.e. need to remove accented
                                                characters, umlaus)

              when you generate a single file, you might make 1000 names and
              make the population of names representative of the population of
              ethnicities in the US. or just compare separately.

              what do you do with names with JR...SR...I...II?

    HAVE ABILITY to grow a herd, which doesn't mean adding to the tuple of
    Records...have it be a way around memory limitations. That means that
    instead of 'appending' to the tuple of Records, it immediately sends
    the data to append to the ES database. It should therefore be that you
    require a connection object in order to create a herd (maybe not).

    """
    def __init__(self):
        self.population = ()
        self._phoneme = 'dmetaphone'

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

    @property
    def phoneme(self):
        """Get the current phoneme."""
        return self._phoneme

    @phoneme.setter
    def phoneme(self, value):
        """Validate and set the phoneme to use for blocking."""
        if value not in PHONEMES:
            raise ValueError("Phoneme must be one of {}.".format(PHONEMES))
        self._phoneme = value

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


