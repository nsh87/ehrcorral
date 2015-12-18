#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test EHRcorral.

Tests for `ehrcorral` module.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import numpy as np
import unittest2 as unittest
from faker import Faker

from ehrcorral.compressions import soundex, nysiis, metaphone, dmetaphone
from ehrcorral.ehrcorral import Herd
from ehrcorral.ehrcorral import compress
from ehrcorral.ehrcorral import gen_record
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
                'national_id1': 'D599776',
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
                'national_id1': 'D599776',
                'birth_year': '1977',
                'birth_month': '08',
                'birth_day': '27'
            },
            {
                'forename': 'John',
                'mid_forename': 'Heidenreich',
                'current_surname': 'Smith',
                'birth_surname': 'Gerlach',
                'address1': '448 Jones Avenue',
                'postal_code': '97856',
                'sex': 'F',
                'national_id1': 'D599886',
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
                'national_id1': 'D597976',
                'birth_year': '1977',
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
        self.assertEqual(forename, 'adelyn')
        self.assertEqual(weight, 0.25)
        forename, weight = extract_forename_similarity_info(self.herd,
                                                            record,
                                                            'mid_fore')
        self.assertEqual(forename, 'heidenreich')
        self.assertEqual(weight, 0.25)
        record = self.herd._population[4]
        forename, weight = extract_forename_similarity_info(self.herd,
                                                            record,
                                                            'fore')
        self.assertEqual(forename, 'jason')
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
        self.assertEqual(surname, 'gerlach')
        self.assertEqual(round(weight, 5), 0.42857)
        surname, weight = extract_surname_similarity_info(self.herd,
                                                          record,
                                                          'current')
        self.assertEqual(surname, 'bartell')
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
        self.assertEqual(surname, 'sanders')
        self.assertEqual(round(weight, 5), 0.14286)

    def test_forename_similarity(self):
        records = [self.herd._population[0], self.herd._population[4]]
        weight = get_forename_similarity(self.herd,
                                         records,
                                         damerau_levenshtein,
                                         "fore")
        self.assertEqual(weight, (-4.0, 6))
        weight = get_forename_similarity(self.herd,
                                         records,
                                         damerau_levenshtein,
                                         "mid_fore")
        self.assertEqual((round(weight[0], 5), weight[1]), (-4.90909, 6))
        records = [self.herd._population[4], self.herd._population[0]]
        weight = get_forename_similarity(self.herd,
                                         records,
                                         damerau_levenshtein,
                                         "mid_fore")
        self.assertEqual(weight, (0, 6))
        records = [self.herd._population[0], self.herd._population[3]]
        weight = get_forename_similarity(self.herd,
                                         records,
                                         damerau_levenshtein,
                                         "mid_fore")
        self.assertEqual(weight, (6.0, 6))

    def test_surname_similarity(self):
        records = [self.herd._population[0], self.herd._population[4]]
        weight = get_surname_similarity(self.herd,
                                        records,
                                        damerau_levenshtein,
                                        "current")
        self.assertEqual((round(weight[0], 5), weight[1]), (-5.14286, 12))
        weight = get_surname_similarity(self.herd,
                                        records,
                                        damerau_levenshtein,
                                        "birth")
        self.assertEqual(weight, (-12.0, 12))
        records = [self.herd._population[4], self.herd._population[0]]
        weight = get_surname_similarity(self.herd,
                                        records,
                                        damerau_levenshtein,
                                        "birth")
        self.assertEqual(weight, (0, 12))
        records = [self.herd._population[0], self.herd._population[1]]
        weight = get_surname_similarity(self.herd,
                                        records,
                                        damerau_levenshtein,
                                        "birth")
        self.assertEqual(weight, (12.0, 12))

    def test_address_similarity(self):
        records = [self.herd._population[0], self.herd._population[1]]
        weight = get_address_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 0)
        records = [self.herd._population[0], self.herd._population[3]]
        weight = get_address_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 2)
        records = [self.herd._population[0], self.herd._population[4]]
        weight = get_address_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 7)
        records = [self.herd._population[0], self.herd._population[2]]
        weight = get_address_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 7)

    def test_clean_address(self):
        address = u'448 Jones Street'.lower()
        cleaned_address = clean_address(address)
        self.assertEqual(cleaned_address, u'448 jones st')
        address = u'448 Jones Avenue, Apartment 2'.lower()
        cleaned_address = clean_address(address)
        self.assertEqual(cleaned_address, u'448 jones ave apt 2')
        address = u'448-A Stromme Strt;; Building G'.lower()
        cleaned_address = clean_address(address)
        self.assertEqual(cleaned_address, u'448 a stromme st bldg g')
        self.assertEqual(clean_address(u''), u'')
        self.assertEqual(clean_address(u' '), u'')

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

    def test_dob_similarity(self):
        records = [self.herd._population[0], self.herd._population[1]]
        weight = get_dob_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 0)
        records = [self.herd._population[0], self.herd._population[2]]
        weight = get_dob_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 14)
        records = [self.herd._population[0], self.herd._population[3]]
        weight = get_dob_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, -4.5)
        records = [self.herd._population[0], self.herd._population[4]]
        weight = get_dob_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 4.75)

    def test_id_similarity(self):
        records = [self.herd._population[0], self.herd._population[1]]
        weight = get_id_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 0)
        records = [self.herd._population[0], self.herd._population[3]]
        weight = get_id_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 0)
        records = [self.herd._population[0], self.herd._population[4]]
        weight = get_id_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 2)
        records = [self.herd._population[0], self.herd._population[2]]
        weight = get_id_similarity(records, damerau_levenshtein)
        self.assertEqual(weight, 7)

    def test_record_similarity(self):
        records = [self.herd._population[0], self.herd._population[1]]
        weight = record_similarity(self.herd,
                                   records[0],
                                   records[1],
                                   damerau_levenshtein,
                                   damerau_levenshtein)
        self.assertEqual(round(weight, 5), -0.00038)
        records = [self.herd._population[0], self.herd._population[2]]
        weight = record_similarity(self.herd,
                                   records[0],
                                   records[1],
                                   damerau_levenshtein,
                                   damerau_levenshtein)
        self.assertEqual(round(weight, 5), 0.08752)
        records = [self.herd._population[0], self.herd._population[3]]
        weight = record_similarity(self.herd,
                                   records[0],
                                   records[1],
                                   damerau_levenshtein,
                                   damerau_levenshtein)
        self.assertEqual(round(weight, 5), -0.10248)
        records = [self.herd._population[0], self.herd._population[4]]
        weight = record_similarity(self.herd,
                                   records[0],
                                   records[1],
                                   damerau_levenshtein,
                                   damerau_levenshtein)
        self.assertEqual(round(weight, 5), -0.30872)
        records = [self.herd._population[0], self.herd._population[0]]
        weight = record_similarity(self.herd,
                                   records[0],
                                   records[1],
                                   damerau_levenshtein,
                                   damerau_levenshtein)
        self.assertEqual(round(weight, 5), 1.0)


