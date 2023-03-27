"""A module for dicovering raw two-level rules from a set of carefully chosen examples

Examples, contexts and rules are treated in terms of strings without any
finite-state machinery or rule compilation.  Examples and contexts are
space separated sequences of pair-symbols. 

© Kimmo Koskenniemi, 2017-2023. Free software under the GPL 3 or later.
"""

import sys
import re
from collections import deque

import twol.cfg as cfg
from twol.cfg import pairsym2sympair, sympair2pairsym
import twol.twexamp as twexamp

pair_symbols_for_input = {}   # key: input symbol, value: set of pair symbols

def relevant_contexts(pair_symbol):
    """Select positive and negative contexts for a given pair-symbol
    
    pair_symbol -- the pair-symbol for which the contexts are selected
    
    returns a tuple of:
    
    pos_context_set -- a set of contexts in the examples in which the
    pair_symbol occurs
    
    neg_context_set -- a set of contexts where the input-symbol of the
    pair_symbol occurs with another output-symbol but so that there is
    no example in the example_set where the pair_symbol occurs in such a
    context
    """
    input_symbol, output_symbol = pairsym2sympair(pair_symbol)
    positive_context_set = set()
    negative_context_set = set()
    pairsymlist = [re.sub(r"([}{])", r"\\\1", psym)
                   for psym
                   in pair_symbols_for_input[input_symbol]]
    # print("pairsymlist:", pairsymlist) ##
    pattern = re.compile("|".join(pairsymlist))
    for example in cfg.example_set:
        for m in pattern.finditer(example):
            i1 = m.start()
            i2 = m.end()
            # print('"' + example[0:i1] +'"', '"' + example[i2:] + '"') ##
            left_context = ".#. " + example[0:i1-1]
            centre = example[i1:i2]
            if i2 >= len(example):
                right_context = ".#."
            else:
                right_context = example[i2+1:] + " .#."
            context = (left_context, right_context)
            # print(centre, context) ##
            if centre == pair_symbol:
                positive_context_set.add(context)
            else:
                negative_context_set.add(context)
    negative_context_set = negative_context_set - positive_context_set
    return positive_context_set, negative_context_set
    
subsets_dict = {
    "Vowel": ["Height", "Frontness", "Rounding"],
    "Height": ["Close", "CloseMid", "OpenMid", "Open"],
    "Close": [":i", ":y", ":u"],
    "CloseMid": [":e", ":ö", ":o"],
    "OpenMid": [":ä"],
    "Open": [":a"],
    "Frontness": ["Front", "Back"],
    "Front": [":i", ":y", ":e", ":ö", ":ä"],
    "Back": [":u", ":o", "a"],
    "Rounding": ["Rounded", "Unrounded"],
    "Rounded": [":y", ":u", ":ö", ":o"],
    "Unrounded": [":i", ":e", ":ä", ":a"],
}


def ppcontexts(ctxs, title):
    """Print a list of context for tracing and debugging"""
    print(title)
    for lc, rc in sorted(ctxs):
        print(lc, "_", rc)

def max_left_len(pos_context_set, neg_context_set):
    maxposlen = max([len(lc.split()) for lc, rc in pos_context_set])
    maxneglen = max([len(lc.split()) for lc, rc in neg_context_set])
    return max(maxposlen, maxneglen)

def max_right_len(pos_context_set, neg_context_set):
    maxposlen = max([len(rc.split()) for lc, rc in pos_context_set])
    maxneglen = max([len(rc.split()) for lc, rc in neg_context_set])
    return max(maxposlen, maxneglen)

def truncate_left(syms_to_remain, pos_context_set, neg_context_set):
    if cfg.verbosity >= 25:
        print(f"entering truncate_left, {syms_to_remain =}") ####
        print(f"{pos_context_set = }") ####
        print(f"{neg_context_set = }") ####
    new_pos_context_set = set()
    new_neg_context_set = set()
    for left_context, right_context in pos_context_set:
        left_lst = left_context.split()
        start = max(0, len(left_lst) - syms_to_remain)
        new_lc = " ".join(left_lst[start:])
        new_pos_context_set.add((new_lc, right_context))
    for left_context, right_context in neg_context_set:
        left_lst = left_context.split()
        start = max(0, len(left_lst) - syms_to_remain)
        new_lc = " ".join(left_lst[start:])
        new_neg_context_set.add((new_lc, right_context))

    if cfg.verbosity >= 25:
        print(f"leaving truncate_left, {syms_to_remain =}") ####
        print(f"{new_pos_context_set = }") ####
        print(f"{new_neg_context_set = }") ####
    return (new_pos_context_set, new_neg_context_set)
        

