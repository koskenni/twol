"""Proposes a rule for the distribution of one phoneme correspondence.

© Kimmo Koskenniemi, 2019. Free software under the GPL 3 or later.

A correspondence is a sequence of phonemes, e.g. "aaä" would be the
correspondence of phonemes "a", "a" and "ä".  The standard input
consists of cognate sets which are represented as a sequence of
correspondences. Correspondences where all phonemes are equal are
abbreviated as a single phoneme.

The command

 $ python3 multialign.py -l horizontal

can produce lines of such aligned cognate word forms, e.g.

  o r ji aØ

out of lines of space-separated cognate words, e.g.

  orja ori

"""

import cfg

corr_width = 0                  # number of languages
corr_set = set()                # set of all phoneme correspondences
context_dict = {}               # key: corr, value: list of contexts
phoneme_set = set()             # set of all phonemes in the correspondences

from collections import deque

def read_aligned_cognates(file_name):
    global corr_width
    alcog_file = open(file_name, "r")
    left_queue = deque([])
    right_queue = deque([])
    for line_nl in alcog_file:
        line = line_nl.strip()
        if line.startswith("!"):
            continue
        lst = line.split("!", maxsplit=1)
        alcog_str = lst[0]
        corr_lst = alcog_str.strip().split()
        mx = max([len(c) for c in corr_lst])
        if mx > corr_width:
            corr_width = mx
        left_queue.clear()
        left_queue.append("#")
        right_queue.clear()
        right_queue.extend(corr_lst)
        right_queue.append("#")
        while len(right_queue) > 1:
            center = right_queue.popleft()
            corr_set.add(center)
            if center not in context_dict:
                context_dict[center] = set()
            left_context = " ".join(left_queue)
            right_context = " ".join(right_queue)
            context_dict[center].add((left_context,right_context))
            left_queue.append(center)
    for corr in corr_set:
        for phoneme in corr:
            phoneme_set.add(phoneme)
    if cfg.verbosity >= 20:
        print(sorted(list(corr_set)))
        for corr, lst in context_dict.items():
            print_rule(corr, lst, "=>")
    return

corr_containing_group_syms = set()

rule_lst = []

def print_rule(corr, context_set, rule_type):
    lst = ["   " + left + " _ " + right
           for left, right in context_set]
    if lst:
        ####print(corr, rule_type)
        strg = " ,\n".join(sorted(lst)).replace("#", ".#.") + " ;"
        rule_lst.append(corr + " " + rule_type + "\n" + strg)
        for left, right in context_set:
            sym_lst = left.split()
            sym_lst.extend(right.split())
            for sym in sym_lst:
                if sym not in corr_set:
                    corr_containing_group_syms.add(sym)
    #else:
    #    rule_lst.append(corr + " => _ ;")
    return

def identity_corr(strg):
    return strg.count(strg[0]) == len(strg)

def collect_corrs(strg, lst):
    global group_expansion_set
    #print(">>>", group_expansion_set, strg, lst) ###
    if lst:
        for phon in lst[0]:
            collect_corrs(strg + phon, lst[1:])
    else:
        if identity_corr(strg):
            strg = strg[0]
        if strg in corr_set:
            group_expansion_set.update({strg})
            #print("<<<", strg, group_expansion_set) ###
            return

def near_correspondence(corr1, corr2, zero):
    n = 0
    z = True
    for (c1, c2) in zip(corr1, corr2):
        if c1 != c2:
            n = n + 1
        elif c1 == zero:
            z = False
    return n == 1 and z

def near_correspondences(corr, zero):
    near_set = []
    corr_expanded = corr_width * corr if len(corr) == 1 else corr
    for c in corr_set:
        c_expanded = corr_width * c if len(c) == 1 else c
        if near_correspondence(c_expanded, corr_expanded, zero):
            near_set.append(c)
    return sorted(near_set)

def symbol_count(context_string):
    l = len(context_string.split())
    return l

def truncate_left(context_set, left_len):
    new_set = set()
    for left, right in context_set:
        left_lst = left.split()
        if len(left_lst) >= left_len:
            new_set.add((" ".join(left_lst[1:]), right))
        else:
            new_set.add((left, right))
    return new_set
            
def truncate_right(context_set, right_len):
    new_set = set()
    for left, right in context_set:
        right_lst = right.split()
        if len(right_lst) >= right_len:
            new_set.add((left, " ".join(right_lst[:right_len - 1])))
        else:
            new_set.add((left, right))
    return new_set

group_lst = []
group_sets = {}

def read_groups(fil):
    skipping = True
    for line_nl in fil:
        line = line_nl.strip()
        if skipping and line == "GROUPS":
            skipping = False
            continue
        elif skipping or not line or line.startswith("#"):
            continue
        elif line == "END":
            break
        line = line.split("#", maxsplit=1)[0].strip()
        lst = line.split()
        group_lst.append(("".join(lst[1:]), lst[0]))
        phon_set = set()
        for letter in lst[1:]:
            if letter in phoneme_set:
                phon_set.add(letter)
            elif letter in group_sets:
                phon_set.update(group_sets[letter])
            else:
                print("***", letter, "***", line_nl)
        group_sets[lst[0]] = phon_set
    return

