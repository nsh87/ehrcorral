#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test EHRcorral.

Tests for `ehrcorral` module.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest2 as unittest
import numpy as np
import json
import os

from faker import Faker

from ehrcorral.ehrcorral import Herd
from ehrcorral.ehrcorral import gen_record
from ehrcorral.ehrcorral import compress
from ehrcorral.compressions import soundex, nysiis, metaphone, dmetaphone
from ehrcorral.measures import *

fake = Faker()


try:
    unicode = unicode
except NameError:
    # Using Python 3
    unicode = str
    basestring = (str, bytes)


class TestHerdProperties(unittest.TestCase):

    def setUp(self):
        data_path = os.path.join(os.path.dirname(__file__), 'profiles_100.json')
        with open(data_path, 'r') as data_file:
            population = tuple(json.load(data_file))
        records = [gen_record(profile) for profile in population]
        self.herd = Herd()
        self.herd.populate(records)

    def test_herd_str_method(self):
        try:
            herd = Herd()
            str(herd)
        except Exception as e:
            self.fail("Getting string of empty herd raised: {0}.".format(e))
        self.assertEqual(str(herd), '()')
        try:
            herd = self.herd
            str(herd)
        except Exception as e:
            self.fail("Getting string of herd raised: {0}.".format(e))
        self.assertNotEqual(str(herd), '()')

    def test_retrieving_populated_herd_size(self):
        self.assertEqual(self.herd.size, 100)

    def test_retrieving_herd_size_with_no_population(self):
        try:
            herd = Herd()
        except Exception as e:
            self.fail("Creating herd with no population raised: {0}.".format(e))
        self.assertEqual(herd.size, 0)


class TestHerdCreation(unittest.TestCase):

    def setUp(self):
        data_path = os.path.join(os.path.dirname(__file__), 'profiles_100.json')
        with open(data_path, 'r') as data_file:
            self.profiles = tuple(json.load(data_file))

    def test_population_loaded_correctly(self):
        self.assertEqual(len(self.profiles), 100)

    def test_populating_herd(self):
        records = [gen_record(profile) for profile in self.profiles]
        herd = Herd()
        herd.populate(records)
        self.assertEqual(herd.size, 100)


class TestHerdCorral(unittest.TestCase):

    def setUp(self):
        data_path = os.path.join(os.path.dirname(__file__), 'profiles_100.json')
        with open(data_path, 'r') as data_file:
            population = tuple(json.load(data_file))
        records = [gen_record(profile) for profile in population]
        self.herd = Herd()
        self.herd.populate(records)

    def test_herd_corraling(self):
        self.herd.corral()
        for record in self.herd._population:
            self.assertIsInstance(record._blocks, tuple)
            self.assertTrue(1 <= len(record._blocks) <= 8)
            self.assertIsInstance(
                record._meta.forename_freq_ref, unicode
            )
            self.assertIsInstance(
                record._meta.mid_forename_freq_ref, unicode
            )
            self.assertIsInstance(
                record._meta.birth_surname_freq_ref, unicode
            )
            self.assertIsInstance(
                record._meta.current_surname_freq_ref, unicode
            )


class TestHerdFrequencyDictionaries(unittest.TestCase):

    def setUp(self):
        population = (
            {
                'forename': 'Adelyn',
                'mid_forename': 'Heidenreich',
                'current_surname': 'Bartell',
                'birth_surname': 'Gerlach'
            },
            {
                'forename': 'John',
                'mid_forename': 'Frederich',
                'current_surname': 'Sanders'
            },
            {
                'forename': 'Joseph',
                'current_surname': 'Smith'
            },
            {
                'forename': 'John',
                'mid_forename': 'Heidenreich',
                'current_surname': 'Smith',
                'birth_surname': 'Gerlach'
            }
        )
        records = [gen_record(profile) for profile in population]
        self.herd = Herd()
        self.herd.populate(records)
        self.herd.corral()

    def test_forename_freq_dict(self):
        self.assertEqual(self.herd._forename_freq_dict['J'], 3)
        self.assertEqual(self.herd._forename_freq_dict['H'], 2)
        self.assertEqual(self.herd._forename_freq_dict['j'], 0)
        self.assertEqual(len(self.herd._forename_freq_dict.keys()), 4)

    def test_surname_freq_dict(self):
        self.assertEqual(self.herd._surname_freq_dict['SM0'], 2)
        self.assertEqual(self.herd._surname_freq_dict['KRLK'], 2)
        self.assertEqual(self.herd._surname_freq_dict['smo'], 0)
        self.assertEqual(len(self.herd._surname_freq_dict.keys()), 4)


