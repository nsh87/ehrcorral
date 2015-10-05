#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test EHRcorral.

Tests for `ehrcorral` module.
"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest
import json
import os
import random

from ehrcorral.herd import Herd
from faker import Faker

fake = Faker()


def create_population(N, start_date="-99y", end_date="-1y"):
    """Creates a fake population.

    A population consists of N profiles of various individuals, where each
    profile includes at least a name, address, and SSN. Herd generation is not
    100% reproducible, so each new population will essentially be random.

    Args:
        N (int): Number of profiles to create.
        start_date (str): Earliest date to use for birthdate. In the form of
            ``+/-[number of years]y``.
        end_date (str): Latest date to use for birthdate, in the same format
            as ``start_date``.

    Returns:
        tuple: A tuple of dictionaries, each representing an individual profile,
        sorted by profile name.
    """
    profile_fields = ['name', 'address', 'ssn', 'blood_group', 'sex']
    population = [fake.profile(fields=profile_fields) for i in range(N)]
    gender_change = {'M': 'F', 'F': 'M'}
    for i in range(N):
        record = population[i]
        # Birthdate
        birthdate = fake.date_time_between(start_date="-99y", end_date="-1y")
        record['birthdate'] = birthdate.strftime("%Y-%m-%d")
        # Gender
        sex = record['sex']
        record['gender'] = gender_change[sex] if random.random() < 0.05 else sex
    return tuple(sorted(population, key=lambda profile: profile['name']))


class TestHerdStr(unittest.TestCase):

    def setUp(self):
        data_path = os.path.join(os.path.dirname(__file__), 'profiles_100.json')
        with open(data_path, 'r') as data_file:
            self.population = tuple(json.load(data_file))

    def test_herd_str(self):
        try:
            herd = Herd()
            str(herd)
        except Exception as e:
            self.fail("Getting string of empty herd raised: {}.".format(e))
        try:
            herd = Herd(self.population)
            str(herd)
        except Exception as e:
            self.fail("Getting string herd raised: {}.".format(e))


class TestHerdPopulation(unittest.TestCase):

    def setUp(self):
        data_path = os.path.join(os.path.dirname(__file__), 'profiles_100.json')
        with open(data_path, 'r') as data_file:
            self.population = tuple(json.load(data_file))

    def test_population_loaded_correctly(self):
        expected_first_profile = {
            'name': 'Aden Reichel',
            'ssn': '317-38-3203',
            'birthdate': '1917-08-30',
            'address': '59654 Wolff Branch Apt. 970\n'
                       'North Fritztown, VT 46589-9935'
        }
        self.assertEqual(self.population[0], expected_first_profile)
        population_len = len(self.population)
        names = [self.population[i]['name'] for i in range(population_len)]
        self.assertIn('Dr. Duard Weissnat', names)
        self.assertEqual(len(self.population), 100)

    def test_herd_class_catches_invalid_profile_on_instantiation(self):
        with self.assertRaises(ValueError):
            Herd(('test', 'test'))  # Tuple of strings
        with self.assertRaises(ValueError):
            Herd((('test',), ('test',)))  # Tuple of tuples
        with self.assertRaises(ValueError):
            Herd((0, 1))  # Tuple of ints
        with self.assertRaises(ValueError):
            Herd(([0], [1]))  # Tuple of lists
        with self.assertRaises(ValueError):
            Herd(([0], {'test': 'test'}))  # Mixed list 1
        with self.assertRaises(ValueError):
            Herd(([0], True))  # Mixed list 2
        with self.assertRaises(ValueError):
            Herd(([0], None))  # Mixed list 3

    def test_herd_class_catches_invalid_population_on_instantiation(self):
        with self.assertRaises(ValueError):
            Herd('test')  # String
        with self.assertRaises(ValueError):
            Herd(['test'])  # List
        with self.assertRaises(ValueError):
            Herd(0)  # Int
        with self.assertRaises(ValueError):
            Herd({'test': 'test'})  # Dict

    def test_herd_class_allows_valid_population_on_instantiation(self):
        try:
            herd = Herd(self.population)
        except Exception as e:
            self.fail("Populating the herd raised: {}.".format(e))
        self.assertEqual(herd.population, self.population)

    def test_instantiate_herd_class_with_no_population(self):
        try:
            herd = Herd()
        except Exception as e:
            self.fail("Creating herd with no population raised: {}.".format(e))
        self.assertEqual(len(herd.population), 0)

    def test_herd_class_catches_invalid_population_after_instantiation(self):
        herd = Herd()
        with self.assertRaises(ValueError):
            herd.population = 'test'  # String
        with self.assertRaises(ValueError):
            herd.population = ['test']  # List
        with self.assertRaises(ValueError):
            herd.population = 0  # Int
        with self.assertRaises(ValueError):
            herd.population = {'test': 'test'}  # Dict

    def test_herd_class_catches_invalid_profile_after_instantiation(self):
        herd = Herd()
        with self.assertRaises(ValueError):
            herd.population = ('test', 'test')  # Tuple of strings
        with self.assertRaises(ValueError):
            herd.population = (('test',), ('test',))  # Tuple of tuples
        with self.assertRaises(ValueError):
            herd.population = (0, 1)  # Tuple of ints
        with self.assertRaises(ValueError):
            herd.population = ([0], [1])  # Tuple of lists
        with self.assertRaises(ValueError):
            herd.population = ([0], {'test': 'test'})  # Mixed list 1
        with self.assertRaises(ValueError):
            herd.population = ([0], True)  # Mixed list 2
        with self.assertRaises(ValueError):
            herd.population = ([0], None)  # Mixed list 3

    def test_herd_class_allows_valid_population_after_instantiation(self):
        herd = Herd()
        try:
            herd.population = self.population
        except Exception as e:
            self.fail("Populating the herd raised: {}.".format(e))
        self.assertEqual(herd.population, self.population)

    def tearDown(self):
        pass
