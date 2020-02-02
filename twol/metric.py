"""metric.py

Produces a weighted finite-state transducer (WFST) out of the alphabet
definition as interpreted by alphabet.py.  The WFST is the used by the
aligner.py program.

Copyright 2020, Kimmo Koskenniemi

This is free software according to GNU GPL 3 license.

"""

within_set_lst = []
forall_lst = []

pair_weight_dict = {}


def main():
    version = "2020-02-01"
    
    import argparse
    arpar = argparse.ArgumentParser(
        "twol-metric",
        description="Builds a distance metric FST out of an alphabet"\
        " description. See"\
        " https://pytwolc.readthedocs.io/en/latest/alignment.html"\
        " for detailed instructions. Version {}".format(version)
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

    import sys
    import re
    import twol.alphabet as alphabet
    import twol.cfg as cfg

    cfg.verbosity = args.verbosity

    alphabet.read_alphabet(args.alphabet)

    pair_weight_lst = []
    for insym in alphabet.consonant_set:
        for outsym in alphabet.consonant_set:
            mphon = insym + outsym
            if alphabet.mphon_is_valid(mphon):
                xyw = "{}:{}::{}".format(insym, outsym, alphabet.mphon_weight(mphon))
                pair_weight_lst.append(xyw)
    for insym in alphabet.vowel_set:
        for outsym in alphabet.vowel_set:
            mphon = insym + outsym
            if alphabet.mphon_is_valid(mphon):
                xyw = "{}:{}::{}".format(insym, outsym,
                                         alphabet.mphon_weight(mphon))
                pair_weight_lst.append(xyw)
    pair_weight_str = "|".join(pair_weight_lst)
    if args.verbosity >= 10:
        print("\npair_weight_str:", pair_weight_str)

    loop_sets = {}
    loop_sets["Consonants"] = alphabet.consonant_set - {"Ø"}
    loop_sets["Vowels"] = alphabet.vowel_set- {"Ø"}
    if args.verbosity >= 10:
        print("\nloop_sets:", loop_sets)
    for_all_lst = []
    for expr, var, loop_set in alphabet.for_definitions_lst:
        if args.verbosity >= 15:
            print(expr, var, loop_set)
        for x in loop_sets[loop_set]:
            if args.verbosity >= 15:
                print(x, var, loop_set)
            item_expr = re.sub(var, x, expr)
            if args.verbosity >= 15:
                print("item_expr:", item_expr)
            for_all_lst.append(item_expr)
    for_all_str = "|".join(for_all_lst)
    if args.verbosity >= 10:
        print("\nfor_all_str:", for_all_str)

    exceptions_str = " | ".join(alphabet.exception_lst)
    if args.verbosity >= 10:
        print("\nexceptions_str:", exceptions_str)
    import hfst

    fst = hfst.regex(pair_weight_str + "|" + for_all_str + "|" + exceptions_str)
    fst.repeat_star()
    fst.minimize()
    fstfile = hfst.HfstOutputStream(filename=args.metrics)
    fstfile.write(fst)
    fstfile.flush()
    fstfile.close()
    return

if __name__ == "__main__":
    main()
