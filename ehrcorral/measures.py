# -*- coding: utf-8 -*-
"""Contains functions for measures of similarity between records.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import pkgutil
import string

from pylev import damerau_levenshtein


def record_similarity(herd,
                      first_record,
                      second_record,
                      forename_method=damerau_levenshtein,
                      surname_method=damerau_levenshtein):
    """Determine weights for the likelihood of two records being the same.

    Args:
        herd (Herd): An object of :py:class:`.Herd` which contains the two
            records being compared.
        first_record (Record): An object of :py:class:`.Record` to be
            compared to the other one.
        second_record (Record): An object of :py:class:`.Record` to be
            compared to the other one.
        forename_method (func): A function that performs some sort of
            comparison between strings.
        surname_method (func): A function that performs some sort of
            comparison between strings.

    Returns:
        A tuple of the sum of name weights and the sum of non-name weights.
    """
    forename_similarity, fore_max = \
        get_forename_similarity(herd,
                                [first_record, second_record],
                                forename_method,
                                "fore")
    mid_forename_similarity, mid_fore_max = \
        get_forename_similarity(herd,
                                [first_record, second_record],
                                forename_method,
                                "mid_fore")
    birth_surname_similarity, bir_sur_max = \
        get_surname_similarity(herd,
                               [first_record, second_record],
                               surname_method,
                               "birth")
    current_surname_similarity, cur_sur_max = \
        get_surname_similarity(herd,
                               [first_record, second_record],
                               surname_method,
                               "current")
    # no place of birth field for similarity
    address_similarity = get_address_similarity([first_record, second_record],
                                                damerau_levenshtein)
    post_code_similarity = get_post_code_similarity([first_record,
                                                     second_record],
                                                    damerau_levenshtein)
    sex_similarity = get_sex_similarity([first_record, second_record])
    dob_similarity = get_dob_similarity([first_record, second_record])
    id_similarity = get_id_similarity([first_record, second_record],
                                      damerau_levenshtein)
    # did not include GP (doctor), place of birth, hospital and hospital number
    name_sum = forename_similarity + mid_forename_similarity + \
        birth_surname_similarity + current_surname_similarity
    # since we are not using a few of the ox-link weights, the non-name
    # numbers will be different
    non_name_sum = address_similarity + post_code_similarity + sex_similarity +\
        dob_similarity + id_similarity
    # sum of max weights for all fields
    max_similarity = fore_max + mid_fore_max + bir_sur_max + cur_sur_max + 33.0
    return (name_sum + non_name_sum) / max_similarity


def get_forename_similarity(herd, records, method, name_type):
    """Determine weights for the likelihood of two forenames being the same.

    Args:
        herd (Herd): An object of :py:class:`.Herd` which contains the two
            records being compared.
        records (List[Record]): A list of two objects of :py:class:`.Record`
            to be compared to one another.
        method (func): A function to be used to compare the forenames.
        name_type (unicode): A unicode string to indicate which forename is
            being compared.

    Returns:
        The forename weight for the similarity of the forenames.
    """
    name_types = ["fore", "mid_fore"]
    first_forename, first_freq = \
        extract_forename_similarity_info(herd, records[0], name_type)
    # Get both names and frequencies from second record to compare to first
    second_forefreq = [
        extract_forename_similarity_info(herd, records[1], name)
        for name in name_types
        ]
    second_forename = [item[0] for item in second_forefreq]
    second_freq = [item[1] for item in second_forefreq]
    # if there is no forename for our first record, we either dismiss the
    # similarity if one of the second record forenames is empty, or return a
    # zero match.
    if first_forename == '':
        if second_forename[0] == '' or second_forename[1] == '':
            return 0, 0
        else:
            return 0, 6
    # Get difference between first record name and both second record names,
    # then find the one that has the minimum difference and keep that one
    diffs = [method(first_forename, name) for name in second_forename]
    difference = min(diffs)
    min_index = diffs.index(difference)
    second_forename = second_forename[min_index]
    second_freq = second_freq[min_index]
    max_length = max(len(first_forename), len(second_forename))
    prop_diff = float(difference) / max_length
    prop_freq = max(first_freq, second_freq, 1.0 / 1000)
    # scale instead of using cutoff
    cutoff = 5.0 / 26  # arbitrary, could be improved
    F = 3 if prop_freq > cutoff else 12
    # map prop_diff from (0, 1) to (-2, 2), then flip sign since lower diff
    # implies that the two name are more similar.
    weight = -(4 * prop_diff - 2)
    return weight * F, 2 * F


def extract_forename_similarity_info(herd, record, name_type):
    """Extract desired forename and associated frequency weight.

    Args:
        herd (Herd): An object of :py:class:`.Herd` which contains the
            frequency dictionary used for the frequency weight.
        record (Record): An object of :py:class:`.Record` from which to
            extract the forename.
        name_type (unicode): A unicode string to indicate which forename is
            being extracted.

    Returns:
        The forename and associated frequency weight for requested name.
    """
    profile = record.profile
    # Add try/except
    if name_type == "fore":
        forename = profile.forename.lower()
        weight = herd._forename_freq_dict[record._meta.forename_freq_ref] / \
            float(sum(herd._forename_freq_dict.values()))
    elif name_type == "mid_fore":
        forename = profile.mid_forename.lower()
        weight = herd._forename_freq_dict[record._meta.mid_forename_freq_ref]\
            / float(sum(herd._forename_freq_dict.values()))
    return forename, weight


def get_surname_similarity(herd, records, method, name_type):
    """Determine weights for the likelihood of two surnames being the same.

    Args:
        herd (Herd): An object of :py:class:`.Herd` which contains the two
            records being compared.
        records (List[Record]): A list of two objects of :py:class:`.Record`
            to be compared to one another.
        method (func): A function to be used to compare the surnames.
        name_type (unicode): A unicode string to indicate which surname is
            being compared.

    Returns:
        The surname weight for the similarity of the surnames.
    """
    name_types = ["birth", "current"]
    first_surname, first_freq = \
        extract_surname_similarity_info(herd, records[0], name_type)
    # Get both names and frequencies from second record to compare to first
    second_forefreq = [
        extract_surname_similarity_info(herd, records[1], name)
        for name in name_types
        ]
    second_surname = [item[0] for item in second_forefreq]
    second_freq = [item[1] for item in second_forefreq]
    # if there is no surname for our first record, we either dismiss the
    # similarity if one of the second record surnames is empty, or return a
    # zero match.
    if first_surname == '':
        if second_surname[0] == '' or second_surname[1] == '':
            return 0, 0
        else:
            return 0, 12
    # Get difference between first record name and both second record names,
    # then find the one that has the minimum difference and keep that one
    diffs = [method(first_surname, name) for name in second_surname]
    difference = min(diffs)
    min_index = diffs.index(difference)
    second_surname = second_surname[min_index]
    second_freq = second_freq[min_index]
    max_length = max(len(first_surname), len(second_surname))
    prop_diff = float(difference) / max_length
    prop_freq = max(first_freq, second_freq, 1.0 / 1000)
    cutoff = 1.0 / 500  # arbitrary, could be improved
    S = 6 if prop_freq > cutoff else 17
    # map prop_diff from (0, 1) to (-2, 2), then flip sign since lower diff
    # implies that the two name are more similar.
    weight = -(4 * prop_diff - 2)
    return weight * S, 2 * S


def extract_surname_similarity_info(herd, record, name_type):
    """Extract desired surname and associated frequency weight.

    Args:
        herd (Herd): An object of :py:class:`.Herd` which contains the
            frequency dictionary used for the frequency weight.
        record (Record): An object of :py:class:`.Record` from which to
            extract the surname.
        name_type (unicode): A unicode string to indicate which surname is
            being extracted.

    Returns:
        The forename and associated frequency weight for requested name.
    """
    profile = record.profile
    # Add try/except
    if name_type == "birth":
        surname = profile.birth_surname.lower()
        weight = herd._surname_freq_dict[record._meta.birth_surname_freq_ref]\
            / float(sum(herd._surname_freq_dict.values()))
    elif name_type == "current":
        surname = profile.current_surname.lower()
        weight = herd._surname_freq_dict[record._meta.current_surname_freq_ref]\
            / float(sum(herd._surname_freq_dict.values()))
    return surname, weight


def get_address_similarity(records, method=damerau_levenshtein):
    """Determine weights for the likelihood of two addresses being the same.

    Args:
        records (List[Record]): A list of two objects of :py:class:`.Record`
            to be compared to one another.
        method (func): A function to be used to compare the addresses.

    Returns:
        The address weight for the similarity of the addresses.
    """
    # ox-link only takes first 8 characters
    first_profile = records[0].profile
    second_profile = records[1].profile
    first_address = first_profile.address1.lower() +\
        ' ' +\
        first_profile.address2.lower()
    second_address = second_profile.address1.lower() +\
        ' ' +\
        second_profile.address2.lower()
    first_address = clean_address(first_address)
    second_address = clean_address(second_address)
    difference = method(first_address[:12], second_address[:12])
    if difference == 0:
        return 7
    elif difference <= 2:
        return 2
    else:
        return 0
    # ox-link method
    # return 7 if diff1 == 0 else 0


def clean_address(address):
    """Clean unicode string that contains an address of all punctuation and
    standardize all street suffixes and unit designators.

    Args:
        address (unicode): A unicode string that contains an address to be
            cleaned and standardized.

    Returns:
        The cleaned unicode address string.
    """
    new_address = ' ' + address + ' '
    generic_abbrevs = get_json('generic_abbrevs.json')
    generics = get_json('generics.json')
    unit_abbrevs = get_json('unit_abbrevs.json')
    designators = get_json('designators.json')
    for char in string.punctuation:
        new_address = new_address.replace(char, ' ')
    for i, generic in enumerate(generics):
        for g in generic:
            old = ' ' + g + ' '
            new = ' ' + generic_abbrevs[i] + ' '
            new_address = new_address.replace(old, new)
    for i, designator in enumerate(designators):
        old = ' ' + designator + ' '
        new = ' ' + unit_abbrevs[i] + ' '
        new_address = new_address.replace(old, new)
    return ' '.join(new_address.split())


def get_post_code_similarity(records, method=damerau_levenshtein):
    """Determine weights for the likelihood of two postal codes being the same.

    Args:
        records (List[Record]): A list of two objects of :py:class:`.Record`
            to be compared to one another.
        method (func): A function to be used to compare the postal codes.

    Returns:
        The postal code weight for the similarity of the postal codes.
    """
    first_profile = records[0].profile
    second_profile = records[1].profile
    first_post_code = str(first_profile.postal_code)  # must be a string
    second_post_code = str(second_profile.postal_code)  # must be a string
    difference = method(first_post_code, second_post_code)
    if difference == 0:
        return 4
    elif difference == 1:  # for transposition, ox-link does not do this
        return 1
    else:
        return 0
    # ox-link method
    # return 4 if difference == 0 else 0


def get_sex_similarity(records):
    """Determine weights for the likelihood of two sexes being the same.

    Args:
        records (List[Record]): A list of two objects of :py:class:`.Record`
            to be compared to one another.

    Returns:
        The sex weight for the similarity of the sexes.
    """
    # consider how better to account for sexes besides male and female
    first_profile = records[0].profile
    second_profile = records[1].profile
    # just take first letter so that male = m
    # TODO: Consider robust way to consider non-binary sexes
    first_sex = str(first_profile.sex.lower())  # should be a string
    second_sex = str(second_profile.sex.lower())  # should be a string
    return 1 if first_sex == second_sex else -10


def get_dob_similarity(records, method=damerau_levenshtein):
    """Determine weights for the likelihood of two dates of birth being the
    same.

    Args:
        records (List[Record]): A list of two objects of :py:class:`.Record`
            to be compared to one another.
        method (func): A function to be used to compare the dates of birth.

    Returns:
        The date of birth weight for the similarity of the dates of birth.
    """
    first_profile = records[0].profile
    second_profile = records[1].profile
    first_dob = str(first_profile.birth_year), \
        str(first_profile.birth_month), \
        str(first_profile.birth_day)
    second_dob = str(second_profile.birth_year), \
        str(second_profile.birth_month), \
        str(second_profile.birth_day)
    # just return 0 if either dob is empty
    if first_dob[0] == first_dob[1] == first_dob[2] == '' or \
        second_dob[0] == second_dob[1] == second_dob[2]:
        return 0
    # TODO: penalize for year diffs like 1983 to 1975
    year_diff = method(first_dob[0], second_dob[0])
    month_diff = method(first_dob[1], second_dob[1])
    day_diff = method(first_dob[2], second_dob[2])
    # could add more complexity here based off of ox-link
    year_prop = 0.5  # slightly arbitrary choice because year means more
    month_prop = 0.25
    day_prop = 0.25
    prop_diff = year_prop * (year_diff / 4.0) + \
        month_prop * (month_diff / 2.0) + \
        day_prop * (day_diff / 2.0)
    # map prop_diff from (0, 1) to (-23, 14), then flip sign since lower diff
    # implies that the two name are more similar.
    return -(37 * prop_diff - 14)


def get_id_similarity(records, method=damerau_levenshtein):
    """Determine weights for the likelihood of two national IDs being the same.

    Args:
        records (List[Record]): A list of two objects of :py:class:`.Record`
            to be compared to one another.
        method (func): A function to be used to compare the national IDs.

    Returns:
        The national ID weight for the similarity of the two national IDs.
    """
    first_profile = records[0].profile
    second_profile = records[1].profile
    first_id = str(first_profile.national_id1.lower())  # must be a string
    second_id = str(second_profile.national_id1.lower())  # must be a string
    difference = method(first_id, second_id)
    if difference == 0:
        return 7
    elif difference == 1:  # for transposition, ox-link does not do this
        return 2
    else:
        return 0
    # ox-link method
    # return 7 if difference == 0 else 0


def get_json(file_name):
    data = pkgutil.get_data('ehrcorral', file_name)
    return json.loads(data.decode())