class TestHerdSimilarityMatrix(unittest.TestCase):

    def setUp(self):
        population = (
            {
                'forename': 'Adelyn',
                'mid_forename': 'Heidenreich',
                'current_surname': 'Bartell',
                'birth_surname': 'Gerlach',
                'address1': '448 Jones Street',
                'postal_code': '95786',
                'sex': 'F',
                'birth_year': '1977',
                'birth_month': '08',
                'birth_day': '27'
            },
            {
                'forename': 'Jane',
                'current_surname': 'Doe',
                'address1': '448 Jones Street',
                'postal_code': '95786',
                'sex': 'F',
                'birth_year': '1977',
                'birth_month': '08',
                'birth_day': '27'
            },
            {
                'forename': 'Adelyn',
                'current_surname': 'Bartell',
                'address1': '612 Johson Ave',
                'postal_code': '92436',
                'sex': 'F',
                'birth_year': '1977',
                'birth_month': '08',
                'birth_day': '27'
            }
        )
        records = [gen_record(profile) for profile in population]
        self.herd = Herd()
        self.herd.populate(records)
        self.herd.corral()

    def test_similarity_matrix(self):
        test_similarity = np.array([
            [
                record_similarity(self.herd, self.herd._population[0],
                                  self.herd._population[0],
                                  damerau_levenshtein,
                                  damerau_levenshtein),
                0,
                record_similarity(self.herd, self.herd._population[0],
                                  self.herd._population[2],
                                  damerau_levenshtein,
                                  damerau_levenshtein)],
            [
                0,
                record_similarity(self.herd, self.herd._population[1],
                                  self.herd._population[1],
                                  damerau_levenshtein,
                                  damerau_levenshtein),
                0],
            [
                record_similarity(self.herd, self.herd._population[2],
                                  self.herd._population[0],
                                  damerau_levenshtein,
                                  damerau_levenshtein),
                0,
                record_similarity(self.herd, self.herd._population[2],
                                  self.herd._population[2],
                                  damerau_levenshtein,
                                  damerau_levenshtein)]],
            dtype=np.float32)
        self.assertTrue((test_similarity == self.herd.similarity_matrix).all())


