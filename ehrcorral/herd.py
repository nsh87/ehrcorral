# -*- coding: utf-8 -*-
"""Contains core classes and functions for defining populations and acting upon
them.
"""


class Herd(object):
    """A collection of profiles, each representing an individual electronic
    health record.

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
