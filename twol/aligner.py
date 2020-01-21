""" aligner.py

Aligns two words (or morphs) by adding some zero symbols so that
phonemes in corresponding positions are optimally similar.

Copyright 2017-2019, Kimmo Koskenniemi

This is free software according to GNU GPL 3 license.
"""

def main():
    import argparse
    arpar = argparse.ArgumentParser(
        description="Run-time aligner of words")
    arpar.add_argument(
        "metrics",
        help="FST which contains weights for preferring alternative alignments")
    arpar.add_argument(
        "-d", "--delimiter",
        help="Separates the two cognates, default is ':'",
        default=":")
    arpar.add_argument(
        "-c", "--comment-separator",
        help="Comment separator. Comments are ignored but copied to output. Default is '!'",
        default="!")
    arpar.add_argument(
        "-l", "--layout",
        choices=["vertical","list","horizontal"],
        help="output layout",
        default="vertical")
    arpar.add_argument(
        "-n", "--number",
        help="number of best results to be printed. Default is 1",
        type=int, default=1)
    arpar.add_argument(
        "-w", "--weights",
        help="print also the weight of each alignment. Default is not to print.",
        action="store_true")
    arpar.add_argument(
        "-v", "--verbosity",
        help="Level of diagnostic information to be printed. Default is 0",
        type=int, default=0)

    args = arpar.parse_args()

    import hfst
    algfile = hfst.HfstInputStream(args.metrics)
    align = algfile.read()

    separator = args.delimiter
    import sys
    for line in sys.stdin:
        pair, comm, comments = line.strip().partition(args.comment_separator)
        if args.verbosity > 0:
            print(pair, args.comment_separator, comm)
        f1, sep, f2 =  pair.strip().partition(args.delimiter)
        if not f2:
            f2 = f1

        w1 = hfst.fst(f1)
        w1.insert_freely(("Ø","Ø"))
        w1.minimize()
    #    print(w1)

        w2 = hfst.fst(f2)
        w2.insert_freely(("Ø","Ø"))
        w2.minimize()
    #    print(w2)

        w3 = hfst.HfstTransducer(w1)
        w3.compose(align)
        w3.compose(w2)
    #    print(w1)

        w3.n_best(args.number)
        w3.minimize()

    #    print(w3)

        paths_str = w3.extract_paths(output='text')
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
                    comments = weight.rjust(4) + " " + comments
                if args.comment_separator:
                    comments = comments + " | " + f1 + " " + f2
                    algh = algh.ljust(30) + args.comment_separator + comments
                
                print(algh)

    return

if __name__ == "__main__":
    main()
