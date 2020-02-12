""" aligner.py

Aligns two words (or morphs) by adding some zero symbols so that
phonemes in corresponding positions are optimally similar.

Copyright 2017-2019, Kimmo Koskenniemi

This is free software according to GNU GPL 3 license.
"""

import hfst

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

    paths_str = w3.extract_paths(output='text')
    return paths_str


def main():

    version = "2020-02-12"
    
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

    algfile = hfst.HfstInputStream(args.metrics)
    aligner_fst = algfile.read()

    separator = args.delimiter
    import sys
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

        paths_str = align_two_words(in_word, out_word,
                                    aligner_fst,
                                    "Ø",
                                    args.number)

        paths_lst = paths_str.split(sep="\n")
        # print(paths_lst) ###
        for path in paths_lst:
            if not path:
                continue
            pair, tab, weight = path.partition("\t")
            inword, colon, outword = pair.partition(":")
            if not colon:
                outword = inword
            tab = "\t" if args.weights else ""
            if args.layout == "list":
                print(inword + "\t" + outword + tab + weight)
            elif args.layout == "vertical":
                if args.weights:
                    print(inword.ljust(35), weight)
                else:
                    print(inword )
                if comments and args.comment_separator:
                    print(outword.ljust(40), comments)
                else:
                    print(outword)
                print()
            else:                       # horizontal
                lst = []
                for inch, outch in zip(inword, outword):
                    if inch == outch:
                        pair = inch
                    else:
                        pair = inch + outch
                    lst.append(pair)
                algh = " ".join(lst)
                if args.weights:
                    weight = weight.rjust(4)
                else:
                    weight = ""
                if args.comment_separator:
                    if comments:
                        comments = " " + comments + " | " + in_word + " " + out_word
                    else:
                        comments = " " + in_word + " " + out_word
                    algh = algh.ljust(30) + args.comment_separator + weight + comments
                
                print(algh)

    return

if __name__ == "__main__":
    main()
