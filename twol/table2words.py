"""Reformats a paradigm table into a one word form per row csv file

© Kimmo Koskenniemi, 2017-2019

 This is free software under GPL 3 license.
"""

def step1():
    import csv, re, sys

    version = "2020-02-08"

    import argparse
    argparser = argparse.ArgumentParser(
        "python3 paratab2segcsv.py",
        description="Converts a tabular csv paradigm into"\
        " one example per row CSV file. Version {} ".format(version))
    argparser.add_argument(
        "input",
        default="ksk-paradigms.csv",
        help="Paradigm table as a CSV file")
    argparser.add_argument(
        "output",
        default="ksk-seg-examp.csv",
        help="One example per row paradigm as a CSV file")
    argparser.add_argument(
        "-s", "--morph-separator",
        default=".",
        help="Boundary between the morphs in a table cell")
    argparser.add_argument(
        "-d", "--csv-delimiter",
        default=",",
        help="CSV delimiter between the two fields, default is ','")
    argparser.add_argument(
        "-n", "--name-separator",
        default=".",
        help="Separator between morpheme names"\
        " in the morpheme list, default is '.'")
    argparser.add_argument(
        "-z", "--zero-symbol",
        default="Ø",
        help="Symbol to be inserted in word forms in order to"\
        " align them, default is Ø.  You are discouraged to change it.")
    args = argparser.parse_args()

    out_file = open(args.output, "w")
    writer = csv.DictWriter(out_file,
                            ["MORPHEMES","MORPHS"],
                            delimiter=args.csv_delimiter)
    writer.writeheader()
    d = {}

    morph_set = {}
    seg_ex_list = []
    with open(args.input, "r") as csvfile:
        reader = csv.DictReader(csvfile,
                                delimiter=args.csv_delimiter,
                                skipinitialspace=True)
        for row in reader:
            if row["ID"].startswith("?"):
                continue
            # process each cell of the row
            for column_label, words in row.items(): 
                if (not words) or (column_label in {"ID", "KSK"}) \
                   or ("STM" not in column_label):
                    continue
                morpheme_list = column_label.split(args.name_separator)
                if morpheme_list[0] == 'STM':
                    morpheme_list[0] = row['ID']
                words_clean = re.sub(r'[][()]', '', words)
                word_list = re.split(r"\s+", words_clean)
                for morphs in word_list:
                    if not morphs or morphs.find('*') >= 0:
                        continue
                    d["MORPHEMES"] = args.name_separator.join(morpheme_list).strip()
                    d["MORPHS"] = morphs
                    writer.writerow(d)
    out_file.close()
    return

if __name__ == "__main__":
    step1()
    