class TestRecordGeneration(unittest.TestCase):

    def setUp(self):
        data_path = os.path.join(os.path.dirname(__file__), 'profiles_100.json')
        with open(data_path, 'r') as data_file:
            self.profiles = tuple(json.load(data_file))

    def test_record_generation_from_fake_profiles(self):
        records = [gen_record(profile) for profile in self.profiles]
        self.assertEqual(len(records), 100)

    def test_record_generation_catches_invalid_profiles(self):
        with self.assertRaises(ValueError):
            record = gen_record({'forename': 'Joe'})
        with self.assertRaises(ValueError):
            record = gen_record({'birth_surname': 'Smith'})
        with self.assertRaises(ValueError):
            record = gen_record({'test': 'test'})


class TestPhonemicCompression(unittest.TestCase):

    def setUp(self):
        self.name = ['Jellyfish']
        self.names = ['Jellyfish', 'Exeter']
        self.empty = ['']

    def test_soundex_compression(self):
        single_compression = compress(self.name, soundex)
        self.assertEqual(single_compression, ['J412'])
        multiple_compressions = compress(self.names, soundex)
        self.assertEqual(multiple_compressions, ['J412', 'E236'])
        empty_compression = compress(self.empty, soundex)
        self.assertEqual(empty_compression, [''])

    def test_nysiis_compression(self):
        single_compression = compress(self.name, nysiis)
        self.assertEqual(single_compression, ['JALYF'])
        multiple_compressions = compress(self.names, nysiis)
        self.assertEqual(multiple_compressions, ['JALYF', 'EXATAR'])
        empty_compression = compress(self.empty, nysiis)
        self.assertEqual(empty_compression, [''])

    def test_metaphone_compression(self):
        single_compression = compress(self.name, metaphone)
        self.assertEqual(single_compression, ['JLFX'])
        multiple_compressions = compress(self.names, metaphone)
        self.assertEqual(multiple_compressions, ['JLFX', 'EKSTR'])
        empty_compression = compress(self.empty, metaphone)
        self.assertEqual(empty_compression, [''])

    def test_dmetaphone_compression(self):
        single_compression = compress(self.name, dmetaphone)
        self.assertEqual(single_compression, ['JLFX', 'ALFX'])
        multiple_compressions = compress(self.names, dmetaphone)
        self.assertEqual(multiple_compressions, ['JLFX', 'ALFX', 'AKSTR'])
        empty_compression = compress(self.empty, dmetaphone)
        self.assertEqual(empty_compression, [''])


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
        self.female_record.gen_blocks(dmetaphone)
        expected_blocks = ['PRTLA', 'KRLKA', 'JRLKA', 'PRTLH', 'KRLKH', 'JRLKH']
        self.assertItemsEqual(self.female_record._blocks, expected_blocks)

    def test_single_forename_and_surname(self):
        self.male_record.gen_blocks(dmetaphone)
        expected_blocks = ['NTRO']
        self.assertItemsEqual(self.male_record._blocks, expected_blocks)


