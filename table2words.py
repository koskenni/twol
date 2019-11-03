"""Reformats a paradigm table into a one word form per row csv file

© Kimmo Koskenniemi, 2017-2018. This is free software under GPL 3 license.
"""

def step1():
    import csv, re, sys

    import argparse
    argparser = argparse.ArgumentParser("python3 paratab2segcsv.py",
                                        description="Converts a tabular csv paradigm into a example per row as a CSV file")
    argparser.add_argument("input",
                            default="ksk-paradigms.csv",
                            help="paradigm table as a CSV file")
    argparser.add_argument("output",
                            default="ksk-seg-examp.csv",
                            help="one example per row paradigm as a CSV file")
    argparser.add_argument("-s", "--morph-separator",
                            default=".",
                            help="separator between morphs in the word form")
    argparser.add_argument("-d", "--csv-delimiter",
                            default=",",
                            help="delimiter between the two fields")
    argparser.add_argument("-n", "--name-separator",
                            default=" ",
                            help="separator between morpheme names in the morpheme list")
    argparser.add_argument("-z", "--zero-symbol",
                            default="Ø",
                            help="symbol to be inserted in word forms in order to align them")
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
        reader = csv.DictReader(csvfile, delimiter=args.csv_delimiter)
        for row in reader:
            if row["ID"].startswith("?"):
                continue
            for column_label, words in row.items(): # process each cell of the row
                #words = row[column_label] # space separated string of words
                if not words or column_label in {"ID", "KSK"}:
                    continue
                morpheme_list = column_label.split(args.name_separator)
                if morpheme_list[0] == 'STM':
                    morpheme_list[0] = row['ID']
                words_clean = re.sub(r'[][()]', '', words)
                word_list = re.split(r"\s+", words_clean.strip())
                for morphs in word_list:
                    if not morphs or morphs.find('*') >= 0:
                        continue
                    d["MORPHEMES"] = args.name_separator.join(morpheme_list)
                    d["MORPHS"] = morphs
                    writer.writerow(d)
    out_file.close()
    return

if __name__ == "__main__":
    step1()
    
