"""Aligns morphs that occur in the example words by inserting zero symbols

© Kimmo Koskenniemi, 2017-2018. This is free software under the GPL 3 license.
"""

def main():

    version = "2020-02-08"
    
    import argparse
    argparser = argparse.ArgumentParser(
        "python3 parad2zerofilled.py",
        description="Aligns a set of word forms with morph boundaries"\
        " Version {} ".format(version))
    argparser.add_argument(
        "input",
        default="ksk-seg-examp.csv",
        help="moprheme names and segmented example words as a CSV file")
    argparser.add_argument(
        "output",
        default="ksk-alig-examp.csv",
        help="example words plus zero-filled aligned forms as a CSV file")
    argparser.add_argument(
        "alphabet",
        default="alphabet-test.text",
        help="An alphabet definition which determines"\
        " the weights for morphophonemes")
    argparser.add_argument(
        "-s", "--morph-separator",
        default=".",
        help="Separator between morphs in the word form, default is '.'")
    argparser.add_argument(
        "-d", "--csv-delimiter",
        default=",",
        help="Delimiter between the fields")
    argparser.add_argument(
        "-n", "--name-separator",
        default=".",
        help="separator between morpheme names"\
        " in the morpheme list,, default is '.'")
    argparser.add_argument(
        "-z", "--zero-symbol",
        default="Ø",
        help="symbol to be inserted in word forms to align them")
    argparser.add_argument(
        "-x", "--extra-zeros", default=0, type=int,
        help="number of extra zeros to be tried in alighnment")
    argparser.add_argument(
        "-v", "--verbosity", default=0, type=int,
        help="level of diagnostic and debugging output")
    args = argparser.parse_args()

    import re
    import csv
    import collections
    from orderedset import OrderedSet
    import grapheme

    # STEP 1:
    # Read in the segmented words and collect the allomorphs of each morpheme

    morphs_of_morpheme = {} 
    """A dict to which allomorphs of each morpheme are collected:
    morphs_of_morpheme[morpheme_name] == OrderedSet of its allomorphs.
    """
    seg_example_list = []
    """A list to which of all example words are collected. 
    Each word is represented as a list of (morpheme,morph) pairs.
    """
    stem_name_set = set()
    """Set of stem morphemes i.e. names of stem morphemes.
    """
    csvfile = open(args.input)

    reader = csv.DictReader(csvfile, delimiter=args.csv_delimiter)
    i = 0
    morphs_of_morpheme = {}
    for row in reader:
        morpheme_list = row["MORPHEMES"].strip().split(args.name_separator)
        morph_list = row["MORPHS"].strip().split(args.morph_separator)
        if args.verbosity >= 25:
            print(row["MORPHEMES"])
            print(morpheme_list)
            print(row["MORPHS"])
            print(morph_list)
        i = i + 1
        if len(morpheme_list) != len(morph_list):
            print("** line", i, ":", row["MORPHEMES"],
                    "is incompatible with", row["MORPHS"])
            continue
        if not morpheme_list:
            continue
        stem_name_set.add(morpheme_list[0])
        name_morph_pair_lst = list(zip(morpheme_list, morph_list))
        seg_example_list.append(name_morph_pair_lst)
        for morpheme, morph in name_morph_pair_lst:
            if morpheme not in morphs_of_morpheme:
                morphs_of_morpheme[morpheme] = OrderedSet()
            morphs_of_morpheme[morpheme].add(morph.strip())
    csvfile.close()

    print("-- STEP 1 COMPLETED (seg_example_list, stem_name_set, morphs_of_morpheme done)--")

    # STEP 2:
    # align the allomorphs of each morpheme

    import twol.cfg as cfg
    cfg.all_zero_weight = 1.0

    import twol.multialign as multialign
    import twol.alphabet as alphabet
    
    alphabet.read_alphabet(args.alphabet)

    alignments = {}
    """All aligned morphs. index: morpheme name, value: sequence of
    aligned symbols.  Each aligned symbol has as many characters as
    there are items in the sequence.
    """

    for morpheme in sorted(morphs_of_morpheme.keys()):
        words = list(morphs_of_morpheme[morpheme])
        if len(words) == 1 and len(words[0]) == 0:
            ###aligned_sym_seq = ["Ø"]
            aligned_sym_seq = []
        else:
            if args.verbosity >= 20:
                print("words:", words)
            nz = args.extra_zeros 
            ####nz = 1 if len(words) > 10 else 2
            aligned_sym_seq = multialign.aligner(words, nz, morpheme)
        if args.verbosity >= 20:
            print("aligned_sym_seq:", aligned_sym_seq)
        alignments[morpheme] = aligned_sym_seq

    print("-- STEP 2 COMPLETED (alignments done) --")

    # STEP 3:
    # Compute the zero filled morphs out of the sequences of aligned symbols

    aligned_morphs = {}
    """index: (morpheme, morph), value: zero-filled morph
    """

    for morpheme, aligned_sym_seq in alignments.items():
        # e.g. "KOTA", ['kkkk', 'oooo', 'tdtd', 'aaØØ']
        if args.verbosity >= 25:
            print("aligned_sym_seq:", aligned_sym_seq)
        if morpheme not in aligned_morphs:
            aligned_morphs[morpheme] = collections.OrderedDict()
        if aligned_sym_seq:
            aligned_vec_seq = [tuple(grapheme.graphemes(aligned_sym))
                               for aligned_sym in aligned_sym_seq]
            l = len(aligned_vec_seq[0])
            zero_filled_morphs = ["".join([x[i] for x in aligned_vec_seq])
                                           for i in range(0,l)]
            original_morphs = [x.replace("Ø", "") for x in zero_filled_morphs] ##########
            for origm, zerofm in zip(original_morphs, zero_filled_morphs):
                #if origm:
                #    aligned_morphs[morpheme][origm] = zerofm
                aligned_morphs[morpheme][origm] = zerofm
        else:
            aligned_morphs[morpheme] = {"": ""}
    if args.verbosity >= 20:
        print("aligned_morphs", aligned_morphs)

    print("-- STEP 3 COMPLETED (aligned_morphs done) --")

    # STEP 4:
    # Write the example word forms plus their a zero filled morphs

    out_file = open(args.output, "w", newline="")
    writer = csv.DictWriter(out_file,
                            ["MORPHEMES","MORPHS","ZEROFILLED"],
                            delimiter=args.csv_delimiter)
    forms_of_morphs = {}

    writer.writeheader()
    d = {}
    for seg_example in seg_example_list:
        if args.verbosity >= 20:
            print("seg_example:", seg_example)
        morpheme_lst = [morpheme for morpheme, morph in seg_example]
        morph_lst = [morph for morpheme, morph in seg_example]
        zero_filled_morph_lst = [aligned_morphs[morpheme].get(morph.replace("Ø", ""), "")
                                  for (morpheme, morph) in seg_example]
        d["MORPHEMES"] = args.name_separator.join(morpheme_lst)
        d["MORPHS"] = args.morph_separator.join(morph_lst)
        d["ZEROFILLED"] = args.morph_separator.join(zero_filled_morph_lst)
        writer.writerow(d)
        if morph_lst[0] not in forms_of_morphs:
            forms_of_morphs[morph_lst[0]] = set()
        forms_of_morphs[morph_lst[0]].add(" ".join(x for x in morpheme_lst[1:]))

    print("-- STEP 4 COMPLETED (zero-filled morphs and the CSV file done) --")
    return

if __name__ == "__main__":
    main()