class TestCommonCharacterErrors(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_no_errors(self):
        """See how the probability matrix looks with no textual errors."""
        herd = Herd()
        data_path = os.path.join(os.path.dirname(__file__),
                                 'error_free_3x2.json')
        with open(data_path, 'r') as data_file:
            population = tuple(json.load(data_file))
        records = [gen_record(profile) for profile in population]
        herd = Herd()
        herd.populate(records)
        herd.corral()
        print()
        print(herd.similarity_matrix)

    def test_character_insertion(self):
        """See how character insertion in someone's name impacts probability
        matrix.
        """
        herd = Herd()
        data_path = os.path.join(os.path.dirname(__file__),
                                 'character_insertion_3x2.json')
        with open(data_path, 'r') as data_file:
            population = tuple(json.load(data_file))
        records = [gen_record(profile) for profile in population]
        herd = Herd()
        herd.populate(records)
        herd.corral()
        print()
        print(herd.similarity_matrix)

    def test_character_omission(self):
        """See how character omission in someone's name impacts probability
        matrix.
        """
        herd = Herd()
        data_path = os.path.join(os.path.dirname(__file__),
                                 'character_omission_3x2.json')
        with open(data_path, 'r') as data_file:
            population = tuple(json.load(data_file))
        records = [gen_record(profile) for profile in population]
        herd = Herd()
        herd.populate(records)
        herd.corral()
        print()
        print(herd.similarity_matrix)

    def test_character_substitution(self):
        """See how character substitution in someone's name impacts probability
        matrix.
        """
        herd = Herd()
        data_path = os.path.join(os.path.dirname(__file__),
                                 'character_substitution_3x2.json')
        with open(data_path, 'r') as data_file:
            population = tuple(json.load(data_file))
        records = [gen_record(profile) for profile in population]
        herd = Herd()
        herd.populate(records)
        herd.corral()
        print()
        print(herd.similarity_matrix)

    def test_character_transposition(self):
        """See how character transposition in someone's name impacts probability
        matrix.
        """
        herd = Herd()
        data_path = os.path.join(os.path.dirname(__file__),
                                 'character_transposition_3x2.json')
        with open(data_path, 'r') as data_file:
            population = tuple(json.load(data_file))
        records = [gen_record(profile) for profile in population]
        herd = Herd()
        herd.populate(records)
        herd.corral()
        print()
        print(herd.similarity_matrix)

    def test_gender_misclassification(self):
        """See how gender misclassification impacts probability matrix.
        """
        herd = Herd()
        data_path = os.path.join(os.path.dirname(__file__),
                                 'gender_misclassification_3x2.json')
        with open(data_path, 'r') as data_file:
            population = tuple(json.load(data_file))
        records = [gen_record(profile) for profile in population]
        herd = Herd()
        herd.populate(records)
        herd.corral()
        print()
        print(herd.similarity_matrix)
