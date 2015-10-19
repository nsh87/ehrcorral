========
Overview
========

Significant effort has been put into developing record-linkage algorithms
using deterministic, probabilistic, machine learning methods, or a
combination of methods. EHRCorral takes a probabilistic approach, wherein
certain fields are weighted based on their match-level, which is determined
using numerical or lexical analysis. A final probability of two records
matching is calculated and if the probability is above a threshold value the
records are linked. Several pre-processing steps are often taken to reduce
the computational requirements and attempt to increase the sensitivity and
specificty of the algorithm.

Precedents
----------

Purely deterministic models, which attempt to find identical values in
certain fields, are unideal for many healthcare data sets. Keying errors,
transpositions (e.g. of first name and last name) are all too common in EHRs,
and some institutions are only able to record minimal identifying information
about patients, such as is often the case with transient, homeless, and
under-served populations. This makes it difficult to identify a field or
fields which can reliably be matched exactly across records.

Machine learning approaches have been tried in recent year with some success,
particularly with neural networks. However, while machine learning is
becoming more common and effective as computational power increases, most of
these algorithms require some method of training in order to identify a
"pattern" and train a specific algorithm to be applied on future datasets for
record linkage. This training might entail feeding in a large data set where
record links have already been identified, or training the algorithm as it is
developed.

A probabilistic method can run immediately on a data set without training data
and identify record linkages with surprising sensitivity and specificity when
the right settings are used. The OX-LINK system, which was developed to match
58 million records spanning from the 1960s to the '90s, achieved a false
positive rate of 0.20% - 0.30% and a false negative rate from 1.0% - 3 .0% on
several hundred thousand records. This system uses a combination of
probabilistic, weighted matching, lexical analysis, phonemic blocking, and
manual review.

The approach taken here is influenced in large part by the methods of OX-LINK
Subsequent improvements to such probabilitic techniques have been incorporated,
as well.

Phonemic Tokenization
---------------------

Exploding Data
--------------

Record Blocking
---------------

Matching
--------

Lexical Analysis
^^^^^^^^^^^^^^^^

Similarity Measures
^^^^^^^^^^^^^^^^^^^

Weighting
^^^^^^^^^
