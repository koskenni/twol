=============================================
Open Finnish two-level morphological analyzer
=============================================

This article describes a plan and a project *OFITWOL* to build an open source two-level morphological analyzer for Finnish as it is described in *Nykysuomen Sanakirja* [NS]_.  During the past decades, several morphological analyzers have been built for Finnish, including

* FINTWOL, originally in [koskenniemi1983]_ and later developed int a commercial product by Lingsoft
* MORFO developed by Kielikone
* Mint by Olli Blåberg and later on adopted by Xerox into the XFST framework
* OMORFI by Tommi Pirinen using the HFST tools
* Voikko based on the Malaga platform



Goals
=====

The goals of OFITWOL are:

1. OFITWOL aims to be *descriptive* rather than normative.  In particular, it is intended to accept inflectional word forms which were used in the 20th century but which are rarely used any more.  Most other Finnish morphological analyzers are more normative and try to allow only those forms which sound unmarked today.  The normative approach has also been the guideline for describing the inflection in more recent dictionaries such as *Kielitoimiston sanakirja* or its predecessor *Suomen kielen perussanakirja*.

2. The building of OFITWOL aims to demonstrate the application of the *simplified two-level model* into building a full-scale morphological analyzer in order to validate the principles and methods and to make it easier for other projects to learn from the expriences of this project.

3. OFITWOL aims to be *flexible* enough to be adapted for various purposes including the analysis of literary and newspaper texts from the 19th and 20th centuries, using it in the description of Finnsh dialects and in the comparison of Finnish with those, Old Literary Finnish and with languages closely related to Finnish.

4. Adopt disciplined methods for creating *lexical entries* either from word-lists such as Nykysyomen sanalista, interactively using a human informant or assisted by corpus data.

5. *Document* the various components well enough so that other scholars can understand how it is built and how it can be modified and improved.  As much as possible, the steps and components are documented prior to their building.

6. Make all rules, lexicons, scripts and programs freely available and extensible so that they can be used for any purpose.

   
Existing language resources
===========================

1. The tables for inflected word forms for paradigms given in *Nykysuomen sanakirja* [NS]_ and in *Suomen kielen käänteissanakirja* [KSK]_ which reflect the same sets of defined inflection classes.  These two are used as a primary resource when determining the morphophonemic shapes of lexical entries.

2. Nykysuomen sanalista [NSSL]_ which is a word list with inflectional coded and can be used under the LGPL license.  The inflection codes in NSSL are those used in Kielitoimiston sanakirja.

3. Suomen kielen tekstipankki, which is a collection of several million words of Finnish texts and is stored in the Kielipankki.  The texts themselves cannot be included in the results but they may be used as a primary resouce of occurrences of word forms and thus for determining the inflectional properties of tentative lexical entries.  Some proofread newspaper texts from early 1900s are also available.

4. Helsinki Finite-State Transducer Tools (HFST) for building the further tools needed at various stages of the project.  The finite-state tools are used both as standalone programs and as embedded in Python 3.

5. An initial version of nominal and verbal affixes as a CSV table which can be used for producing LEXC lexicons for affixes of Finnish.

