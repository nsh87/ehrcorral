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
    current_surname_similarity = \
        get_surname_similarity(herd,
                               [first_record, second_record],
                               surname_method,
                               "current")
    # no place of birth field for similarity
    address_similarity = get_address_similarity([first_record, second_record])
    post_code_similarity = get_post_code_similarity([first_record,
                                                     second_record])
    sex_similarity = get_sex_similarity([first_record, second_record])
    dob_similarity = get_dob_similarity([first_record, second_record])


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
        weight = herd._forename_freq_dict[record._meta.forename_freq_ref] / \
            float(sum(herd._forename_freq_dict.values()))
    elif type == "mid_fore":
        forename = profile.mid_forename
        weight = herd._forename_freq_dict[record._meta.mid_forename_freq_ref]\
            / float(sum(herd._forename_freq_dict.values()))
    return forename, weight


def get_surname_similarity(herd, records, method, type):
    first_surname, first_weight = \
        extract_surname_similarity_info(herd, records[0], type)
    second_surname, second_weight = \
        extract_surname_similarity_info(herd, records[1], type)
    surname_weight = max(first_weight, second_weight, 1.0 / 1000)
    surname_cutoff = 1.0 / 500
    difference = damerau_levenshtein(first_surname, second_surname)
    max_length = max(len(first_surname), len(second_surname))
    if surname_weight > surname_cutoff:
        S = 6
    else:
        S = 17
    if difference == 0:
        similarity = 2 * S
    elif float(difference) / max_length < 0.3:
        similarity = S
    elif float(difference) / max_length < 0.6:
        similarity = -S
    else:
        similarity = -2 * S
    return similarity


def extract_surname_similarity_info(herd, record, type):
    profile = record.profile
    # Add try/except
    if type == "birth":
        surname = profile.birth_surname
        weight = herd._surname_freq_dict[record._meta.birth_surname_freq_ref]\
            / float(sum(herd._surname_freq_dict.values()))
    elif type == "current":
        surname = profile.current_surname
        weight = herd._surname_freq_dict[record._meta.current_surname_freq_ref]\
            / float(sum(herd._surname_freq_dict.values()))
    return surname, weight


def get_address_similarity(records):
    # ox-link only takes first 8 characters and greps for things like "flat"
    first_profile = records[0].profile
    second_profile = records[1].profile
    first_address = [first_profile.address1, first_profile.address2]
    second_address = [first_profile.address1, first_profile.address2]
    diff1 = damerau_levenshtein(first_address[0], second_address[0])
    if diff1 == 0:
        diff2 = damerau_levenshtein(first_address[1], second_address[1])
        if diff2 == 0:
            return 7
        else:
            return 2
    else:
        return 0


def get_post_code_similarity(records):
    first_profile = records[0].profile
    second_profile = records[1].profile
    first_post_code = first_profile.postal_code  # must be a string
    second_post_code = second_profile.postal_code  # must be a string
    difference = damerau_levenshtein(first_post_code, second_post_code)
    if difference == 0:
        return 4
    elif difference == 1: # for transposition, ox-link does not do this
        return 1
    else:
        return 0


def get_sex_similarity(records):
    first_profile = records[0].profile
    second_profile = records[1].profile
    first_sex = first_profile.sex
    second_sex = second_profile.sex
    if first_sex == second_sex:
        return 1
    else:
        return -10


def get_dob_similarity(records):
    first_profile = records[0].profile
    second_profile = records[1].profile
    first_dob = first_profile.birth_year, first_profile.birth_month, \
                first_profile.birth_day
    second_dob = second_profile.birth_year, second_profile.birth_month, \
                second_profile.birth_day
    

