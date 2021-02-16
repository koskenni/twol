
.. _raw2named:

twol\.raw2named module
======================

.. automodule:: twol.raw2named
    :members:
    :undoc-members:
    :show-inheritance:

See :ref:`representations` to see how the program is used in conjunction with other twol utility programs.

The program gives a help message::

  $ twol-raw2named -h
  usage: python3 raw2named.py [-h] [-d DELIMITER] [-n NAME_SEPARATOR]
                              [-F] [-v VERBOSITY]
			      input output names

  Renames raw morphophonemes. Version 2020-02-20

  positional arguments:
    input                 aligned examples as a CSV file
    output                renamed examples as a space separated pair
                          symbol strings
    names                 mapping from raw to neat morphophonemes as
                          a CSV file, default is ','

  optional arguments:
    -h, --help            show this help message and exit
    -d DELIMITER, --delimiter DELIMITER
			  delimiter between raw name and new name
			  fields, default is ','
    -n NAME_SEPARATOR, --name-separator NAME_SEPARATOR
			  Separator between morpheme names in the
			  morpheme list, default is '.'
    -F, --add-features    add affix morpheme names to the pairstring
			  representation
    -v VERBOSITY, --verbosity VERBOSITY
			  level of diagnostic and debugging output
