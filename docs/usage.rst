=====
Usage
=====

To use EHRcorral in a project::

    import ehrcorral

EHRCorral operates on a collection of Records, each of which represents a single
electronic health record. A collection of Records is called a Herd, hence the
name EHRCorral: generating a master patient index of all the records is
done by "corraling" the Herd.

There is a small number of actions to perform, but potentially several setting
to consider:

   1. Create Records
   2. Create a Herd
   3. Populate the Herd with the Records
   4. Corral the Herd

Records
-------

**Ref:** :py:class:`ehrcorral.ehrcorral.Record`

A Record is a simplified representation of a patient's EHR which only contains
information relevant to the current matching algorithm. Each Record *must*
contain a forename and a current surname, but it can also house other
identifying information. All the information in a Record is used to discover
other Records that describe the same individual.

.. code-block:: python

    ehr_entries = [
        first_entry = {
            'forename': 'John',
            'mid_forename': '',
            'current_surname': 'Doe',
            'suffix': 'Sr.',
            'address1': '1 Denny Way',
            'city': 'Orlando',
            'state_province': 'FL'
            'postal_code': 32801,
            'sex': 'M',
            'gender': 'M',
            'national_id1': '123-45-678',  # Using field as social security num
            'id2': 'F1234578',  # Optional ID, such as driver license num
            'birth_year': '1985',
            'birth_month': '08',
            'birth_day': '04',
            'blood_type': 'B+'
        }
        second_entry = {
            'first_name': 'Jane',
            'middle_name': 'Erin',
            'birth_surname': 'Doe',
            'current_surname': 'Fonda',
            'suffix': '',
            'address1': '1 Bipinbop St'
            'address2': 'Apt. 100',
            'city': 'Austin',
            'state_province': 'TX',
            'postal_code': 73301,
            'sex': 'F',
            'gender': 'F',
            'national_id1': '876-54-321',
            'birth_year': 1976,
            'birth_month': '08',  # Numeric fields are coerced to proper type
            'birth_day': 01,
            'blood_type': 'A-'),
        }
    ]
    records = [ehrcorral.gen_record(entry) for entry in ehr_entries]

Above, we create two Records (an entry for John and one for Jane) using the
function :py:func:`ehrcorral.ehrcorral.gen_record`. Generally, you will not
need to interact directly with the Records once they are created.

In practicality, you won't have just two EHR entries, but thousands or millions
of them, and there might be multiple entries for John or Jane and many other
individuals in the sub-population. The Record class is designed to be extremely
light on memory usage, much more so than a dictionary or list, for example. A
collection of 10 million Records will occupy about 5---6 GB, whereas 10 million
dictionaries containing the same data will occupy about three times the memory.
Therefore, when generating Records it is advisable *not* to build up a large
dictionary of data to then be sent one by one to
:py:func:`ehrcorral.ehrcorral.gen_record`. Instead, generate the Records in a
loop that operates only on a single EHR entry at a time so the dictionaries like
the ones above are thrown away once the Record is created:

.. code-block:: python

    records = []
    for entries in ehr:
        # Extract forenames, sex, etc. from EHR data into dict called 'entry'
        # ...
        # entry =  {'forename': 'John', ... , 'blood_type': 'B+'}
        records.append(ehrcorral.gen_record(entry)

Record Fields
-------------

For the full list of fields available to generate a Record, see
:py:class:`ehrcorral.ehrcorral.Profile`.

If additional fields are passed to ``gen_record()`` they are ignored.
Missing fields receive a value of empty string. No transformations are applied
to these fields other than to coerce strings to integers when the algorithm
requires integers. You should perform any pre-processing that you think is
relevant for your region or data set, such as removing accents or umlauts if you
do not want to match based on such special characters, defining forename and
mid forename if names if your region are particularly long, removing prefixes
like Mr. and Mrs., and determining what to use for the national ID field.

Creating a Herd
---------------

**Ref:** :py:class:`ehrcorral.ehrcorral.Herd`

Once the Records have been created, you can populate a Herd. A list or tuple
of Records can be used.

.. code-block:: python

    herd = ehrcorral.Herd()
    herd.populate(records)

Once a Herd has been populated the sub-population cannot be updated. Calling
``populate()`` again with additional records will raise an error. Making the
population immutable prevents race conditions during matching.
