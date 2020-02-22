"""metric.py

Produces a weighted finite-state transducer (WFST) out of the alphabet
definition as interpreted by alphabet.py.  The WFST is the used by the
aligner.py program.

Copyright 2020, Kimmo Koskenniemi

This is free software according to GNU GPL 3 license.

"""

import sys
import re
import twol.alphabet as alphabet
import twol.cfg as cfg
import hfst

within_set_lst = []
forall_lst = []

pair_weight_dict = {}

def alignment_fst():
    pair_weight_lst = []
    for insym in alphabet.consonant_set:
        mphon = "Ø" + insym
        if alphabet.mphon_is_valid(mphon):
            xyw = "{}:{}::{}".format(insym, "Ø", alphabet.mphon_weight(mphon))
        pair_weight_lst.append(xyw)
        mphon = insym + "Ø"
        if alphabet.mphon_is_valid(mphon):
            xyw = "{}:{}::{}".format("Ø", insym, alphabet.mphon_weight(mphon))
        pair_weight_lst.append(xyw)
        for outsym in alphabet.consonant_set:
            mphon = insym + outsym
            if alphabet.mphon_is_valid(mphon):
                xyw = "{}:{}::{}".format(insym, outsym,
                                         alphabet.mphon_weight(mphon))
                pair_weight_lst.append(xyw)
    for insym in alphabet.vowel_set:
        mphon = "Ø" + insym
        if alphabet.mphon_is_valid(mphon):
            xyw = "{}:{}::{}".format(insym, "Ø", alphabet.mphon_weight(mphon))
        pair_weight_lst.append(xyw)
        mphon = insym + "Ø"
        if alphabet.mphon_is_valid(mphon):
            xyw = "{}:{}::{}".format("Ø", insym, alphabet.mphon_weight(mphon))
        pair_weight_lst.append(xyw)
        for outsym in alphabet.vowel_set:
            mphon = insym + outsym
            if alphabet.mphon_is_valid(mphon):
                xyw = "{}:{}::{}".format(insym, outsym,
                                         alphabet.mphon_weight(mphon))
                pair_weight_lst.append(xyw)
    pair_weight_str = "|".join(pair_weight_lst)
    if cfg.verbosity >= 20:
        print("\npair_weight_str:", pair_weight_str)

    loop_sets = {}
    loop_sets["Consonants"] = alphabet.consonant_set - {"Ø"}
    loop_sets["Vowels"] = alphabet.vowel_set- {"Ø"}
    if cfg.verbosity >= 20:
        print("\nloop_sets:", loop_sets)
    for_all_lst = []
    for expr, var, loop_set in alphabet.for_definitions_lst:
        if cfg.verbosity >= 25:
            print(expr, var, loop_set)
        for x in loop_sets[loop_set]:
            if cfg.verbosity >= 25:
                print(x, var, loop_set)
            item_expr = re.sub(var, x, expr)
            if cfg.verbosity >= 25:
                print("item_expr:", item_expr)
            for_all_lst.append(item_expr)
    for_all_str = "|".join(for_all_lst)
    if cfg.verbosity >= 20:
        print("\nfor_all_str:", for_all_str)

    exceptions_str = " | ".join(alphabet.exception_lst)
    if cfg.verbosity >= 20:
        print("\nexceptions_str:", exceptions_str)

    fst = hfst.regex(pair_weight_str + "|" + for_all_str + "|" + exceptions_str)
    fst.repeat_star()
    fst.minimize()
    return fst

def main():
    #last_modified_date = datetime.fromtimestamp(mtime)
    
    version = cfg.timestamp(__file__)
    
    import argparse
    arpar = argparse.ArgumentParser(
        "twol-metric",
        description="""Builds a distance metric FST out of an alphabet
        description. See
        https://pytwolc.readthedocs.io/en/latest/alignment.html
        for detailed instructions. Version {}""".format(version)
    )
    arpar.add_argument(
        "alphabet",
        help="An alphabet definition with features and similarity sets")
    arpar.add_argument(
        "metrics",
        help="FST which contains weights for preferring alternative alignments")
    arpar.add_argument(
        "-v", "--verbosity",
        help="Level of diagnostic output printed, default=0",
        type=int, default=0)
    args = arpar.parse_args()

    cfg.verbosity = args.verbosity
    cfg.all_zero_weight = 1000

    alphabet.read_alphabet(args.alphabet)

    fst = alignment_fst()

    fstfile = hfst.HfstOutputStream(filename=args.metrics)
    fstfile.write(fst)
    fstfile.flush()
    fstfile.close()
    return

if __name__ == "__main__":
    main()
