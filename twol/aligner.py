""" aligner.py

Aligns two words (or morphs) by adding some zero symbols so that
phonemes in corresponding positions are optimally similar.

Copyright 2017-2019, Kimmo Koskenniemi

This is free software according to GNU GPL 3 license.
"""

import hfst
import twol.cfg as cfg
import twol.multialign as multialign

def align_two_words(in_word, out_word, aligner_fst, zero, number):
    w1 = hfst.fst(in_word)
    w1.insert_freely((zero,zero))
    w1.minimize()
    ###print(w1)

    w2 = hfst.fst(out_word)
    w2.insert_freely((zero,zero))
    w2.minimize()
    ###print(w2)

    w3 = hfst.HfstTransducer(w1)
    w3.compose(aligner_fst)
    w3.compose(w2)
    ###print(w1)

    w3.n_best(number)
    w3.minimize()
    ###print(w3)

    raw_paths = w3.extract_paths(output='raw')
    if cfg.verbosity >= 10:
        print("raw_paths:", raw_paths)
    return raw_paths

def print_result(raw_path, comments, weights, layout="horizontal"):

    weight, sym_pair_lst = raw_path
    
    if layout == "horizontal":
        mphon_lst = \
            [insym if insym == outsym else insym + ":" + outsym for insym, outsym in sym_pair_lst]
        mphonemic_str = " ".join(mphon_lst)
        if weights:
            print(mphonemic_str.ljust(40), weight)
        else:
            print(mphonemic_str)
        return
    if layout == "vertical" or layout == "list":
        in_word_lst = [insym for insym, outsym in sym_pair_lst]
        in_word_str = "".join(in_word_lst)
        out_word_lst = [outsym for insym, outsym in sym_pair_lst]
        out_word_str = "".join(out_word_lst)
    if layout == "vertical":
        print(in_word_str)
        print(out_word_str)
        if weights:
            print(29 * " ", weight)
        print()
    elif layout == "list":
        print(in_word_str, out_word_str)
        if weights:
            print(29 * " ", weight)
    return

def main():

    version = cfg.timestamp(__file__)
    
    import argparse
    arpar = argparse.ArgumentParser(
        "twol-aligner",
        description="""Aligns pairs of words separated by a
        colon. See https://pytwolc.readthedocs.io/en/latest/alignment.html
        for detailed instructions. Version {}""".format(version))
    arpar.add_argument(
        "metrics",
        help="FST computed with twol-metric from an alphabet file."
        " The FST contains weights for phoneme correspondences.")
    arpar.add_argument(
        "-d", "--delimiter",
        help="Separates the two cognates, default is ' '",
        default=" ")
    arpar.add_argument(
        "-l", "--layout",
        choices=["vertical","list","horizontal"],
        help="output layout",
        default="vertical")
    arpar.add_argument(
        "-c", "--comment-separator",
        help="""Comment separator. Comments in input after this
        character are just copied to output. Input words are then
        also copied to the end of comments. Default separator is ''
        i.e. no comments.  Comments come to the output only in
        horizontal layout.""",
        default="")
    arpar.add_argument(
        "-w", "--weights",
        help="print also the weight of each alignment."
        " Default is not to print."
        " Works only if a comment separator is also set.",
        action="store_true")
    arpar.add_argument(
        "-n", "--number",
        help="number of best results to be printed. Default is 1",
        type=int, default=1)
    arpar.add_argument(
        "-v", "--verbosity",
        help="Level of diagnostic information to be printed. "
        "Default is 0",
        type=int, default=0)

    args = arpar.parse_args()
    cfg.verbosity = args.verbosity

    algfile = hfst.HfstInputStream(args.metrics)
    aligner_fst = algfile.read()

    separator = args.delimiter
    import sys
    import twol.multialign as multialign
    
    for line in sys.stdin:
        if args.comment_separator:
            pair, comm, comments = \
                line.strip().partition(args.comment_separator)
        else:
            pair, comm, comments = line.strip(), "", ""
        if args.verbosity > 0:
            print(pair, args.comment_separator, comm)
        in_word, sep, out_word =  pair.strip().partition(args.delimiter)
        if not out_word:
            out_word = in_word

        raw_paths = align_two_words(in_word, out_word,
                                    aligner_fst,
                                    "Ø",
                                    args.number)
        for aligned_result in raw_paths:
            print_result(aligned_result,
                         comments,
                         args.weights,
                         layout=args.layout)


    return

if __name__ == "__main__":
    main()
