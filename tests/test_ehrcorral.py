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

from faker import Faker

from ehrcorral.ehrcorral import Herd
from ehrcorral.ehrcorral import gen_record
from ehrcorral.ehrcorral import compress
from ehrcorral.compressions import soundex, nysiis, metaphone, dmetaphone

fake = Faker()


class TestHerdProperties(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        data_path = os.path.join(os.path.dirname(__file__), 'profiles_100.json')
        with open(data_path, 'r') as data_file:
            population = tuple(json.load(data_file))
        records = [gen_record(profile) for profile in population]
        cls.herd = Herd()
        cls.herd.populate(records)

    def test_herd_str_method(self):
        try:
            herd = Herd()
            str(herd)
        except Exception as e:
            self.fail("Getting string of empty herd raised: {}.".format(e))
        self.assertEqual(str(herd), '()')
        try:
            herd = self.herd
            str(herd)
        except Exception as e:
            self.fail("Getting string of herd raised: {}.".format(e))
        self.assertNotEqual(str(herd), '()')

    def test_retrieving_populated_herd_size(self):
        self.assertEqual(self.herd.size, 100)

    def test_retrieving_herd_size_with_no_population(self):
        try:
            herd = Herd()
        except Exception as e:
            self.fail("Creating herd with no population raised: {}.".format(e))
        self.assertEqual(herd.size, 0)


class TestHerdCreation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        data_path = os.path.join(os.path.dirname(__file__), 'profiles_100.json')
        with open(data_path, 'r') as data_file:
            cls.profiles = tuple(json.load(data_file))

    def test_population_loaded_correctly(self):
        self.assertEqual(len(self.profiles), 100)

    def test_populating_herd(self):
        records = [gen_record(profile) for profile in self.profiles]
        herd = Herd()
        herd.populate(records)
        self.assertEqual(herd.size, 100)


class TestHerdCorral(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        data_path = os.path.join(os.path.dirname(__file__), 'profiles_100.json')
        with open(data_path, 'r') as data_file:
            population = tuple(json.load(data_file))
        records = [gen_record(profile) for profile in population]
        cls.herd = Herd()
        cls.herd.populate(records)

    def test_herd_corraling(self):
        self.herd.corral()
        for record in self.herd._population:
            self.assertIsInstance(record._blocks, tuple)
            self.assertTrue(1 <= len(record._blocks) <= 8)
            self.assertIsInstance(record._meta.forename_freq_ref, str)
            self.assertIsInstance(record._meta.mid_forename_freq_ref, str)
            self.assertIsInstance(record._meta.birth_surname_freq_ref, str)
            self.assertIsInstance(record._meta.current_surname_freq_ref, str)
            count1 = 0
            count2 = 0
            count3 = 0
            if record._meta.forename_freq_ref:
                count1 += 1
            if record._meta.mid_forename_freq_ref:
                count1 += 1
            if record._meta.birth_surname_freq_ref:
                count2 += 1
            if record._meta.current_surname_freq_ref:
                count2 += 1
            self.assertTrue(count3 <= sum(len(v) for v in
                                          self.herd._block_dict.itervalues()))
            count3 = sum(len(v) for v in self.herd._block_dict.itervalues())
        self.assertTrue(sum(self.herd._forename_freq_dict.values()) == count1)
        self.assertTrue(sum(self.herd._surname_freq_dict.values()) == count2)


class TestRecordGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        data_path = os.path.join(os.path.dirname(__file__), 'profiles_100.json')
        with open(data_path, 'r') as data_file:
            cls.profiles = tuple(json.load(data_file))

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

    @classmethod
    def setUpClass(cls):
        cls.name = ['Jellyfish']
        cls.names = ['Jellyfish', 'Exeter']

    def test_soundex_compression(self):
        single_compression = compress(self.name, soundex)
        self.assertEqual(single_compression, ['J412'])
        multiple_compressions = compress(self.names, soundex)
        self.assertEqual(multiple_compressions, ['J412', 'E236'])

    def test_nysiis_compression(self):
        single_compression = compress(self.name, nysiis)
        self.assertEqual(single_compression, ['JALYF'])
        multiple_compressions = compress(self.names, nysiis)
        self.assertEqual(multiple_compressions, ['JALYF', 'EXATAR'])

    def test_metaphone_compression(self):
        single_compression = compress(self.name, metaphone)
        self.assertEqual(single_compression, ['JLFX'])
        multiple_compressions = compress(self.names, metaphone)
        self.assertEqual(multiple_compressions, ['JLFX', 'EKSTR'])

    def test_dmetaphone_compression(self):
        single_compression = compress(self.name, dmetaphone)
        self.assertEqual(single_compression, ['JLFX', 'ALFX'])
        multiple_compressions = compress(self.names, dmetaphone)
        self.assertEqual(multiple_compressions, ['JLFX', 'ALFX', 'AKSTR'])


class TestPhonemicBlocking(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Female profile with different birth surname and current surname
        female = {
            'forename': 'Adelyn',
            'mid_forename': 'Heidenreich',
            'current_surname': 'Bartell',
            'birth_surname': 'Gerlach'
        }
        cls.female_record = gen_record(female)
        # Male profile with some missing name fields
        male = {
            'forename': 'Oliver',
            'current_surname': 'Nader'
        }
        cls.male_record = gen_record(male)

    def test_multiple_surnames_and_forenames(self):
        self.female_record.gen_blocks(dmetaphone)
        expected_blocks = ['PRTLA', 'KRLKA', 'JRLKA', 'PRTLH', 'KRLKH', 'JRLKH']
        self.assertItemsEqual(self.female_record._blocks, expected_blocks)

    def test_single_forename_and_surname(self):
        self.male_record.gen_blocks(dmetaphone)
        expected_blocks = ['NTRO']
        self.assertItemsEqual(self.male_record._blocks, expected_blocks)
