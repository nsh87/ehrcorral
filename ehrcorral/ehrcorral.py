# -*- coding: utf-8 -*-
"""Contains core classes and functions for defining populations and acting upon
them.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from collections import namedtuple, defaultdict

import numpy as np
from pylev import damerau_levenshtein

try:
    from collections import Counter
except ImportError:
    from backport_collections import Counter
from .compressions import first_letter, dmetaphone
from .measures import record_similarity

# Make unicode compatible with Python 2 and 3
try:
    unicode = unicode
except NameError:
    # Using Python 3
    unicode = str
    basestring = (str, bytes)

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
    'forename_freq_ref',  # Often phonemic compression, but not necessarily
    'mid_forename_freq_ref',  # Same as above
    'birth_surname_freq_ref',  # same as above
    'current_surname_freq_ref',  # Same as above
)


def compress(names, method):
    """Compresses surnames using different phonemic algorithms.

    Args:
        names (list): A list of names, typically surnames
        method (func): A function that performs phonemic compression

    Returns:
        A list of the compressions.
    """
    if not isinstance(names, list):
        ValueError("Expected a list of names, got a {0}.".format(type(names)))
    compressions = []
    raw_compressions = map(method, names)
    # Double metaphone returns a list of tuples, so need to unpack it
    for item in raw_compressions:
        if isinstance(item, (list, tuple)):
            compressions.extend([unicode(sub) for sub in item if sub != ''])
        elif item != '':
            compressions.append(unicode(item))
    return compressions if compressions else ['']


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

        Apartment or unit information, such as "Apt. 201".

    .. py:attribute:: state_province

        State or province.

    .. py:attribute:: postal_code

    .. py:attribute:: country

        Consistent formatting should be used. Do not use USA in one Record
        and United States of America in another.

    .. py:attribute:: sex

        Physiological sex (M or F)

    .. py:attribute:: gender

        The gender the patient identifies with (M or F), e.g. in the case of
        transexualism.

    .. py:attribute:: national_id1

        For example, social security number. This should be the same type of
        number for all patients. Do not use USA social security in one
        Record and with Mexico passport number in another.

    .. py:attribute:: id2

        Can be used as an additional identifying ID number, such as driver's
        license number. Again, define the type of ID number this is for the
        entire sub-population.

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
        return self.__unicode__()

    def save_name_freq_refs(self,
                            record_number,
                            forename_freq_method,
                            surname_freq_method):
        """Compress the forenames and surnames and save the compressions to
        the Record.

        Args:
            record_number (int): An integer to be assigned as initial person
                and accession number.
            forename_freq_method (func): A function that performs some sort of
                compression on a single name.
            surname_freq_method (func): A function that performs some sort of
            compression on a single name.
        """
        profile = self.profile
        compressions = {
            "forename":
                compress([profile.forename], forename_freq_method)[0],
            "mid_forename":
                compress([profile.mid_forename], forename_freq_method)[0],
            "current_surname":
                compress([profile.current_surname], surname_freq_method)[0],
            "birth_surname":
                compress([profile.birth_surname], surname_freq_method)[0]
        }
        meta = [
            record_number,  # Person number, can be changed if match found
            record_number,  # Accession number, unique to this record
            compressions['forename'],  # forename ref for dict
            compressions['mid_forename'],  # mid forename ref for dict
            compressions['birth_surname'],  # birth surname ref for dict
            compressions['current_surname']  # current surname ref for dict
        ]
        self._meta = Meta._make(meta)

    def gen_blocks(self, compression):
        """Generate and set the blocking codes for a given record.

        Blocking codes are comprised of the phonemic compressions of the
        profile surnames combined with the first letter of each forename.
        Generated blocking codes are stored in self._blocks, and only contain
        the unique set of blocking codes.

        Args:
            compression (func): A function that performs phonemic
                compression.
        """
        blocks = []
        profile = self.profile
        surnames = [profile.current_surname, profile.birth_surname]
        surnames = [surname for surname in surnames if surname != '']
        bases = compress(surnames, compression)
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
    """A collection of :py:class:`.Record` with methods for interacting with
    and linking records in the herd.

    Attributes:
        similarity_matrix (numpy.ndarray, None): A numpy array containing the
            similarities between :py:class:`.Record` instances, ordered by
            accession number on both axes. Each entry is between 0 and 1 with 1
            being perfect similarity.
    """
    def __init__(self):
        self._population = None
        self._block_dict = defaultdict(list)
        self._surname_freq_dict = Counter()
        self._forename_freq_dict = Counter()
        self.similarity_matrix = None

    def __unicode__(self):
        population = self._population
        if population is None:
            return str(())
        elif len(population) >= 4:
            return "({0},\n {1}\n ...,\n {2},\n {3})".format(
                population[0],
                population[1],
                population[-2],
                population[-1]
            )
        else:
            return str(population)

    def __str__(self):
        return self.__unicode__()

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

    def corral(self,
               forename_freq_method=first_letter,
               surname_freq_method=dmetaphone,
               blocking_compression=dmetaphone):
        """Perform record matching on all Records in the Herd.

        Args:
            forename_freq_method (func): A function that performs some sort of
                compression. Compression of forename can be different than
                compression of surname. The compression information is used to
                determine weights for certain matching scenarios. For example,
                if forename is compressed to be just the first initial, matching
                a name that begins with the letter 'F' will result in a weight
                equal to the fraction of names that begin with the letter 'F' in
                the entire Herd. The less common names that begin with 'F' are,
                the more significant a match between two same or similar
                forenames that begin with 'F' will be. Defaults to the first
                initial of the forename.
            surname_freq_method (func): A function that performs some sort of
                compression. Defaults to double metaphone.
            blocking_compression (func): Compression method to use when
                blocking. Blocks are created by compressing the surname and then
                appending the first initial of the forename. Defaults to double
                metaphone and then uses the primary compression from that
                compression. By default the first initial of the forenames are
                appended to the surname compressions to generate block codes.
        """
        pop_length = len(self._population)
        self.similarity_matrix = np.zeros((pop_length, pop_length),
                                           dtype=np.float32)
        for i, record in enumerate(self._population):
            try:
                record.gen_blocks(blocking_compression)  # Explode the record
                # Keep count of each fore/surname compression for weighting
            except TypeError:
                exc_type, trace = sys.exc_info()[:2]
                raise TypeError("{0}\nYou must populate the Herd "
                                "first.".format(trace))
            finally:
                # Clear per https://docs.python.org/2/library/sys.html#sys.exc_info
                sys.exc_info()
            record.save_name_freq_refs(i, forename_freq_method,
                                       surname_freq_method)
            self.append_names_freq_counters(record)
            # Keep track of the Record's blocking codes in the Herd
            self.append_block_dict(record)
        for record in self._population:
            self.append_similarity_matrix_row(record)

    def append_block_dict(self, record):
        """Appends the herd's block dictionary with the given Record's
        blocking codes.

        The dictionary keys are block codes. The value of each key is a list
        of references to Records that have that block.

        Args:
            record (:py:class:`.Record`): An object of class
                :py:class:`.Record`
        """
        for block in record._blocks:
            self._block_dict[block].append(record)

    def append_names_freq_counters(self, record):
        """Adds the forename and surname for the given Record to the forename
        and surname counters.

        Args:
            record (:py:class:`.Record`): An object of class
                :py:class:`.Record`
        """
        meta = record._meta
        forenames = [
            meta.forename_freq_ref,
            meta.mid_forename_freq_ref,
        ]
        forenames = [forename for forename in forenames if forename != '']
        surnames = [
            meta.birth_surname_freq_ref,
            meta.current_surname_freq_ref
        ]
        surnames = [surname for surname in surnames if surname != '']
        self._forename_freq_dict.update(forenames)
        self._surname_freq_dict.update(surnames)

    def append_similarity_matrix_row(self, comparison_record):
        row = comparison_record._meta.accession
        for block in comparison_record._blocks:
            for record in self._block_dict[block]:
                col = record._meta.accession
                self.similarity_matrix[row][col] = \
                    record_similarity(self,
                                      comparison_record,
                                      record,
                                      damerau_levenshtein,
                                      damerau_levenshtein)


def gen_record(data):
    """Generate a :py:class:`.Record` which can be used to populate a
    :py:class:`Herd`.

    In addition to extracting the profile information for

    Args:
        data (dict): A dictionary containing at least one of fields in
            :py:data:`PROFILE_FIELDS`.

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

