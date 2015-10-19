"""A helper module to generate fake records for testing.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
import re
import json
import argparse
import random
from faker import Faker

fake = Faker()

# Parse arguments
argparser = argparse.ArgumentParser()
argparser.add_argument("f", metavar="filename",
   help="JSON filename (file automatically saved to test dir)")
argparser.add_argument("--N", metavar="num_records",
   help="number of records to create",
   default=100)
argparser.add_argument("--overwrite", required=False,
   metavar="True/False", help="overwrite existing files (True/False)",
   default='True')
argparser.add_argument("--start_date", required=False,
   metavar="START_DATE",
   help="earliest year for birthdate (+/-<number of years>y)",
   default="-99y")
argparser.add_argument("--end_date", required=False,
   metavar="END_DATE", help="latest year for birthdate",
   default="-1y")
args = argparser.parse_args()


def create_population(N, start_date, end_date):
    """Creates a fake population.

    A population consists of N profiles of various individuals, where each
    profile includes at least a name, address, and SSN. Herd generation is not
    100% reproducible, so each new population will essentially be random.

    Args:
        N (int): Number of profiles to create.
        start_date (str): Earliest date to use for birthdate. In the form of
            ``+/-<number of years>y``.
        end_date (str): Latest date to use for birthdate, in the same format
            as ``start_date``.

    Returns:
        tuple: A tuple of dictionaries, each representing an individual profile,
        sorted by profile name.
    """
    profile_fields = ['address', 'ssn', 'blood_group']
    population = [fake.profile(fields=profile_fields) for i in range(N)]
    gender_change = {'M': 'F', 'F': 'M'}
    for i in range(N):
        record = population[i]
        # Birthdate
        birthdate = fake.date_time_between(start_date="-99y", end_date="-1y")
        record['birthdate'] = birthdate.strftime("%Y-%m-%d")
        # Name, Sex, and Gender
        record['sex'] = 'F' if random.random() <= 0.60 else 'M'
        has_middle_name = True if random.random() <= 0.50 else False
        is_married = True if random.random() <= 0.49 else False
        sex = record['sex']
        if sex == 'F':
            record['forename'] = fake.first_name_female()
            if has_middle_name:
                record['mid_forename'] = fake.last_name()
            record['current_surname'] = fake.last_name()
            if is_married:
                record['birth_surname'] = fake.last_name_female()
        else:
            record['forename'] = fake.first_name_male()
            record['mid_forename'] = fake.last_name() if has_middle_name else ''
            record['current_surname'] = fake.last_name_male()
        record['gender'] = gender_change[sex] if random.random() < 0.05 else sex
        # Do some manipulation of keys to match expected Profile fields
        address = record.pop('address')
        address = re.split('[\n,]', address)
        record['state_province'] = next(s for s in address[-1].split(' ') if s)
        record['postal_code'] = address[-1].split(' ')[-1]
        record['city'] = address[1]
        record['address1'] = address[0]  # First consider address to be one field
        # But then try to split address into two fields and overwrite the field
        # if necessary.
        delimiters = ['Suite', 'Ste', 'Unit', 'Apartment', 'Apt', 'Department',
                      'Dpt']
        for delimiter in delimiters:
            split_address = address[0].split(delimiter)
            if len(split_address) > 1:
                record['address1'] = split_address[0].rstrip()
                record['address2'] = delimiter + split_address[1]
        # Fix SSN key to match Profile fields
        ssn = record.pop('ssn')
        record['national_id1'] = ssn
        # Split birthdate to match Profile fields
        birthdate = record.pop('birthdate')
        birthdate = birthdate.split('-')
        record['birth_year'] = birthdate[0]
        record['birth_month'] = birthdate[1]
        record['birth_day'] = birthdate[2]
        # Fix 0+/- blood type to be O+/-
        blood = record.pop('blood_group')
        record['blood_type'] = blood.replace('0', 'O')
    return tuple(sorted(population, key=lambda profile: profile['forename']))


if __name__ == '__main__':
    # Abort if file exists and overwrite is False
    this_dir = os.path.dirname(os.path.realpath(__file__))
    if args.f in os.listdir(this_dir) and args.overwrite != 'True':
        print("Filename exists...aborting.")
    elif args.f not in os.listdir(this_dir) or args.overwrite == 'True':
        # Generate records
        records = create_population(int(args.N), args.start_date, args.end_date)
        # Write records
        filepath = os.path.join(this_dir, args.f)
        with open(filepath, 'w+') as data_file:
            json.dump(records, data_file)
        # Confirm success
        print("Data written to {}".format(filepath))