def truncate_right(syms_to_remain, pos_context_set, neg_context_set):
    if cfg.verbosity >= 25:
        print(f"entering truncate_right, {syms_to_remain =}") ####
        print(f"{pos_context_set = }") ####
        print(f"{neg_context_set = }") ####
    new_pos_context_set = set()
    new_neg_context_set = set()
    for left_context, right_context in pos_context_set:
        right_lst = right_context.split()
        new_rc = " ".join(right_lst[0:syms_to_remain])
        # print(f"{new_rc = }") ####
        new_pos_context_set.add((left_context, new_rc))
    for left_context, right_context in neg_context_set:
        right_lst = right_context.split()
        new_rc = " ".join(right_lst[0:syms_to_remain])
        new_neg_context_set.add((left_context, new_rc))

    if cfg.verbosity >= 25:
        print(f"leaving truncate_right, {syms_to_remain =}") ####
        print(f"{new_pos_context_set = }") ####
        print(f"{new_neg_context_set = }") ####
    return (new_pos_context_set, new_neg_context_set)
        
def surface_all(pos_context_set, neg_context_set):
    pairsym2outsym_map = {}
    for ctx_set in [pos_context_set, neg_context_set]:
        for ctx_pair in ctx_set:
            for ctx in ctx_pair:
                sym_lst = ctx.split()
                # print(f"{sym_lst = }") ####
                for pair_sym in sym_lst:
                    outsym = pairsym2sympair(pair_sym)[1]
                    # print(f"{pair_sym = }, {outsym = }") ####
                    if outsym == ".#.":
                        pairsym2outsym_map[pair_sym] = outsym
                    else:
                        pairsym2outsym_map[pair_sym] = ":" + outsym
    # print(f"{pairsym2outsym_map = }") ####
    new_pos_context_set = set()
    new_neg_context_set = set()
    for left_context, right_context in pos_context_set:
        new_left_ctx = [pairsym2outsym_map.get(pairsym, pairsym)
                        for pairsym in left_context.split()]
        new_rght_ctx = [pairsym2outsym_map.get(pairsym, pairsym)
                        for pairsym in right_context.split()]
        new_pos_context_set.add((" ".join(new_left_ctx),
                                 " ".join(new_rght_ctx)))
    for left_context, right_context in neg_context_set:
        new_left_ctx = [pairsym2outsym_map.get(pairsym, pairsym)
                        for pairsym in left_context.split()]
        new_rght_ctx = [pairsym2outsym_map.get(pairsym, pairsym)
                        for pairsym in right_context.split()]
        new_neg_context_set.add((" ".join(new_left_ctx),
                                 " ".join(new_rght_ctx)))
    if cfg.verbosity >= 20:
        print(f"{new_pos_context_set = }") ####
        print(f"{new_neg_context_set = }") ####
    return (new_pos_context_set, new_neg_context_set)


def search_reductions(agenda, pos_context_set, neg_context_set):
    """context_sets -- (positive_context_sets, negative_context_sets) where these sets are space-separated strings of pair symbols.
"""
    if cfg.verbosity >= 10:
        print(f"{agenda = }") ####

    if not agenda:                  # No more reductions to do.
        # print(f"final result: {pos_context_set = }, {neg_context_set = }") ####
        return pos_context_set, neg_context_set

    task = agenda.pop()             # Next step to be tested.
    # print(f"{task = }") ####
    op = task[0]

    # -- Start with truncatig all and then truncating less and less --
    if op == "truncate-left":
        [op, target_len] = task
        max_ll = max_left_len(pos_context_set,
                              neg_context_set)
        # print(f"{target_len = }, {max_ll = }") ####
        if target_len <= max_ll:            # possible to truncate
            # print(f"truncating, {target_len = }") ####
            (new_pos_ctx_set,
             new_neg_ctx_set) = truncate_left(target_len,
                                              pos_context_set,
                                              neg_context_set)
            good = new_pos_ctx_set.isdisjoint(new_neg_ctx_set)
        else:
            good = False
        # print(f"{good = }") ####
        if (not good) and (target_len < max_ll):  # Possible to go on trunc
            new_task = [op, target_len+1]
            # print(f"failing but pushing {new_task = }") ####
            agenda.append(new_task)     # Next attempt pushed into agenda

        if good:
            # print("succeeding and no further tasks created from this") ####
            return search_reductions(agenda,
                                     new_pos_ctx_set,
                                     new_neg_ctx_set)
        else:
            return search_reductions(agenda,
                                     pos_context_set,
                                     neg_context_set)

    # -- Start with truncatig all and then extend incrementally --
    elif op == "truncate-right":
        [op, target_len] = task
        max_rl = max_right_len(pos_context_set,
                               neg_context_set)
        # print(f"{target_len = }, {max_rl = }") ####
        if target_len > max_rl:            # Not possible to truncate
            # print("cannot go on with truncating less, giving up") ####
            good = False
        else:
            # print(f"truncating, {target_len = }") ####
            (new_pos_ctx_set,
             new_neg_ctx_set) = truncate_right(target_len,
                                               pos_context_set,
                                               neg_context_set)
            good = new_pos_ctx_set.isdisjoint(new_neg_ctx_set)
        # print(f"{good = }") ####
        if (not good) and (target_len < max_rl):  # Possible to go on trunc
            new_task = [op, target_len+1]
            # print(f"failing but pushing {new_task = }") ####
            agenda.append(new_task)     # Next attempt pushed into agenda

        if good:
            # print("succeeding and no further tasks created from this") ####
            return search_reductions(agenda,
                                     new_pos_ctx_set,
                                     new_neg_ctx_set)
        else:
            return search_reductions(agenda,
                                     pos_context_set,
                                     neg_context_set)
    elif op == "surface-all":
        (new_pos_ctx_set,
         new_neg_ctx_set) = surface_all(pos_context_set,
                                        neg_context_set)
        good = new_pos_ctx_set.isdisjoint(new_neg_ctx_set)
        # print(f"{good = }") ####
        if good:
            # -- Proceed with the reduced context sets --
            # print("succeeding and no further tasks created from this") ####
            # print(f"{agenda = }") ####
            return search_reductions(agenda,
                                     new_pos_ctx_set,
                                     new_neg_ctx_set)
        else:
            return search_reductions(agenda,
                                     pos_context_set,
                                     neg_context_set)


