# Create mophophonemic representations out of a table of inflected forms

This directory contains test cases for the programs:

a. twol-table2words

b. twol-words2zerofilled

c. twol-zerofilled2raw

d. twol-raw2renamed


Three sets of test data are provided:

1. *demo* -- a very small set of Finnish inflected words.

2. *kskn* -- a coimprehensive set of Finnish noun inflection as
   described in *Nykysuomen sanakirja* and *Suomen kielen
   Käänteissanakirja*

3. *kskv* -- a coimprehensive set of Finnish verb inflection as
   described in *Nykysuomen sanakirja* and *Suomen kielen
   Käänteissanakirja*

Ech test data sets consist of:

* ``xxx-table.csv``: A table of the inflected forms given as a CSV
  (comma separated values) file.  Each line in the table represents
  one lexeme and each column an inflectional form.  The first column
  is the label used for identifying the lexeme and the top line for
  identifying the forms.  The word forms in the cells must contain
  morph separators which mark the boundaries between stems and endings
  and affixes.  The column labels indicate what inflectional morphemes
  are present in word forms given in that column.  Note that there may
  be several endings or no edings at all in the word forms, but in
  each column the number must be the same.  One can use a spreadsheet
  program to produce such files by storing the table in CSV format.
  See more details of the format of the table in the actual
  documentation at:
  https://pytwolc.readthedocs.io/en/latest/morphophon.html

* ``xxx-affixes.csv``: A small CSV file which indicates which columns
  of the table we wish to include in the processing and what would be
  the morphophonemic representations of the affixes involved.  See the
  same documentation as above.

* ``xxx-newnames.csv``: A CSV file which contains cleaner and more
  readable names for some raw morphophonemes.  This file can initially
  be almost empty but it can be incrementally.  The first column gives
  the raw morpophoneme name as given by twol-zerofilled2raw and the
  second column gives the new cleaner name.  If the second column is
  empty, that raw name is kept.


## Makefile

Most tests can be performed through a ``make`` command which uses the
``Makefile`` present in this directory.  Plain ``make`` will do the
tests for the demo test set.  The ``make`` command will produce:

* ``demo-words.csv`` out of ``demo-table.csv`` by using
  ``twol-table2words`` command,

* ``demo-zerofilled.csv`` out of ``demo-words.csv``,
  ``demo-affixes.csv`` and ``alphabet.text`` by using
  ``twol-words2zerofilled`` command,

* ``demo-raw.csv`` out of ``demo-zerofilled.csv`` by using
  ``twol-zerofilled2raw`` command and

* ``demo-renamed.pstr`` out of ``demo-raw.csv`` and ``demo-newnames``
  by using ``twol-raw2renamed`` command.

One can compare the produced files to which are stored in the github
twol project.  Those files hava a ``-orig`` part added near the end of
the file name, e.g. ``demo-raw-orig.csv``.

Other testsets can be executed by giving a parameter to the command,
e.g.:

   $ make BASE=kskn

If one needs to redo the make, one can clean the generated files by a
command, e.g.:

   $ make BASE=kskn clean



## DEMO


2. ``demo-affixes.csv`` is a small file which determines two things:

    a. Firstly, it tells which columns (or forms) are actually taken
       for the process.  Often the table contains more forms than we
       actually need.  The initial four lines in the CSV table
       identify each one column in ``demo-table.csv``.  Such lines
       contain a ``+`` sign in the second column.  b. Secondly, the
       table gives the morphophonemic forms of the inflectional
       morphemes present in the selected columns.  E.g. the plural
       might occur in several columns.  The morphophonemes are
       enclosed in braces (e.g. ``{aä}``).  The program could align
       the endings but that is done manually this way because of
       practical reasons.

This small table is needed for the producing the raw morphophonemic
representations for the word forms in the original table.



## KSKN and KSKV

These two are full-scale inflectional paradigms of Finnish nouns and
verbs.  The describe the stem internal and stem final phonemic
alternations in a comprehensive manner.  The tables of inflectional
forms can be transformed into a set of example words in a format
required by the Python implementation of the two-level rule compiler.