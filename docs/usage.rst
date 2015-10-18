=====
Usage
=====

To use EHRcorral in a project::

    import ehrcorral

EHRCorral operates on a collection of Records, each of which represents a single
electronic health record. A collection of records is called a Herd, hence the
name EHRCorral: generating a master patient index (MPI) of all the records is
done by "corraling" the Herd.

There is a small number of actions to perform, but potentially several setting
to consider.

   1. Create records
   2. Create a herd
   3. Populate the herd with the records
   4. Corral the herd

Records
-------

See: :py:class:`ehrcorral.herd.Record`

A Record is a simplified representation of a patient's EHR which only contains
information relevant to the current matching algorithm. Each Record must*
contain a forename (first name) and a current surname (last name), but can also
contain other identifying information if it is supplied. All the information in
a Record can be used to discover other Records that describe the same
individual.::

    from ehrcorral.herd import Record
    records = (
        Record(forename='John',
               mid_forename='',
               current_surname='Doe',
               suffix='Sr.',
               address='1 Denny Way\nOrlando, FL 32801',
               sex='M',
               gender='M',
               ssn='123-45-678',
               birthdate='04-08-1985',
               blood_type='B+'),
        Record(first_name='Jane',
               middle_name='Erin',
               birth_surname='Doe',
               current_surname='Fonda',
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



