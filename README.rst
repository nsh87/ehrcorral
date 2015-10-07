===============================
EHRcorral
===============================

.. image:: https://img.shields.io/travis/nsh87/ehrcorral.svg
        :target: https://travis-ci.org/nsh87/ehrcorral

.. image:: https://img.shields.io/pypi/v/ehrcorral.svg
        :target: https://pypi.python.org/pypi/ehrcorral


EHRcorral cross-matches and links electronic medical records for the
purpose of de-duplication

* Free software: ISC license
* Documentation: https://ehrcorral.readthedocs.org.

Features
--------

* TODO

Usage
-----

EHRcorral calls a collection of Records a "herd"  - think of it like a
herd of sheep. There are some core tasks that you want to perform:

    1. Create a herd
    2. Populate a herd
    3. Move a herd
    4. Corral a herd

These tasks are explained below.

Record Class
^^^^^^^^^^^^

The :py:class:`ehrcorral.herd.Record` is the main component of your herd. Each
record contains some identifying information (e.g. name, address, etc.) from an
EHR that can be used to discover other records that describing the same
individual. If you imagine a traditional herd as being a collection of sheep,
here your herd is a collection of Records.::

    from ehrcorral.herd import Record
    records = (
        Record(first_name='John',
               middle_name='',
               last_name='Doe',
               suffix='',
               address='1 Denny Way\nOrlando, FL 32801',
               sex='M',
               gender='M',
               ssn='123-45-678',
               birthdate='04-08-1985',
               blood_type='B+'),
        Record(first_name='Jane',
               middle_name='',
               last_name='Doe',
               suffix='',
               address='1 Bipinbop St\nAustin, TX 73301',
               sex='F',
               gender='F',
               ssn='876-54-321',
               birthdate='01-14-1976',
               blood_type='A-'),
    )
    
Above, we have defined a tuple of Records. In general, the population of
your herd should not change, so a tuple is desirable.

You have four name fields available to you: `first_name`, `middle_name`,
`last_name`, and `suffix`. How you define them is entirely up to you. There
is no special transformations that get applied (WHAT ABOUT CONVERTING TO
UNICODE OR REMOVING SPECIAL CHARACATERS - MAYBE MAKE THAT A FLAG) and they
are first matched phonetically and then evaluated for similarity - each field
is matched the same way. DON'T YOU WANT ONLY A SINGLE NAME (i.e. NO SPACES)
IN EACH ONE? If you want to leave the middle name field blank, that is fine.
However you define each field is entirely up to you.

Create and Populating a Herd
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can create and populate a herd at
the same time, or create it and then populate it.::

    from ehrcorral.herd import Herd

    # Create and populate at the same time
    herd = Herd(population=records)

    # Create then populate
    herd = Herd()
    herd.populatiion = records

Move a Herd
^^^^^^^^^^^


