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
    # did not include GP (doctor), place of birth, hospital and hospital number
    name_sum = forename_similarity + mid_forename_similarity +\
        birth_surname_similarity + current_surname_similarity
    # since we are not using a few of the ox-link weights, the non-name
    # numbers will be different
    non_name_sum = address_similarity + post_code_similarity + sex_similarity +\
        dob_similarity
    return name_sum, non_name_sum


def get_forename_similarity(herd, records, method, name_type):
    first_forename, first_freq = \
        extract_forename_similarity_info(herd, records[0], name_type)
    second_forename, second_freq = \
        extract_forename_similarity_info(herd, records[1], name_type)
    prop_freq = max(first_freq, second_freq, 1.0 / 1000)
    cutoff = 5.0 / 26  # arbitrary, could be improved
    F = 3 if prop_freq > cutoff else 12
    difference = damerau_levenshtein(first_forename, second_forename)
    max_length = max(len(first_forename), len(second_forename))
    prop_diff = float(difference) / max_length
    # map prop_diff from (0, 1) to (-2, 2), then flip sign since lower diff
    # implies that the two name are more similar.
    weight = -(4 * prop_diff - 2)
    return weight * F


def extract_forename_similarity_info(herd, record, name_type):
    profile = record.profile
    # Add try/except
    if name_type == "fore":
        forename = profile.forename
        weight = herd._forename_freq_dict[record._meta.forename_freq_ref] / \
            float(sum(herd._forename_freq_dict.values()))
    elif name_type == "mid_fore":
        forename = profile.mid_forename
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
    second_surname = [
        extract_surname_similarity_info(herd, records[1], name)[0]
        for name in name_types
        ]
    second_freq = [
        extract_surname_similarity_info(herd, records[1], name)[1]
        for name in name_types
        ]
    # Get difference between first record name and both second record names,
    # then find the one that has the minimum difference and keep that one
    diffs = [method(first_surname, name) for name in second_surname]
    difference = min(diffs)
    min_index = diffs.index(min(diffs))
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
    return weight * S


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
        surname = profile.birth_surname
        weight = herd._surname_freq_dict[record._meta.birth_surname_freq_ref]\
            / float(sum(herd._surname_freq_dict.values()))
    elif name_type == "current":
        surname = profile.current_surname
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
    # ox-link only takes first 8 characters and greps for things like "flat"
    first_profile = records[0].profile
    second_profile = records[1].profile
    first_address = [first_profile.address1, first_profile.address2]
    second_address = [second_profile.address1, second_profile.address2]
    diff1 = method(first_address[0], second_address[0])
    diff2 = method(first_address[1], second_address[1])
    if diff1 == 0:
        if diff2 == 0:
            return 7
        else:
            return 2
    else:
        return 0
    # ox-link method
    # return 7 if diff1 == 0 else 0


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
    first_sex = str(first_profile.sex)  # must be a string
    second_sex = str(second_profile.sex)  # must be a string
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
    year_diff = method(first_dob[0], second_dob[0])
    month_diff = method(first_dob[1], second_dob[1])
    month_length = max(len(first_dob[1]), len(second_dob[1]))
    day_diff = method(first_dob[2], second_dob[2])
    # could add more complexity here based off of ox-link
    year_prop = 0.5  # slightly arbitrary choice because year means more
    month_prop = 0.25
    day_prop = 0.25
    prop_diff = year_prop * (year_diff / 4.0) + \
        month_prop * (month_diff / float(month_length)) + \
        day_prop * (day_diff / 2.0)
    # map prop_diff from (0, 1) to (-23, 14), then flip sign since lower diff
    # implies that the two name are more similar.
    return -(37 * prop_diff - 14)


def extract_surname_similarity_info(herd, record, type):
    profile = record.profile
    # Add try/except
    if name_type == "birth":
        surname = profile.birth_surname
        weight = herd._surname_freq_dict[record._meta.birth_surname_freq_ref]\
            / float(sum(herd._surname_freq_dict.values()))
    elif name_type == "current":
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
    diff2 = damerau_levenshtein(first_address[1], second_address[1])
    if diff1 == 0:
        if diff2 == 0:
            return 7
        else:
            return 2
    else:
        return 0
    # ox-link method
    # return 7 if diff1 == 0 else 0


def get_post_code_similarity(records):
    first_profile = records[0].profile
    second_profile = records[1].profile
    first_post_code = str(first_profile.postal_code)  # must be a string
    second_post_code = str(second_profile.postal_code)  # must be a string
    difference = damerau_levenshtein(first_post_code, second_post_code)
    if difference == 0:
        return 4
    elif difference == 1:  # for transposition, ox-link does not do this
        return 1
    else:
        return 0
    # ox-link method
    # return 4 if difference == 0 else 0


def get_sex_similarity(records):
    first_profile = records[0].profile
    second_profile = records[1].profile
    first_sex = first_profile.sex
    second_sex = second_profile.sex
    return -1 if first_sex == second_sex else -10


def get_dob_similarity(records):
    first_profile = records[0].profile
    second_profile = records[1].profile
    first_dob = str(first_profile.birth_year), \
        str(first_profile.birth_month), \
        str(first_profile.birth_day)
    second_dob = str(second_profile.birth_year), \
        str(second_profile.birth_month), \
        str(second_profile.birth_day)
    year_diff = damerau_levenshtein(first_dob[0], second_dob[0])
    month_diff = damerau_levenshtein(first_dob[1], second_dob[1])
    month_length = max(len(first_dob[1]), len(second_dob[1]))
    day_diff = damerau_levenshtein(first_dob[2], second_dob[2])
    # could add more complexity here based off of ox-link
    year_prop = 0.5  # slightly arbitrary choice because year means more
    month_prop = 0.25
    day_prop = 0.25
    prop_diff = year_prop * (year_diff / 4.0) + \
        month_prop * (month_diff / float(month_length)) + \
        day_prop * (day_diff / 2.0)
    return -(37 * prop_diff - 14)


