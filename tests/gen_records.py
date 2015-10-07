"""A helper module to generate fake records for testing.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
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
    profile_fields = ['name', 'address', 'ssn', 'blood_group', 'sex']
    population = [fake.profile(fields=profile_fields) for i in range(N)]
    gender_change = {'M': 'F', 'F': 'M'}
    for i in range(N):
        record = population[i]
        # Birthdate
        birthdate = fake.date_time_between(start_date="-99y", end_date="-1y")
        record['birthdate'] = birthdate.strftime("%Y-%m-%d")
        # Gender
        sex = record['sex']
        record['gender'] = gender_change[sex] if random.random() < 0.05 else sex
    return tuple(sorted(population, key=lambda profile: profile['name']))


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



