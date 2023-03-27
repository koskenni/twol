
.. _pytwol-glossary:


========
Glossary
========

.. glossary::

   alignment
     The process of making allomorphs equal length and make them to correspond each other :term:`phoneme` by phoneme.  Alignment consists of adding :term:`zero` symbols as needed so that the phonemes in the same position are phonologically similar.  One could align, e.g. ``mäki`` and ``mäe`` by inserting one zero to the latter morph (``mäØe``) so that the corresponding phonemes would be ``mm``, ``ää``, ``kØ`` and ``ie``.  See :doc:`alignment`.

   comma-separated values
   CSV
     A common exchange format for representing tabular data which most spreadsheet programs can import and export.  In CSV table rows are usually lines where fields are separated by a comma.  Instead of a comma, a semicolon is sometimes used.  Values may be enclosed in double quotes if they contain e.g. commas.  For more information, see https://en.wikipedia.org/wiki/Comma-separated_values.

   context
      The immediate environment where a symbol occurs.  The context consists of the left context, i.e. zero or more symbols occurring before and of the right context, i.e. zero or more symbols occurring after the symbol whose context we are speaking of.

   deletion
     Deletion is said to occur when a phoneme in a in a morph corresponds to :term:`zero` in another :term:`morph` of the same :term:`morpheme`.  Cf. :term:`epenthesis`.

   encoded FST
     A :term:`FST` can be converted into an equivalent :term:`FSM` by changing all its transition labels so that the new labels are combinations of the original input and output labels using functions *fst_to_fsa*.  If the original FST contained a transition ``{aä}:a`` then the encoded FSA will have a transition ``{aä}^a:{aä}^a``.  An encoded FSA can be made back to a normal FST by the function *fsa_to_fst*.  See the HFST documentation 

   epenthesis
     Epenthesis is said to occur when a :term:`zero` in a morph corresponds to a phoneme in another morph of the same morpheme.  In the simplified two-level framework, epenthesis and :term:`deletion` are equivalent.

   epsilon
   null string
     Epsilon represents the null string, i.e. a string whose length is 0.  For a :term:`FSM` or a :term:`FST` it matching an epsilon in input means that the machine reads nothing (i.e. the input tape does not move).  An epsilon in output for a FST means that nothing is written.  Epsilon is not present in the two-level model.  Instead, it uses a :term:`zero`.

   finite-state machine
   finite-state automaton
   FSM
   FSA
     A finite-state machine (automaton).  An abstract device consisting of :term:`states <state>` and :term:`transitions <transition>`.  One state is the *initial state* where the FSM is when it starts.  An FSM reads symbols, one at a time and moves into another state if there is a transition from the current state where the transition label is the current input symbol.  If so, the FSM moves into a new state given by the transition.  It continues so, until the last input symbol has been read.  If the FSM is in one of its *final states*, the FSM is said to *accept* the input string.  If the FSM fails to have a matching transition at any step, then the FSM *rejects* the input.  The FSM also rejects the input, if it ends up in a state which is not one of the final states.

   finite-state transducer
   FST
     An abstract machine like a :term:`FSM` but it operates with two tapes: *input tape* and *output tape*.  Thus, the :term:`transitios <transition>` are labeled with a :term:`symbol pair` instead of a single symbol.  A transition is applied, if the current input symbol matches the former component of the symbol pair in the transition.  Then, the latter component of the symbol pair is output.  Labels in FST transitions may, in general, also  contain :term:`epsilons <epsilon>` instead of symbols.  In the two-level rules and examples, no epsilons are used.  Two-level FSTs define, thus, *same length relations*, i.e. the relate pairs of strings where both strings are equally long.

   generalized restriction
     A method for compiling rules by formulating the rule components as regular sets.  Additional boundary markers are used so that the restriction for the center part and the restrictions for the context parts can be combined.  The boundary markers are removed after the operations.  Using the boundary markers, the context parts get a natural expression and the context parts can be disjuncted in a natural manner.  See [ylijyrä2006]_ for details.

   inflection
   conjugation
   declination
     A process of producing :term:`word forms <word form>` of a :term:`lexeme`.  Inflecting verbs is often called *conjugation* and inflecting nouns is called *declination*.  Conjugation can also refer to an :term:`inflection class` of verbs and delination to an inflectional class of nouns.

   inflection class
   inflectional class
     A set of :term:`lexemes <lexeme>` which are inflected in a similar way.

   initial state
     The :term:`state` where an automaton (e.g. :term:`FSM` or :term:`FST`) is when it starts.

   input symbol
     In general, input symbols are the symbols that a FST reads in.  In two-level rules and examples, the input symbols belong to the underlying representation and they may be either phonemes or morphophonemes.  The input symbols in two-level rules and examples are sometines also called *lexical characters* or *upper characters*.

   lemma
   lexeme
     Lexemes correspond roughly to dictionary entry words.  In morphological analysis, a lexeme can be idientified by its base form and inflectional class.  Two words represent different lexemes if they have an identical base form but are inflected in a different way.  A lexeme may have several *senses*.  A lemma is a label for all inflected forms of a lexeme.  A representation of a lexeme in a lexicon might have more information than just a lemma.

   morph
     A part of the surface form which is said to correspond to a :term:`morpheme`, e.g. in ``kadulla`` the part ``kadu`` (street) and the part ``lla`` (on) are morphs.

   morpheme
     A minimal unit with a meaning and which is manifeseted as :term:`morphs <morph>`, e.g. we may have a morpheme ``KATU`` which has a meaning 'street' and is manifested as two possible morphs ``katu`` and ``kadu``.  E.g. stems of words may be morphemes as well as various affixes for inflection and derivation.  Some stems combine two or more morphemes, e.g. compounds and derived lexemes.

   morphophoneme
     An abstract symbol which denotes the alternation of surface characters in a position within a morpheme. E.g. ``{td}`` could denote the alternation between ``t`` and ``d``.  The names of the morphophonemes are chosen by the linguist who writes a two-level grammar.  Morphophonemes are always :term:`input symbols <input symbol>` to the two-level rules.

   morphophonemic representation
     An abtract representation which is a kind of summary of the concrete surface :term:`morphs <morph>` of a :term:`morpheme`.  Two-level rules describe the relation between the lexical and the surface level.  Corresponds to the sequence of :term:`input symbols <input symbol>` of two-level rules.  The morphophonemic representation is sometimes also called the *lexical level* or the *upper level*.

   output symbol
   surface character
     In general, output symbols are the symbols that a FST writes as output.  In two-level rules and examples, the output symbols are the phonemes in actual word forms (or letters in a near phonemic writing system).  Output symbols are sometimes called *surface characters* or *lower characters*.

   pair symbol
     A human readable representation of a :term:`symbol pair`.  It consists either of an output symbol, e.g. ``a`` which corresponds to symbol pair ``('a', 'a')``, or an input symbol followed by a colon followed by an output symbol, e.g. ``{aä}:a`` which corresponds to symbol pair ``('{aä}', 'a')``.

   phoneme
     For the purposes of writing two-level rules and analyzers, phonemes often correspond to letters in a near-phonemic writing system.  In linguistics, phonemes are units which represent similar phohes whose differences do not carry any additional information.  The choice of a phone in a phoneme might be irrelevant or sometimes determined by the surrounding context of phones.

   principal forms
   principal parts
     A subset of inflectional forms that is needed for determining the full paradigm of inflectional forms for a :term:`lemma`.
     
   raw morphophoneme
     A combination of :term:`phonemes <phoneme>` which correspond to each other as a result of alignment, e.g. if ``käsi``, ``käde``, ``käte``, ``käs`` and ``kät`` are aligned, we get raw morphophonemes such as ``kkkk`` or ``sdtst``.  Raw morhpphonemes are usually renamed to morphophonemes, e.g. ``k`` or ``{tds}``

   state
     :term:`FSMs <FSM>` and :term:`FSTs <FST>` have states.  At any moment, the machines are in some state and during the process, they move from some state to another state according to what :term:`transition` matches the :term:`input symbol`.

   surface representation
     The concrete representation of of word forms as a sequence of phonemes or letters (possibly with some :term:`zeros <zero>` inserted).

   surface symbol
     Surface symbols are phonemes or the symbols which are used to write word forms.  For two-level rules, surface symbols are output-symbols.

   symbol pair
     A tuple consisting of an input and an output symbol, e.g. ``({aä}, a)``

   transition
     :term:`FSMs <FSM>` and :term:`FSTs <FST>` have transitions which tell to which state the machine must move according to the :term:`input symbol` that is currently being processed.  In a :term:`FST`, the transition also gives the possible :term:`output symbol`.

   word form
     A possibly inflected form of a lexeme.  A word form is a string of phonemes or letters.  A word form might have several occurrences (sometimes called word *tokens*) in a text.  In some statistical contexts, word_forms are called word *types* or just types.

   zero
     A placeholder which indicates that in some other allomorphs there is some phoneme in this position.  By inserting zeros, one makes the allomorphs same length.  Zero is not a morphophoneme and it never occurs in morphophonemic representations.  The zero is not an :term:`epsilon`.

     
