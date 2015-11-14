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
    # look into how to use weights properly since S in the table seems to
    # already account for some of this.
    forename_similarity = \
        get_forename_similarity(herd,
                                [first_record, second_record],
                                forename_method,
                                "fore")
    mid_forename_similarity = \
        get_forename_similarity(herd,
                                [first_record, second_record],
                                forename_method,
                                "mid_fore")
    birth_surname_similarity = \
        get_surname_similarity(herd,
                               [first_record, second_record],
                               surname_method,
                               "birth")


def get_forename_similarity(herd, records, method, type):
    first_forename, first_weight = \
        extract_forename_similarity_info(herd, records[0], type)
    second_forename, second_weight = \
        extract_forename_similarity_info(herd, records[1], type)
    forename_weight = max(first_weight, second_weight, 1.0 / 1000)
    forename_cutoff = 5.0 / 26
    difference = damerau_levenshtein(first_forename, second_forename)
    max_length = max(len(first_forename), len(second_forename))
    # investigate use of weights
    if forename_weight > forename_cutoff:
        F = 3
    else:
        F = 12
    if difference == 0:
        similarity = 2 * F
    elif float(difference) / max_length < 0.3:
        similarity = F
    elif float(difference) / max_length < 0.6:
        similarity = -F
    else:
        similarity = -2 * F
    return similarity


def extract_forename_similarity_info(herd, record, type):
    profile = record.profile
    # Add try/except
    if type == "fore":
        forename = profile.forename
    elif type == "mid_fore":
        forename = profile.mid_forename
    weight = herd._forename_freq_dict[
                              record._meta.forename_freq_ref] / float(sum(
        herd._forename_freq_dict.values()))
    return forename, weight


def get_surname_similarity(herd, records, method, type):
    pass


def extract_surname_similarity_info(herd, record, type):
    profile = record.profile
    # Add try/except
    if type == "birth":
        forename = profile.forename
    elif type == "current":
        forename = profile.mid_forename
    weight = herd._forename_freq_dict[
                              record._meta.forename_freq_ref] / float(sum(
        herd._forename_freq_dict.values()))
    return forename, weight

