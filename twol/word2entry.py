# guessbygenerating.py

copyright = """Copyright © 2017, Kimmo Koskenniemi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from typing import List, Dict, Set, Tuple, NewType

PairSym = str
InSym = str # one mophophonemic symbol as a string
OutSym = str # ine surface symbol as a string
SymPair = Tuple[str, str]
InSymWord = str # a concatenation of InSyms
OutSymWord = str # a concatenation of OutSyms
ContClass = str # name of the next sublexicon in the lexicon
Entry = str # InSymWord + " " + Continuation

import hfst as hfst

State = int
##FST = NewType("FST", hfst.libhfst.HfstTransducer)
# <class 'hfst.libhfst.HfstTransducer'>
# <class 'hfst.libhfst.HfstInputStream'>

input_alphabet: Set[InSym] = set()
def main():

    import argparse

    argparser = argparse.ArgumentParser(
        "python3 gyessbygenerating.py",
        description=(
            "The program proposes possible entries for given input"
            " words, and generates principal forms of each candidate."
            " The user can then choose the correct entry among them."))
    argparser.add_argument(
        "-g", "--guesser",
        help="Guesser file FST",
        default="ofi3/ofiguess.ofst")
    argparser.add_argument(
        "-r", "--rules", 
        help="name of the two-level rule file",
        default="rules/rules-norm.fst")
    argparser.add_argument(
        "-p", "--suffixes", 
        help="name of the priincipal suffix file",
        default="principal-suffixes.json")
    argparser.add_argument(
        "-w", "--weights", 
        help=("Print the weighst of the proposed entries,"
              " default is not to print"),
        action="store_true", default=False)
    argparser.add_argument(
        "-v", "--verbosity", type=int,
        help="level of diagnostic output",
        default=0)
    args = argparser.parse_args()

    guesser_fil = hfst.HfstInputStream(args.guesser)
    guesser_fst = guesser_fil.read()
    guesser_fil.close()

    import re
    import sys

    import twol.twgenerate as twgenerate

    twgenerate.init(args.rules)

    import json

    suffix_file = open(args.suffixes, "r")
    suffix_lst_dic: Dict[str, List[InSymWord]] = json.load(suffix_file)
    suffix_file.close()
    #
    # suffix_list_dic now contains a mapping from entry types (e.g. "/s"
    # to a list of morphophonemic strings to be appended to the stem
    # in order to get the morphophonemic representations of the set of
    # principal forms of that stem.  E.g.:
    #
    #suffix_lst_dic = {
    #    "/s": ["", "n", "{nrs}{aä}", "{ij}{Øt}{aä}"],
    #    "/v": ["{dlnrtØ}{aä}", "n", "{i}{VØ}", "isi",
    #           "{C}", "{nlrs}{uy}{tØthn}{ØeØØØ}"],
    #    "/a": ["", "n", "{nrs}{aä}", "{ij}{Øt}{aä}", "m{pm}i"]
    #}

    print()
    for line_nl in sys.stdin:
        line = line_nl.strip()
        res_str = guesser_fst.lookup(line, output="text")
        if args.verbosity >= 10:
            print("lookup res_str =", res_str)
        res_lst: List[str] = res_str.split("\n")
        stem_cont_weight_lst: List[Tuple[InSymWord, ContClass, float]] = []
        entry_set: Set[Entry] = set()
        for res in res_lst:
            if not res.strip() or res.find("/") < 0:
                continue
            ### res = res.replace("_", "{§}") # word boundary *** check this solution
            if args.verbosity >= 10:
                print("res =", res)
            efw: Tuple[str, str, str] = res.partition("\t")
            entry_feat, tab, weight_str = efw
            ef: Tuple[Entry, str, str] = entry_feat.partition(";")
            (e, semicolon, feat) = ef
            entry = Entry(e)
            if entry in entry_set:
                continue
            else:
                entry_set.add(entry)
            sc: Tuple[Entry, str, ContClass] = entry.partition(" ")
            (stem, space, cont) = sc
            weight = float(weight_str.strip())
            stem_cont_weight_lst.append((stem.strip(),
                                         cont.strip(), weight))
        if not stem_cont_weight_lst:
            print("** NO GUESSES")
            continue
        if args.verbosity >= 20:
            print("lookup stem_cont_weight_lst =", stem_cont_weight_lst)
        best_w = min([weight for stem, cont, weight in stem_cont_weight_lst])
        stem_cont_weight_lst.sort(key = lambda scw : scw[2])
        i = 0
        for [stem, cont, weight] in stem_cont_weight_lst:
            i += 1
            suffix_lst = suffix_lst_dic.get(cont, [])
            word_lst = []
            for suffix in suffix_lst:
                generated_words = twgenerate.generate(stem+suffix)
                for word in generated_words:
                    word = word.replace("Ø", "")
                    word_lst.append(word)
            print("{}: {} ".format(i, cont), " ".join(word_lst))
        num = len(stem_cont_weight_lst)
        print(",".join([str(i + 1) for i in range(num)]),  "?")
        linenl = sys.stdin.readline()
        if not linenl: exit()
        line = linenl.strip()
        if re.fullmatch("([1-9][0-9]*)", line):
            i = int(line)
            if (i > 0) and (i <= len(stem_cont_weight_lst)):
                stem, cont, weight = stem_cont_weight_lst[i-1]
                print(stem, cont, "\n")
            else:
                print("--rejected ({})\n".format(i))
        else:
            print("--rejected\n")
    return

if __name__ == "__main__":
    main()
