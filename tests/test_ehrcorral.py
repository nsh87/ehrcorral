#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_ehrcorral
----------------------------------

Tests for `ehrcorral` module.
"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

from ehrcorral import ehrcorral
from faker import Faker

fake = Faker()
fake.seed(8548)


class TestEHRcorral(unittest.TestCase):

    def setUp(self):
        profile_fields = ['name', 'birthdate', 'ssn', 'address']
        self.herd = [fake.profile(fields=profile_fields) for n in xrange(100)]

    def test_something(self):
        pass

    def tearDown(self):
        pass
