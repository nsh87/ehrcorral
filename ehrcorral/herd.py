# -*- coding: utf-8 -*-
"""Contains core classes and functions for defining populations and acting upon
them.
"""


from collections import namedtuple


class Record(namedtuple('Record', ['first_name',
                                   'middle_name',
                                   'last_name',
                                   'suffix',
                                   'gender',
                                   'sex',
                                   'address',
                                   'ssn',
                                   'id_number',
                                   'blood_type',
                                   'birthdate'])):
    """An immutable representation of an electronic health record primarily
    containing identifying patient information.
    """
    __slots__ = ()  # Prevent per-instance dictionaries for low memory


class Herd(object):
    """A collection of :py:class:`.Record` with methods for interacting with
    and linking records in the herd.

    You need:
    - validate names (check for commas, weird chars, convert to unicode/ascii?)
        * remove Mrs, PhD, Ms., etc.
        * check for commas, weird chars
        * convert to unicode/ascii?
    - validate that you only have certain field names in the incoming dict
    - parse names into first, last, prefix, suffix
    """
    def __init__(self, population=None):
        self._population = None  # Declaration for readability
        self.population = () if population is None else population

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

    def __repr__(self):
        return "Herd(population={})".format(str(self))

    @property
    def population(self):
        """Get the current population."""
        return self._population

    @population.setter
    def population(self, value):
        """Validate and set the herd's population."""
        if not isinstance(value, tuple):
            raise ValueError("Expected a tuple.")
        if not all(isinstance(profile, dict) for profile in value):
            raise ValueError("Expected a tuple of dictionaries.")
        self._population = value
