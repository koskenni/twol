twol\.alphabet module
=====================

Phonemes are defined according to what features they have.  Features are divided into six groups or positions so that each feature name belongs to exactly one position.  One the first three groups characterize consonants and the last three groups characterize vowels.  Consonants typically have one feature in each of their first three positions and and the last three positions are empty.  A consonant ``t`` could be described e.g. as::

  "t": ("Dental", "Unvoiced", "Stop", "", "", "")

In ``features_of_phoneme`` dict the phonemes are represented in this way after the alphabet has been processed.  Similarly, vowels have their first three slots empty and the three last positions filled with vocalic features, e.g. the phonemes ``i`` and ``u`` could be represented as::

  "i": ("", "", "", "Close", "Front", "Unrounded")
  "u": ("", "", "", "Close", "Back", "Rounded")

We represent semivowels or approximants by giving them features in all six positions, e.g. Finnish and Estonian ``j`` could be::

  "j": ("Palatal","Voiced","Approximant",
        "SemiVowel","Front","Unrounded")

The ``Ø`` which will be inserted in the words during the course of alignment is represented as::

  "Ø": ("Zero", "Zero", "Zero", "Zero", "Zero", "Zero")


Representing phonemes and morphophonemes with sets
--------------------------------------------------

Another, equivalent, *set representation* for phonemes is useful for defining the *compatibility* of pairs of phonemes and sets of phonemes.  Individual features are replaced by sets and the empty position by a universal set ``U``, e.g. for ``t``, ``ì``, ``u`` and ``j``::

  "t": ({"Dental"}, {"Unvoiced"}, {"Stop"}, U, U, U)
  "i"; (U, U, U, {"Close"}, {"Front"}, {"Unrounded"})
  "u": (U, U, U, {"Close"}, {"Back"}, {"Rounded"})
  "j": ({"Palatal"}, {"Voiced"}, {"Approximant"},
        {"SemiVowel"}, {"Front"}, {"Unrounded"})

We define a *(raw) morphophoneme* to be either a single phoneme (e.g. ``i``) or a combination of a (raw) morphophoneme and a single phoneme (e.g. ``iu``).  The set representation of the combination is the six-tuple of unions of their sets, e.g.::

  "iu": (U, U, U, {"Close"}, {"Front", "Back"},
        {"Rounded", "Unrounded"})
  "ij": (U, U, U, {"Close", "Semivowel"}, {"Front"}, {"Unrounded"})
  "ti": (U, U, U, U, U, U)

The tuple with six universal sets is *not valid* by definition, i.e. such morphophonemes are not established.  The universal set ``U`` is defined to include not only the existing features in a position but at least some other non-existing features as well so that the union with ``U`` always is a superset of sets of actually used feature.  Thus, e.g. the morphophoneme consisting of all vowels is not confused with ``U``.


Binary representation of sets of features
-----------------------------------------

For each of the six positions, there is a small finite set of possible features.  We assume that there are never more than 16 different features (including "Zero") for any positionThe program finds them and gives a numeric value for each.  The "Zero" feature is always value 0, and the rest are given values 1, 2, 4, 8, 16, 32, ...  Each phoneme gets a representation of six integers which are powers of 2.  The set ``U`` would be ``{1, 2, 4, 8, 16, ..., 2*15}``

For each of the six positions we now have an integer which corresponds to the set of features as discussed above.  Union of two sets corresponds to the *or* (``|``) of these binary integers. Combining a morphophoneme and a phoneme reduces now to the or (``|``) of the six corresponding binary integers.

We have six 16 bit integers.  They can be represented as a single Python integer which contains (at least) 96 bits.  Hereafter we can represent any phoneme and any sets of phonemes by a single integer.  Furthermore we can combine them with an elementary Python (``|``) operation.  The result is invalid if it consists of 96 bits one i.e. is equal to 0xffffffffffffffffffffffff and this integer value represens ``U``.

.. automodule:: twol.alphabet
    :members:
    :undoc-members:
    :show-inheritance:
