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
from ehrcorral.herd import gen_record
from ehrcorral.herd import compress
from faker import Faker

fake = Faker()


class TestHerdStr(unittest.TestCase):

    def setUp(self):
        data_path = os.path.join(os.path.dirname(__file__), 'profiles_100.json')
        with open(data_path, 'r') as data_file:
            self.population = tuple(json.load(data_file))

    def test_herd_str_method(self):
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


class TestPhonemicCompression(unittest.TestCase):

    def setUp(self):
        self.name = ['Jellyfish']
        self.names = ['Jellyfish', 'Exeter']

    def test_soundex_compression(self):
        single_compression = compress(self.name, 'soundex')
        self.assertEqual(single_compression, ['J412'])
        multiple_compressions = compress(self.names, 'soundex')
        self.assertEqual(multiple_compressions, ['J412', 'E236'])

    def test_nysiis_compression(self):
        single_compression = compress(self.name, 'nysiis')
        self.assertEqual(single_compression, ['JALYF'])
        multiple_compressions = compress(self.names, 'nysiis')
        self.assertEqual(multiple_compressions, ['JALYF', 'EXATAR'])

    def test_metaphone_compression(self):
        single_compression = compress(self.name, 'metaphone')
        self.assertEqual(single_compression, ['JLFX'])
        multiple_compressions = compress(self.names, 'metaphone')
        self.assertEqual(multiple_compressions, ['JLFX', 'EKSTR'])

    def test_dmetaphone_compression(self):
        single_compression = compress(self.name, 'dmetaphone')
        self.assertEqual(single_compression, ['JLFX', 'ALFX'])
        multiple_compressions = compress(self.names, 'dmetaphone')
        self.assertEqual(multiple_compressions, ['JLFX', 'ALFX', 'AKSTR'])

    def tearDown(self):
        pass

class TestPhonemicBlocking(unittest.TestCase):

    def setUp(self):
        # Female profile with different birth surname and current surname
        female = {
            'forename': 'Adelyn',
            'mid_forename': 'Heidenreich',
            'current_surname': 'Bartell',
            'birth_surname': 'Gerlach'
        }
        self.female_record = gen_record(female)
        # Male profile with some missing name fields
        male = {
            'forename': 'Oliver',
            'current_surname': 'Nader'
        }
        self.male_record = gen_record(male)

    def test_multiple_surnames_and_forenames(self):
        self.female_record.gen_blocks('dmetaphone')
        expected_blocks = ['PRTLA', 'KRLKA', 'JRLKA', 'PRTLH', 'KRLKH', 'JRLKH']
        self.assertItemsEqual(self.female_record._blocks, expected_blocks)

    def test_single_forename_and_surname(self):
        self.male_record.gen_blocks('dmetaphone')
        expected_blocks = ['NTRO']
        self.assertItemsEqual(self.male_record._blocks, expected_blocks)

    def tearDown(self):
        pass