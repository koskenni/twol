"""Global values and functions for twol modules.

These definitions and values are used by several twol-related
programs, e.g. `twol`, `multialign`, `table2words`,
`words2zerofilled` etc.
"""

__author__ = """© Kimmo Koskenniemi, 2018"""

import re
import hfst

#hfst.set_default_fst_type(hfst.ImplementationType.FOMA_TYPE)

verbosity = 0

all_zero_weight = 100.0
"""in multialign: the weight for a set {'Ø'} which is normally
not preferred but sometimes is needed, eg. when using Øs in
the input words"""

final = False
"""In multialign: preferring of the deletion of final phonemes"""

definitions = {}

error_message = ""

input_symbol_set = set()
"""The set of input symbols (phonemes and morphophonemes) occurring in
the examples"""

output_symbol_set = set()
"""The set of output symbols (surface characters) occurring in the
examples"""

symbol_pair_set = set() 
"""The set of all symbol pairs (e.g. ('{aä}', 'a')) in the examples."""

all_pairs_fst = None
"""An FST which accepts any one symbol pair in symbol_pair_set"""

pair_symbol_set = set()
"""The set of all normalized pair symbols (e.g. 'k', '{aä}:a')
occurring in the examples"""

examples_fst = None
"""Examples as a tranducer that accepts them as symbol pair sequences"""

example_lst = []
"""List of example words as pair symbol strings"""

example_set = set()
"""Set of examples as space-separated string of normalized pair symbols"""

def pairsym2sympair(pairsym):
    """Converts one pair symbol into a corresponding symbol pair
    
    pairsym -- a pair symbol, e.g. 'k' or '{aä}:a' or 'k:k'

    returns -- a symbol pair, e.g. ('k', 'k') or ('{aä}', 'a') or ('k','k')
    """
    m = re.match(r"^([^:]*):([^:]*)$", pairsym)
    if m:
        return(m.group(1), m.group(2))
    else:
        return(pairsym, pairsym)

def sympair2pairsym(insym, outsym):
    """Converts a symbol pair into a corresponding normalized pair symbol

    insym -- a symbol in the input alphabet, e.g. 'k' or '{aä}'

    outsym -- a symbol in the output alphabet, e.g. 'k' or 'a'

    returns -- a normalized pair symbol, e.g. 'k' or '{aä}:a' (not 'k:k')
    """
    if insym == outsym:
        return(insym)
    else:
        return(insym + ':' + outsym)

if __name__ == "__main__":
    print("cgf module is not meant to be used as a script")