6. Extensive list of word forms (KLK) from low quality OCR of huge amounts of Finnish texts from the 19th and 20th centuries.  (National Library of Finland (Kansalliskirjasto) (2014).  The Finnish N-grams 1820-2000 of the Newspaper and Periodical Corpus of the National Library of Finland [text corpus]. Kielipankki.  Retrieved from http://urn.fi/urn:nbn:fi:lb-2014073038)


Overview of the stages
======================

1. Completing the paradigm tables and sets of word form examples.  Word forms in the tables are segmented so that morphs are separated from each other by a boundary.  Establishing the morphophonemes through alignment as is explained in :ref:`representations`.  This is done separately for nouns, (adjectives) and for verbs.  The result of this stage is a collection of examples as space-separated pair symbol strings.  The result is free.  (Done for verbs and nouns by March 2019.)

2. Writing and testing the two-level rules as is explained in :ref:`discovery`, :ref:`formalism` and :ref:`compiling`.  The result of this stage is a two-level grammar which covers all relevant phoneme alternations of the language as they are present in the examples.  The result is free.  The tuning of the rules might result in some revisions in the sets of examples (such as correcting mistakes in the examples and adding missing examples).  (Done for verbs and nouns by March 2019.)

3. Writing and testing regular expression patterns for NS/KSK inflection types as described in :ref:`lexguessing`.  The patterns can be tested against the KSK word list by converting the word list into a LEXC lexicon.  A script checks whether it covers the KSK vocabulary and reports items not covered.  The patterns are used for determining the underlying lexicon entry from a set of word forms.  The patterns may be complete in the above sense but still too permissive which results in too many possible lexical entries for sets of inflected word forms.  The patterns need to be made strict enough to exclude most of the extra entries.  This is achieved by making the patterns reflect the phonological patterns present in inflection classes.  The result of this stage is a set of patterns which can be used both for converting the KSK word list into a LEXC lexicon and for guessing lexicon entries from scratch or with the aid of a corpus.  The result is free.

4. Build a LEXC lexicon out of the verb, noun and adjective entries of KSK which together with the two-level rules is a morphological analyzer for Finnish.  The result of this stage is a CSV list giving each KSK verb, noun and adjective, a  two-level lexicon entry using morphophonemes associated with its base form and inflection code in KSK.  This result cannot be published as such, but it can be used for processing further results.  From this CSV file, the affixes and the two-level rules one produces a KSK morphological ananlyzator KSKTWOL1 in a straight-forward manner, and this is also project internal.  Note that KSKTWOL1 is not prepared to analyze compound words.

5. Use KSKTWOL1 against various corpora, e.g. NSSL, SKTP, KLK, lexeme inventory of OMORFI, in order to collect sets of (non-compound) lexeme entries which occur in them.  The restriction of KSKTWOL to such a subset is taken and closed class entries (pronouns, conjunctions, numerals) are added.  The results are of type OFITWOL1.  These are free lexicons (a seprarate one for each corpus) which can be published and combined according to needs.

6. Augment OFITWOL1 with a mechanism for compounding (two part compounds) resulting in OFITWOL2 (which is again free).  OFITWOL2 is used for collecting tentative sets of compound entries from corpora.  Compound words with a sufficient frequency are (after at least superficial human checking) added to the lexicon resulting in OFITWOL3 (which is free).

7. One can guess more entries by using the patterns as an entry guesser which uses a word form list out of a corpus.  This time it would be useful to use a word form list from which all word forms recognized by OFITWOL2 or OFITWOL3 have been removed.  


Alignment, morphophonemes and rules
===================================

The tables for example words and their inflectional forms were taken from the Reverse Dictionary of Modern Standard Finnish [KSK]_.  The parenthetical forms were reproduced with their parentheses.  The parentheses were ignored in the processing, so less common forms became equally acceptable as the recommended forms in agreement of the goals of OFITWOL.  Some additional inflectional forms were included (and enclosed in square brackets ``[...]``) according the judgement of the author.  A few inflectional classes were considered to include suppletive segments rather than just phonemic alternations, such as nouns like ``askel`` and ``askele`` or ``korkea`` and ``korkee``, and verb forms like ``haravoin`` and ``haravoitsen``.  Such classes were simplified by splitting them into two subclasses anticipating the representation of such lexemes with two entries in the final lexicon.  Entries for pronouns, adjectives and conjunctions were not included in the process.  They were marked with a question mark (``?``) in the first column.  The tables are in `kskn-table.csv <https://github.com/koskenni/twol/blob/master/test/align/kskn-table.csv>`_ and `kskv-table.csv <https://github.com/koskenni/twol/blob/master/test/align/kskv-table.csv>`_.

The small tables needed for identifying the principal forms of nouns and verbs and the morphophonemic representations for the affixes can be browsed at GITHUB: `kskn-affixes.csv <https://github.com/koskenni/twol/blob/master/test/align/kskn-affixes.csv>`_ and `kskv-affixes.csv <https://github.com/koskenni/twol/blob/master/test/align/kskv-affixes.csv>`_.  Note that these files only cover those affixes that are present in the tables and they have no use after this stage.  Full lists of affixes and their reprsentations are written later on.

Raw morphophonemes were calculated and the results are separate for nouns and verbs: `kskn-raw.csv <https://github.com/koskenni/twol/blob/master/test/align/kskn-raw-orig.csv>`_ and `kskv-raw.csv <https://github.com/koskenni/twol/blob/master/test/align/kskv-raw-orig.csv>`_.  You can browse them at GITHUB.  Notice that the raw morphophonemes have longish names which will be shortened by renaming.

Rules were written one-by-one and tested right away.  Note that this stage tries to handle all alternations by using morphophonemes and rules instead of continuation classes which would take care of different stems.  The resulting set of rules can be seen in `ksk-rules.twol <https://raw.githubusercontent.com/koskenni/twol/master/test/align/ksk-rules.twol>`_.
The ``START`` and ``STOP`` directives were used when compiling in order to ignore those rules which have already been compiled and tested (just to speed up the test cycles).  The writing of a rule consisted first of renaming the raw morphophoneme, see `kskn-newnames.csv <https://github.com/koskenni/twol/blob/master/test/align/kskn-newnames.csv>`_ and `kskv-newnames.csv <https://github.com/koskenni/pytwolc/blob/master/test/align/kskv-newnames.csv>`_.  The example file needed by ``twol-comp`` was the concatenation of the renamed files for nouns and verbs, see `ksk-examples.pstr  <https://github.com/koskenni/twol/blob/master/test/align/ksk-examples.pstr>`_

Once all rules seemed to be OK, the complete rule set was tested against the example file.  In particular, now one could see what kinds of negative examples the rules would still accept.  Some tuning of the rules was needed in order to get rid of obvious overgenerated forms.  Some overgenerated forms actually were acceptable and lead to some additions in the example file rather than modifications to the rules.

From here on, the file containing the examples and the rule file became independent and the modifications were made directly to the examples rather than to the tables containing the inflected forms.  Some phenomena were not present in the paradigm tables and needed examples which the tables would not accommodate.


Building KSKTWOL1
=================

Nykysuomen sanakirja and Suomen kielen käänteissanakirja list 82 inflectional classes for nominals and 45 classes for verbs.  Two files with patterns were created in order to map each headword together with its class number into its morphophonological representation which then served as a lexicon entry.  The patterns are fairly loose and general at this stage as they have the inflectional class number available when deducing the morphophonemes.  The patterns for nouns and adjectives is `ofi-pat-na.csv <https://github.com/koskenni/ofitwol/blob/master/ofi/ofi-pat-na.csv>`_ and the one for verbs is ofi-pat-v.csv `<https://github.com/koskenni/ofitwol/blob/master/ofi/ofi-pat-v.csv>`_.
Using these pattern files and the program `pat-proc-py <https://github.com/koskenni/ofitwol/blob/master/ofi/pat-proc.py>`_ lexical entries were produced using the two-level rules priviously written and tested.  These entries corresponded to the noun, adjective and verb entries in the KSK.  Those files are not published as it cannot be guaranteed that they are fully free from copyright.

The lexicon entries for lexemes need still inflectional affixes in order to make them a part of an operational morphological analyzer.  The table listed the affixes and the information defining  the combinations in which the affixes may occur.  The affix file `ofi-affixes.csv <https://github.com/koskenni/ofitwol/blob/master/ofi/ofi-affixes.csv>`_

The table of inflectional affixes was so constructed that with some short Python scrpts, one could produce different versions of LEXC lexicons out of it.  One version could analyze inflected word forms to their base form and grammatical features indicating the inflectional form.  Another version produced the OFITWOL entry of the word instead of the base form.  This was used in the stages for generating entries out of corpora.


Building OFITWOL1
=================

The analyzer KSKTWOL1 was applied to a list of 243,398,561 distinct word forms of *The Finnish N-grams 1820-2000 of the Newspaper and Periodical Corpus of the National Library of Finland* (http://urn.fi/urn:nbn:fi:lb-2014073038) published in Language Bank of Finland (Kielipankki, https://www.kielipankki.fi).  The file contained lots of words which were incorrectly recognized by the OCR progran, e.g.::

  koaaerttimuallkkla
  koaaerttipäivän
  koaaerttlaaaallkkia
  koaaet
  koaaetaan
  koaaeuteec
  koaafamaan

Some of the underlying printed words could be guessed, eg. the first has probably been ``konserttimusiikkia`` but other instances are more difficult.  For the current purposes, these noise words are not harmful at all.  They are just ignored.  One possible later uses of OFITWO would be to improve the accuracy of the OCR of printed old Finnish texts.

Other sections of the list of word forms are analyzed with ``hfst-lookup`` using the KSKTWOL1 are informative, e.g.::
  
  aapeluskouluja  aapeluskouluja+?        inf
  aapeluskukkoo   aapeluskukkoo+? inf
  aapeluslen      aapeluslen+?    inf
  aapelusohjeena  aapelusohjeena+?        inf
  aapelust        aapelust+?      inf
  aapelusta       aapelu{ØkØkk}s{ØeØeØ} /s;+N+SG+PTV      0,000000
  aapelustaan     aapelu{ØkØkk}s{ØeØeØ} /s;+N+SG+PTV+SG3  0,000000
  aapelustakaan   aapelu{ØkØkk}s{ØeØeØ} /s;+N+SG+PTV+KAAN 0,000000
  aapelustani     aapelu{ØkØkk}s{ØeØeØ} /s;+N+SG+PTV+SG1  0,000000
  aapelustcn      aapelustcn+?    inf
  aapelusten      aapelu{ØkØkk}s{ØeØeØ} /s;+N+PL+GEN      0,000000

Here one can identify entries of the noun ``aapelus`` (``aapinen``, 'alphabet book') in five different forms.  The other word forms shown are either misspellings or compound words of the same lexeme.  Anyway, the analyzer shows that the word ``aapelus`` occurs in the corpus and that a lexicon ``aapelu{ØkØkk}s{ØeØeØ} /s;`` accounts for those five forms.  The entry tells that the lexeme is inflected as ``aapelus``, ``aapeluksen``, ``aapelusta``, ``aapeluksia``. etc.


Guessing entries
================

