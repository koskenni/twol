"""A script for converting zero-filled examples into examples with raw morphophonemes

Raw morphophonemes are named according to a set of principal forms
(principal parts) which are assumed to reflect all morphophonemic
alternations in a lexeme.  The script assumes that the examples within
a lexeme occur all in the same order as for their form.

In order to apply this script to another language, one must revise the
principal_set and the feat2mphons values.  The code still relies on
the assumption that the stem comes as the first morph (and thus some
minor modifications would be required in order to handle prefixing
languages).

© Kimmo Koskenniemi, 2018. This is free software under GPL 3 license.
"""

def main():
    import argparse
    argparser = argparse.ArgumentParser(
        "python3 zerofilled2raw.py",
        description="Forms raw morphophonemes out of zero-filled morphs")
    argparser.add_argument(
        "input",
        default="ksk-zerofilled.csv",
        help="zero-filled example words as a CSV file")
    argparser.add_argument(
        "output",
        default="ksk-raw-examp.csv",
        help="example word with raw morhpophonemes as a CSV file")
    argparser.add_argument(
        "affix_info",
        default="demo-affix-info.csv",
        help="principal forms and morphophonemic affixes as a CSV file")
    argparser.add_argument(
        "-s", "--morph-separator",
        default=".",
        help="separator between morphs in the word form")
    argparser.add_argument(
        "-d", "--csv-delimiter",
        default=",",
        help="delimiter between the fields")
    argparser.add_argument(
        "-n", "--name-separator",
        default=" ",
        help="separator between morpheme names in the morpheme list")
    argparser.add_argument(
        "-z", "--zero-symbol",
        default="Ø",
        help="symbol inserted in word forms to align them")
    argparser.add_argument(
        "-v", "--verbosity",
        default=0,
        type=int,
        help="level of diagnostic and debugging output")
    args = argparser.parse_args()

    import re
    import csv
    from collections import OrderedDict
    from orderedset import OrderedSet

    principal_set = OrderedSet()
    """"Set of principal forms or principal parts, i.e. the forms which
    uniquely determine the morphophonemic variations that may occur
    within the stem
    """
    feat2mphons = {}

    # Read in the feature combinations of principal forms and
    # the morphophonemic representations of affix features
    with open(args.affix_info, "r") as afffil:
        affrdr = csv.reader(afffil, delimiter=args.csv_delimiter)
        for row in affrdr:
            if row[1] == '+':
                principal_set.add(row[0])
            else:
                feat2mphons[row[0]] = row[1]
    #print("principal_set =", principal_set)####
    #print("feat2mphons =", feat2mphons)####

    # Read in the morpheme names and the zero-filled morphs

    stem_morpheme_data = OrderedDict()
    """Indexed by stem morpheme name, value is a list of the original data
    for that stem morpheme.  Each value consists of a tuple of fields
    (MORPHEMES, MORPHS, ALIGNED) in the original data.
    """
    with open(args.input, "r") as infil:
        rdr = csv.DictReader(infil, delimiter=args.csv_delimiter)
        for row in rdr:
            names = row["MORPHEMES"].strip()
            orig_morphs = row["MORPHS"].strip()
            zerof_morphs = row["ZEROFILLED"].strip()
            if (not names) or (not zerof_morphs):
                continue
            name_lst = names.split(args.name_separator, maxsplit=1)
            stem_name = name_lst[0]
            form_name = " ".join(name_lst[1:]) if len(name_lst) > 1 else ""
            zerof_morph_lst = zerof_morphs.split(args.morph_separator,
                                                 maxsplit=1)
            if stem_name not in stem_morpheme_data:
                stem_morpheme_data[stem_name] = []
            stem_morpheme_data[stem_name].append((form_name, orig_morphs,
                                                  zerof_morph_lst))

    ofil = open(args.output, "w")
    writer = csv.DictWriter(ofil, fieldnames=["MORPHEMES", "MORPHS",
                                              "ZEROFILLED", "RAW"])
    writer.writeheader()

    for stem_morpheme, data_lst in stem_morpheme_data.items():
        princ_zstem_lst =[]
        # select the principal forms of this stem morpheme
        for data in data_lst:
            form_name, orig_morphs, zerof_morph_lst = data
            if form_name in principal_set:
                princ_zstem_lst.append(zerof_morph_lst[0])
        # form the raw morphophonemes by combining corresponding
        # symbols
        l = len(princ_zstem_lst[0])
        zstem_rawsym_lst = []
        for i in range(l):
            lst = []
            for princ_zstem in princ_zstem_lst:
                lst.append(princ_zstem[i])
                # print(stem_morpheme, i, lst)###
            raw_seq = "".join(lst)
            if re.match(r"^(.)(\1)*$", raw_seq):
                raw_sym = raw_seq[0]  # abbreviate if all identical
            else:
                raw_sym = "{" + raw_seq + "}"
            zstem_rawsym_lst.append(raw_sym)
        zstem_pairsym_str = " ".join(zstem_rawsym_lst)
        # Output the data augmented with the representation with raw
        # morphophonemes
        for data in data_lst:
            form_name, orig_morphs, zerof_morph_lst = data
            row["MORPHEMES"] = (stem_morpheme + " " + form_name).strip() 
            row["MORPHS"] = orig_morphs
            orig_zerof_morphs = args.morph_separator.join(zerof_morph_lst)
            row["ZEROFILLED"] = orig_zerof_morphs
            raw_lst = [zstem_pairsym_str]
            feat_lst = form_name.split(" ")
            for feat in feat_lst:
                raw_lst.append(feat2mphons[feat])
            row["RAW"] = " ".join(raw_lst)
            writer.writerow(row)
    return

if __name__ == "__main__":
    main()
