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

Ref: :py:class:`ehrcorral.ehrcorral.Record`

A Record is a simplified representation of a patient's EHR which only contains
information relevant to the current matching algorithm. Each Record *must*
contain a forename and a current surname, but it can also house other
identifying information. All the information in a Record is used to discover
other Records that describe the same individual.

.. code-block:: python

    ehr_entries = [
        first = {
            'forename': 'John',
            'mid_forename': '',
            'current_surname': 'Doe',
            'suffix': 'Sr.',
            'address': '1 Denny Way\nOrlando, FL 32801',
            'sex': 'M',
            'gender': 'M',
            'ssn': '123-45-678',
            'birthdate': '04-08-1985',
            'blood_type': 'B+'
        }
        second = {
            'first_name': 'Jane',
            'middle_name': 'Erin',
            'birth_surname': 'Doe',
            'current_surname': 'Fonda',
            'suffix': '',
            'address': '1 Bipinbop St\nAustin, TX 73301',
            'sex': 'F',
            'gender': 'F',
            'ssn': '876-54-321',
            'birthdate': '01-14-1976',
            'blood_type': 'A-'),
        }
    ]
    records = [ehrcorral.gen_record(entry) for entry in ehr_entries]

Above, we create two Records (an entry for John and one for Jane) using the
function :py:func:`ehrcorral.ehrcorral.gen_record`. Generally, you will not
need to interact directly with the Records once they are created.

In practicality, you won't have just two EHR entries, but hundreds or millions
of them, and there might be multiple entries for John or Jane and many other
individuals in the sub-population. Records are designed to be extremely light on
memory usage, much more so than a dictionary or list, for example. Therefore,
when generating Records it is advisable *not* to build up a large dictionary of
data to then be sent to :py:func:`ehrcorral.ehrcorral.gen_record`. Instead,
generate the Records in a loop that operates on a single EHR entry at a time
so the dictionaries like the ones above are thrown away once the Record is
created.

.. code-block:: python

    records = []
    for data in raw_ehr_data:
        # Extract forenames, surnames, birth dates, sex, etc. from your
        # raw EHR data into a dictionary named 'entry'.
        # ...
        # entry =  {'forename': 'John', ... , 'blood_type': 'B+'}
        records.append(ehrcorral.gen_record(entry)

For the full list of fields available to generate a Record, see
:py:class:`ehrcorral.ehrcorral.Profile`.

You have four name fields available to you: `first_name`, `middle_name`,
`last_name`, and `suffix`. How you define them is entirely up to you. There
is no special transformations that get applied (WHAT ABOUT CONVERTING TO
UNICODE OR REMOVING SPECIAL CHARACATERS - MAYBE MAKE THAT A FLAG) and they
are first matched phonetically and then evaluated for similarity - each field
is matched the same way. DON'T YOU WANT ONLY A SINGLE NAME (i.e. NO SPACES)
IN EACH ONE? If you want to leave the middle name field blank, that is fine.
However you define each field is entirely up to you.

Create and Populating a Herd
----------------------------

You can create and populate a herd at
the same time, or create it and then populate it.::

    from ehrcorral.herd import Herd

    # Create and populate at the same time
    herd = Herd(population=records)

    # Create then populate
    herd = Herd()
    herd.populatiion = records

Move a Herd
-----------