class TestMeasuresSimilarityFunctions(unittest.TestCase):

    def setUp(self):
        population = (
            {
                'forename': 'Adelyn',
                'mid_forename': 'Heidenreich',
                'current_surname': 'Bartell',
                'birth_surname': 'Gerlach',
                'address1': '448 Jones Street',
                'postal_code': '95786',
                'sex': 'M',
                'birth_year': '1977',
                'birth_month': '08',
                'birth_day': '27'
            },
            {
                'forename': 'Adelyn',
                'mid_forename': 'Frederich',
                'current_surname': 'Gerlach'
            },
            {
                'forename': 'Joseph',
                'current_surname': 'Smith',
                'address1': '448 Jones Street',
                'postal_code': '95786',
                'sex': 'M',
                'birth_year': '1977',
                'birth_month': '08',
                'birth_day': '27'
            },
            {
                'forename': 'John',
                'mid_forename': 'Heidenreich',
                'current_surname': 'Smith',
                'birth_surname': 'Gerlach',
                'address1': '484 Jones Avenue',
                'postal_code': '97856',
                'sex': 'F',
                'birth_year': '1986',
                'birth_month': '10',
                'birth_day': '27'
            },
            {
                'forename': 'Jason',
                'current_surname': 'Sanders',
                'address1': '448 Jones Street',
                'address2': 'Apt. A',
                'postal_code': '97586',
                'sex': 'F',
                'birth_year': '1986',
                'birth_month': '10',
                'birth_day': '27'
            }
        )
        records = [gen_record(profile) for profile in population]
        self.herd = Herd()
        self.herd.populate(records)
        self.herd.corral()

    def test_extract_forename_info(self):
        record = self.herd._population[0]
        forename, weight = extract_forename_similarity_info(self.herd,
                                                            record,
                                                            'fore')
        self.assertEqual(forename, 'Adelyn')
        self.assertEqual(weight, 0.25)
        forename, weight = extract_forename_similarity_info(self.herd,
                                                            record,
                                                            'mid_fore')
        self.assertEqual(forename, 'Heidenreich')
        self.assertEqual(weight, 0.25)
        record = self.herd._population[4]
        forename, weight = extract_forename_similarity_info(self.herd,
                                                            record,
                                                            'fore')
        self.assertEqual(forename, 'Jason')
        self.assertEqual(weight, 0.375)
        forename, weight = extract_forename_similarity_info(self.herd,
                                                            record,
                                                            'mid_fore')
        self.assertEqual(forename, '')
        self.assertEqual(weight, 0.0)

    def test_extract_surname_info(self):
        record = self.herd._population[0]
        surname, weight = extract_surname_similarity_info(self.herd,
                                                          record,
                                                          'birth')
        self.assertEqual(surname, 'Gerlach')
        self.assertEqual(round(weight, 5), 0.42857)
        surname, weight = extract_surname_similarity_info(self.herd,
                                                          record,
                                                          'current')
        self.assertEqual(surname, 'Bartell')
        self.assertEqual(round(weight, 5), 0.14286)
        record = self.herd._population[4]
        surname, weight = extract_surname_similarity_info(self.herd,
                                                          record,
                                                          'birth')
        self.assertEqual(surname, '')
        self.assertEqual(weight, 0.0)
        surname, weight = extract_surname_similarity_info(self.herd,
                                                          record,
                                                          'current')
        self.assertEqual(surname, 'Sanders')
        self.assertEqual(round(weight, 5), 0.14286)

    def test_forename_similarity(self):
        records = [self.herd._population[0], self.herd._population[4]]
        weight = get_forename_similarity(self.herd,
                                         records,
                                         damerau_levenshtein,
                                         "fore")
        self.assertEqual(weight, -4.0)
        weight = get_forename_similarity(self.herd,
                                         records,
                                         damerau_levenshtein,
                                         "mid_fore")
        self.assertEqual(round(weight, 5), -4.90909)
        records = [self.herd._population[4], self.herd._population[0]]
        weight = get_forename_similarity(self.herd,
                                         records,
                                         damerau_levenshtein,
                                         "mid_fore")
        self.assertEqual(weight, 0)
        records = [self.herd._population[0], self.herd._population[3]]
        weight = get_forename_similarity(self.herd,
                                         records,
                                         damerau_levenshtein,
                                         "mid_fore")
        self.assertEqual(weight, 6.0)

    def test_surname_similarity(self):
        records = [self.herd._population[0], self.herd._population[4]]
        weight = get_surname_similarity(self.herd,
                                        records,
                                        damerau_levenshtein,
                                        "current")
        self.assertEqual(round(weight, 5), -5.14286)
        weight = get_surname_similarity(self.herd,
                                        records,
                                        damerau_levenshtein,
                                        "birth")
        self.assertEqual(weight, -12.0)
        records = [self.herd._population[4], self.herd._population[0]]
        weight = get_surname_similarity(self.herd,
                                        records,
                                        damerau_levenshtein,
                                        "birth")
        self.assertEqual(weight, 0)
        records = [self.herd._population[0], self.herd._population[1]]
        weight = get_surname_similarity(self.herd,
                                        records,
                                        damerau_levenshtein,
                                        "birth")
        self.assertEqual(weight, 12.0)

    def test_address_similarity(self):
        records = [self.herd._population[0], self.herd._population[1]]
        weight = get_address_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 0)
        records = [self.herd._population[0], self.herd._population[3]]
        weight = get_address_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 0)
        records = [self.herd._population[0], self.herd._population[4]]
        weight = get_address_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 2)
        records = [self.herd._population[0], self.herd._population[2]]
        weight = get_address_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 7)

    def test_post_code_similarity(self):
        records = [self.herd._population[0], self.herd._population[1]]
        weight = get_post_code_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 0)
        records = [self.herd._population[0], self.herd._population[3]]
        weight = get_post_code_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 0)
        records = [self.herd._population[0], self.herd._population[4]]
        weight = get_post_code_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 1)
        records = [self.herd._population[0], self.herd._population[2]]
        weight = get_post_code_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 4)

    def test_sex_similarity(self):
        records = [self.herd._population[0], self.herd._population[1]]
        weight = get_sex_similarity(records)
        self.assertEqual(weight, -10)
        records = [self.herd._population[0], self.herd._population[3]]
        weight = get_sex_similarity(records)
        self.assertEqual(weight, -10)
        records = [self.herd._population[0], self.herd._population[2]]
        weight = get_sex_similarity(records)
        self.assertEqual(weight, 1)

    def test_record_similarity(self):
        pass
