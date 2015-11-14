"""Contains functions for measures of similarity between records.
"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from ehrcorral.ehrcorral import Herd, Record
from pylev import levenshtein, damerau_levenshtein

def record_similarity(herd,
                      first_record,
                      second_record,
                      forename_method=levenshtein,
                      surname_method=levenshtein):
    """Determine probability of two records being the same.

    Args:
        first_record (Record): An object of :py:class:`.Record` to be
            compared to the other one.
        second_record (Record): An object of :py:class:`.Record` to be
            compared to the other one.
        forename_method (func): A function that performs some sort of
            comparison between strings.
        surname_method (func): A function that performs some sort of
            comparison between strings.
        """
    first_profile = first_record.profile
    second_profile = second_record.profile
    first_forename = first_profile.forename
    second_forename = second_profile.forename
    forename_weight = max(herd._forename_freq_dict[
                              first_record._meta.forename_freq_ref],
                          herd._forename_freq_dict[
                              second_record._meta.forename_freq_ref]) / sum(
        herd._forename_freq_dict.values())
    forename_similarity = name_similarity([first_forename, second_forename],
                                          forename_weight)

def name_similarity(names, weights, method):
    pass
