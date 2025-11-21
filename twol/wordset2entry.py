"""Guesses a word entry from a set of word forms given by the user

© Kimmo Koskenniemi, 2017-2025

 This is free software under GPL 3 license.

"""

# guessbyasking.py

copyright = """Copyright © 2017, 2025, Kimmo Koskenniemi

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

import hfst as hfst
import sys
import re
import argparse
from collections import defaultdict

from typing import NewType

entry = NewType("entry", str)
lookup_item = NewType("lookup_item", tuple[str, int])

def entry_from_lookup_item(lu_item: lookup_item) -> tuple[entry, str, int]:
    entry_and_feats, weight = lu_item
    entr, semicol, feats = entry_and_feats.partition(";")
    return (entry(entr), feats, weight)
    
def main():
    argparser = argparse.ArgumentParser(
        "python3 guessbyasking.py",
        description="Guess lexicon entries by asking forms from the user")
    argparser.add_argument(
        "guesser",
        help="Guesser file FST")
    argparser.add_argument(
        "-r", "--reject",
        type=int, default=1000000,
        help=("reject candidates which are worse than the best by"
              " REJECTION or more")
    )
    argparser.add_argument(
        "-v", "--verbosity",
        type=int, default=0,
        help="level of diagnostic output")
    args = argparser.parse_args()

    guesser_fil = hfst.HfstInputStream(args.guesser)
    guesser_fst = guesser_fil.read()
    guesser_fil.close()

    print("\nENTER FORMS OF A WORD:\n")
    while True:
        remaining_set: set[entry] = set()
        remaining_lst: list[entry] = []
        weights: dict[entry, int] = defaultdict(int)
        # weights[entry] == weight
        first: bool = True
        res: list[lookup_item]
        while True:
            linenl: str = sys.stdin.readline()
            if not linenl: exit()
            line: str = linenl.strip()
            if line in {"", "0"} :
                print("GIVING UP THIS WORD\n\n")
                break
            if re.match("[1-9][0-9]*", line):
                e: str = remaining_lst[int(line)-1]
                print("\n" + "="*len(e))
                print(e)
                print("="*len(e) + "\n")
                break
            if line[0] == '-':
                res = guesser_fst.lookup(line[1:], output="tuple")
            else:
                res = guesser_fst.lookup(line, output="tuple")
            if args.verbosity >= 10:
                print("lookup result =", res)
            if len(res) == 0:
                print("FITS NO PATTERN! INGORED.")
                continue
            entry_set: set[entry] = set()
            for lu_item in res:
                (entr, feats, w) = entry_from_lookup_item(lu_item)
                entry_set.add(entr)
                weights[entr] = min(w, weights[entr])
            if first:
                first = False
                new_remaining_set = entry_set
            elif line[0] == '-':
                new_remaining_set = remaining_set - entry_set
            else:
                new_remaining_set = remaining_set & entry_set
            best_weight = min([weights[e] for e in new_remaining_set],
			      default=0)
            remaining_lst = []
            for e in new_remaining_set:
                if weights[e] <= best_weight + args.reject:
                    remaining_lst.append(e)
            remaining_lst.sort(key = lambda e : weights[e])
            if len(remaining_lst) == 1:
                e = remaining_lst[0]
                print("\n" + "="*len(e))
                print(e)
                print("="*len(e) + "\n")
                break
            elif not remaining_lst:
                print("DOES NOT FIT! IGNORED.")
            else:
                i = 0
                for entr in remaining_lst:
                    i += 1
                    w = weights[entr]
                    print("    ({}) {}  {}".format(i, entr, w))
                remaining_set = set(remaining_lst)



if __name__ == "__main__":
    main()

