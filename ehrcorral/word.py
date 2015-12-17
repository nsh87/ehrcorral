# -*- coding: utf-8 -*-
""" This script was modified from https://github.com/oubiwann/metaphone, also on
PyPi at https://pypi.python.org/pypi/Metaphone/0.4. Currently, this package
does not support installation on Python 3.x, so it has been copied and modified
here to support Python 3.x. A request has also been submitted to the author to
support Python 3. The original LICENSE is below:

Copyright (c) 2007 Andrew Collins, Chris Leong
Copyright (c) 2009 Matthew Somerville
Copyright (c) 2010 Maximillian Dornseif, Richard Barran
Copyright (c) 2012 Duncan McGreggor
All rights reserved.

* Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

Neither the name "Metaphone" nor the names of its contributors may be used to
endorse or promote products derived from this software without specific prior
written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
import unicodedata


class Word(object):
    """
    """
    def __init__(self, input):
        self.original = input
        if isinstance(input, bytes):
            self.decoded = input.decode('utf-8', 'ignore')
        else:
            self.decoded = input
        self.decoded = self.decoded.replace('\xc7', "s")
        self.decoded = self.decoded.replace('\xe7', "s")
        self.normalized = ''.join(
            (c for c in unicodedata.normalize('NFD', self.decoded)
            if unicodedata.category(c) != 'Mn'))
        self.upper = self.normalized.upper()
        self.length = len(self.upper)
        self.prepad = "--"
        self.start_index = len(self.prepad)
        self.end_index = self.start_index + self.length - 1
        self.postpad = "------"
        # so we can index beyond the begining and end of the input string
        self.buffer = self.prepad + self.upper + self.postpad

    @property
    def is_slavo_germanic(self):
        return (
            self.upper.find('W') > -1
            or self.upper.find('K') > -1
            or self.upper.find('CZ') > -1
            or self.upper.find('WITZ') > -1)

    def get_letters(self, start=0, end=None):
        if not end:
            end = start + 1
        start = self.start_index + start
        end = self.start_index + end
        return self.buffer[start:end]