def print_rule(pair_symbol, operator, contexts):
    """Prints one rule"""
    print(pair_symbol, operator)
    rule_lst = ["    {} _ {}".format(lc, rc) for lc, rc in contexts]
    print(" ,\n".join(rule_lst) + " ;")
    return

def context_to_output_str(pairsym_str):
    """Converts a pair symbol string into its surface string"""
    pairsym_lst = pairsym_str.split()
    sympair_lst = [pairsym2sympair(psym) for psym in pairsym_lst]
    outsym_lst = [outsym for insym, outsym in sympair_lst]
    return "".join(outsym_lst)

def main():
    
    version = cfg.timestamp(__file__)
    
    import argparse
    import json
    
    arpar = argparse.ArgumentParser(
        "twol-discov",
        description="Deduces two-level rules out of"\
        " a file of examples.  The file must consist of"\
        " lines of space-separated pair string.  Such a file"\
        " can be produced e.g. by twol-raw2renamed program."\
        " Version {}".format(version))
    arpar.add_argument(
        "examples",
        help="Example pair strings file",
        default="test.pstr")
    arpar.add_argument(
        "-s", "--symbol",
        help="Input symbol for which to find rules."\
        " If not given then rules are proposed for"\
        " all morphophonemes in the example file",
        default="")
    arpar.add_argument(
        "-a", "--agenda",
        help="initial agenda for the context reductions",
        default="")

    arpar.add_argument(
        "-v", "--verbosity",
        help="Level of  diagnostic output, default is 5. Set to"\
        " 0 to omit the printing of relevant examples for the rules",
        type=int, default=5)
    args = arpar.parse_args()

    cfg.verbosity = args.verbosity

    # -- read in all examples --
    twexamp.read_examples(filename_lst=[args.examples], build_fsts=False)
    if cfg.verbosity >= 10:
        print("--- all examples read in ---")
    
    for insym in cfg.input_symbol_set:
        pair_symbols_for_input[insym] = set()
    for insym, outsym in cfg.symbol_pair_set:
        pair_symbol = sympair2pairsym(insym, outsym)
        pair_symbols_for_input[insym].add(pair_symbol)

    # -- expand a plain input symbol into a list of symbol pairs --
    if args.symbol in pair_symbols_for_input:
        pair_lst = []
        for pairsym in pair_symbols_for_input[args.symbol]:
            (insym, outsym) = pairsym2sympair(pairsym)
            pair_lst.append((insym, outsym))
        if cfg.verbosity >= 10:
            print(f"{pair_lst = }")
    elif args.symbol in cfg.pair_symbol_set:
        pair_lst = [pairsym2sympair(args.symbol)]
    else:
        print(f"Symbol {args.symbol!r} does not occur in the examples")
        lst = list(cfg.input_symbol_set)
        print("The following input symbols would be valid:\n",
              " ".join(sorted(lst)))
        exit("")

    if args.agenda:
        agenda_f = open(args.agenda, 'r')
        task_lst = list(json.load(agenda_f))
        print(f"{task_lst = }") ####
        initial_agenda = deque(reversed(task_lst))
    else:
        initial_agenda = deque([
            ["truncate-right", 0],
            ["truncate-left", 0],
            ["surface-all"],
        ])
        
    # -- collect the minimal contexts for each sym pair --
    pos_neg_contexts_lst = []
    for insym, outsym in pair_lst:
        if len(pair_symbols_for_input[insym]) <= 1:
            continue
        pair_symbol = sympair2pairsym(insym, outsym)

        (positive_contexts,
         negative_contexts) = relevant_contexts(pair_symbol)

        agenda = initial_agenda.copy()
        (pos_contexts,
         neg_contexts) = search_reductions(agenda,
                                           positive_contexts.copy(),
                                           negative_contexts.copy())

    # -- print the results collected
        if len(pos_contexts) <= len(neg_contexts) or cfg.verbosity > 0:
            print_rule(pair_symbol, "=>", pos_contexts)
        if len(pos_contexts) > len(neg_contexts) or cfg.verbosity > 0:
            print_rule(pair_symbol, "/<=", neg_contexts)

        if cfg.verbosity > 1:
            for lc, rc in positive_contexts:
                l_str = context_to_output_str(lc[3:])
                r_str = context_to_output_str(rc[:-3])
                print(f"!{l_str:>29}<{outsym}>{r_str}")

if __name__ == "__main__":
    main()
