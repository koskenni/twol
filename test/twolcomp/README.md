# twol-comp tests

When in this directory, run the following, which compiles and tests a
small two-level rule grammar:
   
    $ twol-comp -t2 grada.pstr grada.twol

The result ought to be something like:

    {kg}:g|{kj}:j|{kv}:v|{pm}:m|{pv}:v|{pØ}:Ø|{td}:d | {tl}:l | {tn}:n
      | {tr}:r | {tØ}:Ø <=>  _  Vi Closed ;
    All positive examples accepted 
    All negative examples rejected


    {kØ}:Ø <=>   _  Vi Closed ;
    All positive examples accepted
    All negative examples rejected


    {kØ'}:' <=> Vi :a _ :a Closed , Vi :e _ :e Closed ,
      Vi :i _ :i Closed , Vi :o _ :o Closed , Vi :u _ :u Closed ,
      Vi :y _ :y Closed , Vi :ä _ :ä Closed ;
    All positive examples accepted
    All negative examples rejected


    {kØ'}:k /<= _ Vi Closed ;
    All positive examples accepted

The following command runs another grammar which, intentionally, has
some errors in it:

    $ twol-comp -t2 grada.pstr graderr.twol

It should produce the following output where the syntax errors are
detected and indicated:


    ****************************************
    ERROR WAS IN INPUT LINES: 16 - 18
    {kg}:g | {kj}:j | {kv}:v | {pm}:m | {pv}:v | {pØ}:Ø |
        {td}:d | {tl}:l | {ťn}:n | {tr}:r | {tØ}:Ø
            <=>  _  Vi Closed ;

    THE ERROR IS LIKELY ABOVE THE '^' OR BEFORE IT
    {kg}:g | {kj}:j | {kv}:v | {pm}:m | {pv}:v | {pØ}:Ø |
       {td}:d | {tl}:l | {ťn}:n | {tr}:r | {tØ}:Ø <=>  _  Vi Closed ;
                                                         
                               ^ <--- FailedParse HERE
    EXPLANATION:
         input symbol '{ťn}' and symbol pair '{ťn}:n' not in alphabet
    ****************************************


    ****************************************
    ERROR WAS IN INPUT LINES: 19 - 19
    {kØ}:Ø <=>   _  Vi Closd ;

    THE ERROR IS LIKELY ABOVE THE '^' OR BEFORE IT
    {kØ}:Ø <=>   _  Vi Closd ;
                            ^ <--- FailedParse HERE
    EXPLANATION:
         'Closd' is an invalid pair/definend symbol
    ****************************************


    ****************************************
    ERROR WAS IN INPUT LINES: 29 - 36
    {kØ'}:' <=>
        Vi :a _ :a Closed ,
        Vi :e _ :e Closed ,
        Vi :i _ :i Closed ,
        Vi :o _ :o Closed 
        Vi :u _ :u Closed ,
        Vi :y _ :y Closed ,
        Vi :ä _ :ä Closed ;

    THE ERROR IS LIKELY ABOVE THE '^' OR BEFORE IT
    {kØ'}:' <=> Vi :a _ :a Closed , Vi :e _ :e Closed , Vi :i _ :i Closed ,
       Vi :o _ :o Closed Vi :u _ :u Closed , Vi :y _ :y Closed ,
       Vi :ä _ :ä Closed ;
                                                      
                                ^ <--- FailedToken HERE
    ****************************************



    {kØ'}:k /<= _ Vi Closed ;
    All positive examples accepted

The first error was found because one symbol or symbol pair was
erroneously written with a diacritic.  That never occurred in the
examples, so the compiler reported the error.  Note that the rules do
not define an alphabet, the alphabet is defined by the examples.

The second error concerned a typo where a name of a defined expression
was mistyped.  The examples must contain all allowed correspondences
of input and output symbols.  Thus, correct symbols may not be mixed
arbitrarily, e.g. ``t:k`` in the rules here would be detected as an
error, even if ``t`` and ``k`` are perfectly acceptable letters.

The last error is about a comma that was accidentally omitted.  This
results in a context with two underscores, and the syntactic parser
notes this.  It does not try to explain, but it points to the location
where the error becomes evident.

The rule in error is given twice: once as it was in the input file
with all spaces and line breaks.  For the indication of the location
of the error, the compiler gives a stripped version of the rule simply
because the TatSu parser works with tokens where whitespace is not
preserved. 
