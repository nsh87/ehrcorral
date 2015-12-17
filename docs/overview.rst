========
Overview
========

Significant effort has been put into developing record-linkage algorithms
using deterministic, probabilistic, or machine learning methods, or
a combination of approaches [#current_practice]_ [#state_of_linkage]_
[#final_report]_. EHRCorral takes a probabilistic approach, wherein certain
fields are weighted based on their match-level, which is determined using
numerical or lexical analysis in the context of two records or the entire set
of records. A composite probability of two records matching is calculated and
if the probability is above a threshold value the records are linked. Several
pre-processing steps are often taken to reduce the computational requirements
and attempt to increase the sensitivity and specificity of the algorithm.

Precedents
----------

Purely deterministic models, which attempt to find identical values in
certain fields, are unideal for many healthcare data sets
[#deterministic_vs_probabilistic]_. Keying errors, misspellings, and
transpositions of first name and last name are all too common in EHRs
[#integrity_patient_data]_ [#data_accuracy]_, and some institutions are only
able to record minimal identifying information about patients, such as is
often the case with transient, homeless, and under-served populations. This
makes it difficult to identify a field or fields which can reliably be
matched exactly across records.

Machine learning algorithms, such as neural networks, can be used for
matching, with pros and cons compared to other approaches
[#matching_records_nmpi]_. However, while machine learning is becoming more
common in many fields as computational units become cheaper, most of these
algorithms require some method of training in order to identify a "pattern"
and develop a specific algorithm to be applied on future records for linkage.
This training might entail feeding in a large data set where record links
have already been identified, or training the algorithm as it is developed.

A probabilistic method can run immediately on a data set without training
data and identify record linkages with surprising sensitivity and specificity
when the right settings are used. The OX-LINK system, which was developed to
match 58 million healthcare records spanning from the 1960s to the '90s,
achieved a false positive rate of 0.20%---0.30% and a false negative rate
from 1.0%---3.0% on several hundred thousand records [#ox_link]_. This system
uses a combination of probabilistic, weighted matching, lexical analysis,
phonemic blocking, and manual review. Recent publications also suggest that
high sensitivity can be achieved with probabilistic methods, even in the
context of error-prone data.

The approach taken here is influenced in large part by the methods of OX-LINK.
Subsequent improvements to such probabilistic techniques have been incorporated,
as well.

Phonemic Tokenization
---------------------

Phonemic name compression, indexing, or tokenization schemes use phonetics to
approximately represent a word or name. There are several common name
compression schemes in wide use, including Soundex, NYSIIS, metaphone, and
double metaphone, which appear here in chronological order according to their
date of creation
[#record_linkage_proceedings]_ [#algorithm_variable_compression]_. The purpose
of name compression in record linkage is to allow for a potential name match
when the spelling of two names disagree but the phonetics are identical. For
example, the Soundex code for Catie and Caity are both **C300**, although
their spelling is different.

Soundex is the oldest method here, developed in the early 1900s and used to
aid the U.S.A. Census Bureau [#phonetic_matching]_. It is computationally
efficient and included in several modern databases for fuzzy name matching
for that reason, but its shortcomings are quite obvious when non-Anglo-Saxan
names are used and in other scenarios. Continuing the example in the previous
paragraph, the Soundex code for Katie is **K300**, although it sounds
identical to both Catie and Caity, which both have the code **C300**. After
stripping vowels and other characters in certain situations, Soundex only
looks at the initial part of a name.

NYSIIS was developed in the 1970s and is used by the New York State Department
of Health and Criminal Justice Services. Unlike Soundex, vowels are not dropped
and codes are not truncated to just four characters. For example, the NYSIIS
encoding of Jonathan is **JANATAN**. This characteristic leads to improvements
in a number of areas, and the algorithm is purported to better handle phonemes
that occur in Hispanic and some European names. The NYSIIS codes for Catie,
Caity, and Katie are all **CATY**. The improvement can be seen here since NYSIIS
correctly identifies the same code for these phonetically identical names.

Metaphone, and then double metaphone, are the most recent phonemic
compressions available in EHRCorral [#metaphone]_ [#double_metaphone]_.
Metaphone was first published in 1990 and is the first algorithm here to
consider the sequences of letters and sounds rather than just individual
characters. It also performs its compression based on the entire name, not
a truncated or stripped version. Double metaphone was released ten years
after metaphone, and particularly turns its attention toward accounting for
combinations of sounds that are not present in the english language. This
makes double metaphone suitable for compression of english or anglicized
names of a variety of origins, including Chinese, European, Spanish, Greek,
French, Italian, and more. It is the most robust algorithm not only for that
reason, but also because it produces two encodings per name: a primary
encoding and a secondary encoding. The metaphone codes for Catie, Caity, and
Katie are all **KT**. Double metaphone produces just one encoding (again,
**KT**) and drops the secondary encoding since this is a phonetically simple
name. If we consider the name Katherine, metaphone produces **KORN** while
double metaphone generates two encodings, **KORN, KTRN**.

Phonemic compressions have been widely used to quickly identify similar names
for record linkage. They can quickly identify similar names and exclude
dissimilar ones, reducing the time to find matches, and they can improve false
positive/negative rates by eliminating unnecessary matches. They are important
to understand in the context of `Record Blocking`_.

.. _record-blocking-label:

Record Blocking
---------------

Record blocking is a technique used to eliminate probabilistic matching
between records that clearly do not match based on some field, such as last
name [#blocking_considerations]_ [#practical_introduction]_. If every record
has to be checked against every other record for a probabilistic match there
are :math:`{n \choose 2}` checks that must occur. For n=1,000,000 records,
this would require 499,999,500,000 (499 trillion) record-to-record
comparisons. If every comparison takes just 1 microsecond, it would still
take over 5 days for the matching process to complete. However, if we were
able to limit record-to-record comparisons to groups (i.e. blocks) of records
that have the possibility of matching and ignore other record-to-record
combinations, the time to completion could be greatly reduced.

By default, EHRCorral blocks data into groups by the phonemic compression of the
current surname plus the first initial of the forename. Other blocking
techniques group by phonemic compression of the forename or current surname, or
by birth month or year. A combinatory approach can be taken, as well, blocking
by both current surname and birth year, and then by sex and birth month. By
probabilistically checking only records in the same block, the time until the
algorithm finishes is greatly reduced if the average block size is manageable.
Blocking by phonemic compression has the advantage of eliminating checks between
two names that have similar spelling but different pronunciations, potentially
eliminating false positives that might match based on word-distance measures
alone. On the other hand, if the phonemic compression algorithm is inaccurate
(as we saw with Caity and Katie using Soundex), potential matches are discarded,
increasing the false negative rate.

Soundex, NYSIIS, and metaphone all generate a single encoding, while the more
robust double metaphone generates two encodings. In the case of double metaphone
both encodings are used, effectively creating larger block sizes. This can lead
to a significant increase in computation time, depending on the data set.
Therefore, the first initial of the forename is also used to then decrease the
block size. This also helps reduce the size of blocks for very common surnames,
such as Smith, which occurs at a rate of about 1% (or 10,000 for every one
million) in the United States of America.

Exploding Data
--------------

Exploding the data set refers to the process of generating additional Records
from each Record by combining, switching, or expanding fields. The purpose of
exploding the data set is to mitigate the effect of certain data entry errors or
scenarios encountered in EHRs, such as the transposition of first name and
middle name, or the entry of a nickname in a name field. This process is used in
conjunction with blocking in order to increase the potential matches of a record
that might have these errors [#ox_link]_.

Consider a Record for a man named Bill Taft Robinson:

| **Forename:** Bill
| **Mid-forename:** Taft
| **Current surname:** Robinson

Initially, blocking would be performed by taking the phonemic compression of the
current surname plus the first initial of the forename. The primary double
metaphone compression of Robinson is **RPNSN**, and adding on the first initial
of the forename would put this record in block **RPNSNB**. When this record is
exploded, it will get the following additional blocking groups:

    * **RPNSNT**, using the first initial of the mid-forename
    * **RPNSNW**, using William in place of Bill for the forename since Bill
      is a common nickname for William in the english language.

This makes this Record available for probabilistic matching within three
blocking groups. Therefore, if Bill Taft Robinson has another Record under
William Taft Robinson, a potential match can be found with this Record. Note
that the blocking group is only used to determine which Records are checked. It
does not modify the forename, nor does it insert William in place of Bill.

A standard set of names and their nicknames is not yet included with
EHRCorral, but in the future one can be supplied to customize the explosion
to names from a different region. For example, instead of Bill and William,
when dealing with records containing Hispanic and Western European names
perhaps the European name Elizabeth should also be considered as Isabel, the
accepted Spanish version of Elizabeth, for blocking purposes.

Matching
--------

The matching that EHRCorral does is heavily based on the Oxford Record
Linkage System (OX-Link) [#ox_link]_.

Similarity Measures
^^^^^^^^^^^^^^^^^^^

Weighting
^^^^^^^^^

.. rubric:: References

.. [#current_practice] Gu, Lifang, et al. "Record linkage: Current practice
   and future directions." CSIRO Mathematical and Information Sciences Technical
   Report 3 (2003): 83.

.. [#state_of_linkage] Winkler, William E. "The state of record linkage and
   current research problems." Statistical Research Division, US Census Bureau.
   1999.

.. [#final_report] Morris, Genevieve et al. "Patient Identification And
   Matching Final Report". HealthIT.gov. N.p., 2014. Web. 17 Sept. 2015.

.. [#deterministic_vs_probabilistic] Zhu, Ying, et al. "When to conduct
   probabilistic linkage vs. deterministic linkage? A simulation study." Journal
   of Biomedical Informatics 56.C (2015): 80-86.

.. [#integrity_patient_data] Just, B. H., et al. "Managing the integrity of
   patient identity in health information exchange." Journal of AHIMA/American
   Health Information Management Association 80.7 (2009): 62-69.

.. [#data_accuracy] Hogan, William R., and Michael M. Wagner. "Accuracy of
   data in computer-based patient records." Journal of the American Medical
   Informatics Association 4.5 (1997): 342-355. institutions are only able to
   record minimal identifying information about

.. [#matching_records_nmpi] Bell, Glenn B., and Anil Sethi. "Matching records
   in a national medical patient index." Communications of the ACM 44.9 (2001):
   83-88.

.. [#ox_link] Gill, Leicester. "OX-LINK: the Oxford medical record linkage
   system." (1997).

.. [#record_linkage_proceedings] Alvey, W., and B. Jamerson. "Record Linkage
   Techniques—1997: Proceedings of an International Workshop and Exposition."
   Washington, DC: Federal Committee on Statistical Methodology (1997).

.. [#algorithm_variable_compression] Dolby, James L. "An algorithm for
   variable-length proper-name compression." Information Technology and
   Libraries 3.4 (2013): 257-275.

.. [#phonetic_matching] Beider, Alexander, and Stephen Morse. "Phonetic
   Matching: A Better Soundex". http://stevemorse.org. N.p., 2015. Web. 17 Oct.
   2015.

.. [#double_metaphone] Philips, Lawrence. "The double metaphone search
   algorithm." C/C++ users journal 18.6 (2000): 38-43.

.. [#metaphone] Lawrence, Philips. "Hanging on the metaphone." Computer
   Language 7.12 (1990): 39-43.

.. [#blocking_considerations] Kelley, Robert Patrick. Blocking considerations
   for record linkage under conditions of uncertainty. Bureau of the Census,
   1984.

.. [#practical_introduction] Clark, D. E. "Practical introduction to record
   linkage for injury research." Injury Prevention 10.3 (2004): 186-191.

