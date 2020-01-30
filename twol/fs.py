"""fs.py: A wrapper module for basic finite-state operations

The HFST engine used for accomplishing the operations but all functions make copies of their arguments when it is necessary to avoid side-effects.

© Kimmo Koskenniemi, 2018. This is free code under the GPL 3 license."""

import hfst
import grapheme
import twol.cfg as cfg

def expr(e):
    """Return an FST corresponding to a XFST regular expression"""
    res = hfst.regex(e)
    res.minimize()
    return res

def concat(f, g):
    """Return the concatenation of two FSTs"""
    res = f.copy()
    res.concatenate(g)
    res.minimize()
    return res

def star(f):
    """Return the Kleene star iteration of an FST"""
    res = f.copy()
    res.repeat_star()
    res.minimize()
    return res

def plus(f):
    """Return the Kleene plus iteration of an FST"""
    res = f.copy()
    res.repeat_plus()
    res.minimize()
    return res

def crossprod(f, g):
    """Return the cross-product of two FSAs"""
    res = f.copy()
    res.cross_product(g)
    res.minimize()
    return res

def compose(f, g):
    """Return the composition of two FSTs"""
    res = f.copy()
    res.compose(g)
    res.minimize()
    return res

def union(f, g):
    """Return the union of two FSTs"""
    res = f.copy()
    res.disjunct(g)
    res.minimize()
    return res

def intersect(f, g):
    """Return the intersection of two FSTs

    Both arguments are assumed to be length preserving mappings.
    """
    res = f.copy()
    res.conjunct(g)
    res.minimize()
    return res

def upper(f):
    """Return the input projection of an FST"""
    res = f.copy()
    res.input_project()
    res.minimize()
    return res

def lower(f):
    """Return the output projection of an FST"""
    res = f.copy()
    res.output_project()
    res.minimize()
    return res

def symbol_to_fsa(sym):
    """Return a FSA which accepts the one letter string 'sym'

    The symbol 'sym' may be e.g. a composed Unicode grapheme, i.e. a
    string of two or more Unicode characters.
    """
    bfsa = hfst.HfstBasicTransducer()
    string_pair_path = ((sym, sym))
    bfsa.disjunct(string_pair_path, 0)
    fsa = hfst.fst(bfsa)
    return(fsa)

def symbol_pair_to_fst(insym, outsym):
    """"Return a FST which accepts one the pair string 'insym:outsym'"""
    bfst = hfst.HfstBasicTransducer()
    string_pair_path = ((insym, outsym))
    bfsa.disjunct(string_pair_path, 0)
    fst = hfst.fst(bfst)
    return(fst)

def string_to_fsa(grapheme_string):
    """Return a FSA which accepts the sequence of graphemes in the string"""
    bfsa = hfst.HfstBasicTransducer()
    grapheme_list = list(grapheme.graphemes(grapheme_string))
    string_pair_path = tuple(zip(grapheme_list, grapheme_list))
    if cfg.verbosity >= 10:
        print(grapheme_list)
        print(string_pair_path)
    bfsa.disjunct(string_pair_path, 0)
    fsa = hfst.HfstTransducer(bfsa)
    return(fsa)
    
if __name__ == "__main__":
    print("fs module is not meant to be used as a script")