def reduce_string(input_string, symbol_string, set_symbol):
    global corr_width
    table = str.maketrans(symbol_string, len(symbol_string) * set_symbol)
    new_string = input_string.translate(table)
    new_string = new_string.replace(corr_width*set_symbol,set_symbol)
    return new_string

def reduce_context_set(context_set, symbol_string, set_symbol):
    new_set = set()
    for left, right in context_set:
        new_left = reduce_string(left, symbol_string, set_symbol)
        new_right = reduce_string(right, symbol_string, set_symbol)
        new_set.add((new_left, new_right))
    return new_set

if __name__ == "__main__":
    global group_expansion_set
    import argparse
    arpar = argparse.ArgumentParser("twol-histdiscov")
    arpar.add_argument(
        "algcognates",
        help="aligned cognates")
    arpar.add_argument(
        "-c", "--correspondence",
        help="one correspondence for which rules are proposed")
    arpar.add_argument(
        "-g", "--groups",
        help="file for alphabet and phoneme groups")
    arpar.add_argument(
        "-v", "--verbosity",
        help="level of  diagnostic output",
        type=int, default=0)
    args = arpar.parse_args()
    cfg.verbosity = args.verbosity

    read_aligned_cognates(args.algcognates)
    if args.groups:
        read_groups(open(args.groups, "r"))
        if args.verbosity >= 10:
            print("group_lst:", group_lst)

    if args.correspondence:
        correspondences = [args.correspondence]
    else:
        correspondences = sorted(list(corr_set))

    for corr in correspondences:
        ###if len(corr) == 1:
        ###    continue
        positives = context_dict[corr]
        if cfg.verbosity >= 3:
            print_rule(corr, positives, "=> ! trivial")
        negatives = set()
        for near_corr in near_correspondences(corr, "Ø"):
            ctx_set = context_dict[near_corr]
            for x in ctx_set:
                negatives.add(x)
        negatives.difference(positives)
        if cfg.verbosity >= 4:
            print_rule(corr, negatives, "/<= ! trivial")

        # Truncate the right context
        while True:
            right_len = max([symbol_count(right)
                            for left, right in positives | negatives])
            if right_len <= 0:
                break
            new_positives = truncate_right(positives, right_len)
            new_negatives = truncate_right(negatives, right_len)
            if new_positives & new_negatives:
                break
            else:
                positives = new_positives
                negatives = new_negatives
                if cfg.verbosity >= 5:
                    print_rule(corr, positives, "=> ! right truncated")
                    print_rule(corr, negatives, "/<= ! right truncated")

        # Truncate the left context
        while True:
            left_len = max([symbol_count(left)
                            for left, right in positives | negatives])
            if left_len <= 0:
                break
            new_positives = truncate_left(positives, left_len)
            new_negatives = truncate_left(negatives, left_len)
            if new_positives & new_negatives:
                break
            else:
                positives = new_positives
                negatives = new_negatives
                if cfg.verbosity >= 5:
                    print_rule(corr, positives, "=> ! left truncated")
                    print_rule(corr, negatives, "/<= ! left truncated")

        # Reduce according to a list of phoneme groups
        succeeded_groups = set()
        all_group_set = set(group_sets.keys())
        for sym_str, set_sym in group_lst:
            gs = group_sets[set_sym]
            gsg = gs & all_group_set
            if (gsg) and (not gsg <= succeeded_groups):
                continue
            new_positives = reduce_context_set(positives, sym_str, set_sym)
            new_negatives = reduce_context_set(negatives, sym_str, set_sym)
            if not (new_positives & new_negatives):
                positives = new_positives
                negatives = new_negatives
                succeeded_groups.add(set_sym)
                if cfg.verbosity >= 5:
                    print_rule(corr, positives, "=> ! " + set_sym + " reduced")
                    print_rule(corr, negatives, "/<= ! " + set_sym + " reduced")

        if len(positives) <= len (negatives) or len(positives) == 0:
            print_rule(corr, positives, "=>")
            if cfg.verbosity > 3:
                print_rule(corr, negatives, "/<=")
        else:
            print_rule(corr, negatives, "/<=")
            if cfg.verbosity > 3:
                print_rule(corr, positives, "=>")
        
    #print("corr_containing_group_syms:", corr_containing_group_syms) ###
    #print("group_sets:", group_sets) ###
    for corr in sorted(list(corr_containing_group_syms)):
        if corr == "#":
            continue
        if len(corr) == 1:
            expanded_corr = corr_width * corr
        else:
            expanded_corr = corr
        lst = []
        for letter in expanded_corr:
            if letter in phoneme_set:
                lst.append(set(letter))
            elif letter in group_sets:
                lst.append(group_sets[letter])
        #print("lst", corr, lst) ###
        group_expansion_set = set()
        collect_corrs("", lst)
        #print("group_expansion_set:", group_expansion_set) ###
        ls = sorted(list(group_expansion_set))
        print(corr, "=", " | ".join(ls), ";")

    for rule in rule_lst:
        print(rule)
