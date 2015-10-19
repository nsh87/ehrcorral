# -*- coding: utf-8 -*-
"""Contains core classes and functions for defining populations and acting upon
them.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
from collections import namedtuple

import jellyfish
import metaphone

PROFILE_FIELDS = (
    'forename',
    'mid_forename',
    'birth_surname',
    'current_surname',
    'suffix',
    'address1',
    'address2',
    'city',
    'state_province',
    'postal_code',
    'country',
    'sex',
    'gender',
    'national_id1',
    'id2',
    'mrn',
    'birth_year',
    'birth_month',
    'birth_day',
    'blood_type',
)
# Use a class and make these class variable so you can document these fields
# in Sphinx. Make sure that when looping through these variables you get them
# in the correct order that you write them. You might need to use a
# namedtuple class. Ideally, every field is its own variable in the class so
# you can add documentation for that individual variable.


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


compression_dispatch = {
    'soundex': jellyfish.soundex,
    'nysiis': jellyfish.nysiis,
    'metaphone': jellyfish.metaphone,
    'dmetaphone': metaphone.doublemetaphone
}


def compress(names, method):
    """Compresses surnames using different phonemic algorithms.

    Args:
        names (list): A list of names, typically surnames
        method (str): A phonemic compression algorithm. Must be one of
            :py:data::PHONEMES.

    Returns:
        A list of the compressions.
    """
    if not isinstance(names, list):
        ValueError("Expected a list of names, got a {}.".format(type(names)))
    compressions = map(compression_dispatch[method], names)
    # Double metaphone returns a list of tuples, so need to unpack it
    if method == 'dmetaphone':
        compressions = [compression for dmetaphone in compressions
                        for compression in dmetaphone if compression != '']
    return compressions


class Profile(namedtuple('Profile', PROFILE_FIELDS)):
    """A selection of patient-identifying information from a single electronic
    health record.

    All fields should be populated with an int or string and will be coerced
    to the proper type for that field automatically.

    .. py:attribute:: forename

        Also known as first name.

    .. py:attribute:: mid_forename

        Also known as middle name.

    .. py:attribute:: birth_surname

        Last name at birth, often same as mother's maiden name.

    .. py:attribute:: current_surname

        Current last name. Can differ from birth surname often in the case of
        marriage for females.

    .. py:attribute:: suffix

        Sr., Junior, II, etc.

    .. py:attribute:: address1

        Street address, such as "100 Main Street".

    .. py:attribute:: address2

        Apartment or unit number.

    .. py:attribute:: state_province

        State or province.

    .. py:attribute:: sex

        Physiological sex (M or F)

    .. py:attribute:: gender

        The gender the patient identifies with (M or F), e.g. in the case of
        transexualism.

    .. py:attribute:: national_id1

        For example, social security number. This should be the same type of
        number for all patients. Do not mix USA social security with Mexico
        passport number.

    .. py:attribute:: id2

        Can be used as an additional identifying ID number, such as driver's
        license number.

    .. py:attribute:: mrn

        Medical record number.

    .. py:attribute:: birth_year

        In the format YYYY.

    .. py:attribute:: birth_month

        In the format MM.

    .. py:attribute:: birth_day

        In the format DD.

    .. py:attribute:: blood_type

        One of A, B, AB, or O with an optional +/- denoting RhD status.
    """
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
        self._blocks = None

    def __unicode__(self):
        if self.profile is None:
            return ''
        else:
            return str(self.profile._asdict())

    def __str__(self):
        return unicode(self).encode('utf-8')

    def gen_blocks(self, blocking_method):
        """Generate and set the blocking codes for a given record.

        Blocking codes are comprised of the phonemic compressions of the
        profile surnames combined with the first letter of each forename.
        Generated blocking codes are stored in self._blocks, and only contain
        the unique set of blocking codes.

        Args:
            blocking_method (str): Which phonemic compression to use for the
                generation of blocks. Must be one of :py:data::PHONEMES.
        """
        blocks = []
        profile = self.profile
        surnames = [profile.current_surname, profile.birth_surname]
        surnames = [surname for surname in surnames if surname != '']
        bases = compress(surnames, blocking_method)
        # Bases are now [PJTR, PHTR] - base phonemic compressions of surnames
        forenames = [profile.forename, profile.mid_forename]
        forenames = [forename for forename in forenames if forename != '']
        # Append 1st letter of each forename to each surname compression
        for base in bases:
            for forename in forenames:
                block = base + forename[0]
                blocks.append(block.upper())
        self._blocks = tuple(set(blocks))


class Herd(object):
    """A collection of :py:class:`.Record`s with methods for interacting with
    and linking records in the herd.
    """
    def __init__(self):
        self._population = None

    def __unicode__(self):
        population = self._population
        if population is None:
            return str(())
        elif len(population) >= 4:
            return "({},\n {}\n ...,\n {},\n {})".format(
                population[0],
                population[1],
                population[-2],
                population[-1]
            )
        else:
            return str(population)

    def __str__(self):
        return unicode(self).encode('utf-8')

    @property
    def size(self):
        """Returns the size of the Herd's population."""
        population = self._population
        if population is None:
            return 0
        else:
            return len(population)

    def populate(self, records):
        """Sets the Herd's sub-population.

        Args:
            records (list, tuple): A list or tuple containing multiple
                :py:class:`.Record`
        """
        if self._population is not None:
            raise AttributeError("The herd is already populated.")
        if not isinstance(records, (tuple, list)):
            raise ValueError("Expected a tuple or list.")
        if isinstance(records, list):
            records = tuple(records)
        self._population = records

    def corral(self, blocking='dmetaphone'):
        if blocking not in PHONEMES:
            raise ValueError("Blocking must be be one of {}.".format(PHONEMES))
        self._explode(blocking)

    def _explode(self, blocking):
        """Generates primary and exploded phonemic blocking codes for each
        Record.

        The primary blocking code uses the current surname and first forename
        and exploded blocking codes use various combinations of birth surname,
        first surname, and middle name.
        """
        try:
            for record in self._population:
                record.gen_blocks(blocking)
        except TypeError:
            exc_type, trace = sys.exc_info()[:2]
            raise TypeError("You must populate the Herd first."), None, trace
        finally:
            # Clear per https://docs.python.org/2/library/sys.html#sys.exc_info
            sys.exc_info()


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
    if len(profile.forename) < 1 or len(profile.current_surname) < 1:
        raise ValueError("A forename and current surname must be supplied.")
    record = Record()
    record.profile = profile
    return record

