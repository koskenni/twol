""" Forms morphophonemic representations out of zero-filled example word forms

    This program is free software under GPL 3 license

    Copyright Kimmo Koskenniemi 2017-2020
"""

def main():
    import re
    import csv
    import argparse

    version = "2020-02-01"

    argparser = argparse.ArgumentParser(
        "python3 raw2named.py",
        description="Renames raw morphophonemes. Version {} ".format(version))
    argparser.add_argument(
        "input",
        default="demo-raw.csv",
        help="aligned examples as a CSV file")
    argparser.add_argument(
        "output",
        default="demo-renamed.pstr",
        help="renamed examples as a space separated pair symbol strings")
    argparser.add_argument(
        "names",
        default="demo-renaming.csv",
        help="mapping from raw to neat morphophonemes as a CSV file,"\
        " default is ','")
    argparser.add_argument(
        "-d", "--delimiter",
        default=",",
        help="delimiter between raw name and new name fields, default is ','")
    argparser.add_argument(
        "-n", "--name-separator",
        default=".",
        help="Separator between morpheme names in the morpheme list,"\
        " default is '.'")
    argparser.add_argument(
        "-F", "--add-features",
        default=False, action="store_true",
        help="add affix morpheme names to the pairstring representation")
    argparser.add_argument(
        "-v", "--verbosity",
        default=0,
        type=int,
        help="level of diagnostic and debugging output")
    args = argparser.parse_args()

    import twol.cfg as cfg
    cfg.verbosity = args.verbosity

    mphon_name = { }

    # Read in the namefile is a CSV file which contains three fields:
    # 1. the raw (old) name for the mophophoneme
    # 2. a neat (new) name for the morphophoneme
    # 3. Comments documenting typical occurrences of the morphophoneme
    with open(args.names) as namefile:
        reader = csv.reader(namefile,
                            delimiter=args.delimiter,
                            skipinitialspace=True)
        for row in reader:
            if not row or (not row[0].strip()):
                continue
            if len(row) < 2:
                print("*** TOO FEW FIELDS IN:", row)
                continue
            if row[1].strip():
                mphon_name[row[0].strip()] = row[1].strip()

    #print(mphon_name)###

    outfil = open(args.output, "w")

    with open(args.input) as csvfile:
        reader = csv.DictReader(csvfile,
                                delimiter=args.delimiter,
                                skipinitialspace=True)
        for row in reader:
            zero_filled_str = row["ZEROFILLED"].strip().replace(".", "")
            raw_str = row["RAW"].strip()
            raw_lst = raw_str.split(" ")
            pairsym_lst = []
            if cfg.verbosity >= 20:
                print(row)
                print("raw_lst:", raw_lst)
            if len(raw_lst) != len(zero_filled_str):
                print("** LENGTHS DISAGREE **", raw_lst, zero_filled_str)
                continue

            for raw_insym, outsym in zip(raw_lst, zero_filled_str):
                if raw_insym == outsym:
                    psym = raw_insym
                else:
                    clean_insym = mphon_name.get(raw_insym, raw_insym)
                    psym = clean_insym + ":" + outsym
                pairsym_lst.append(psym)
            if args.add_features:
                morpheme_lst = row["MORPHEMES"].strip().split(args.name_separator)
                for morpheme in morpheme_lst[1:]:
                    pairsym_lst.append(morpheme + ":Ø")
            pairsym_str = " ".join(pairsym_lst)
            print(pairsym_str, file=outfil)

    return

if __name__ == "__main__":
    main()
