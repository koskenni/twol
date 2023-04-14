"""A module for dicovering raw two-level rules from a set of carefully chosen examples

Examples, contexts and rules are treated in terms of strings without any
finite-state machinery or rule compilation.  Examples and contexts are
space separated sequences of pair-symbols. 

© Kimmo Koskenniemi, 2017-2023. Free software under the GPL 3 or later.
"""

import sys
import re
from collections import deque, defaultdict

import twol.cfg as cfg
from twol.cfg import pairsym2sympair, sympair2pairsym, pair_symbol_set
import twol.twexamp as twexamp
from typing import Dict, Set, Tuple

import twol.discopars as discopars

Context = Tuple[str, str]
ContextSet = Set[Context]
PairSym = str
SymPair = Tuple[str, str]
ContextSetPair = Tuple[ContextSet, ContextSet]

pairsym_set_for_insym: Dict[str, str] = {}   # key: input symbol, value: set of pair symbols

#=============================================================
def relevant_contexts(pair_symbol: PairSym) -> ContextSetPair:
    """ Select positive and negative contexts for a given pair-symbol
    
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
    positive_context_set: ContextSet = set()
    negative_context_set: ContextSet = set()
    pairsymlist = [re.sub(r"([}{])", r"\\\1", psym)
                   for psym
                   in pairsym_set_for_insym[input_symbol]]
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

def max_ctx_len(ctx_set: ContextSet) -> int:
    return max([len(lctx.split()) + len(rctx.split())
                for (lctx, rctx) in ctx_set])

def max_left_len(pos_context_set, neg_context_set):
    maxposlen = max([len(lc.split()) for lc, rc in pos_context_set])
    maxneglen = max([len(lc.split()) for lc, rc in neg_context_set])
    return max(maxposlen, maxneglen)

def max_right_len(pos_context_set:set, neg_context_set:set) -> int:
    maxposlen = max([len(rc.split()) for lc, rc in pos_context_set])
    maxneglen = max([len(rc.split()) for lc, rc in neg_context_set])
    return max(maxposlen, maxneglen)

#================================================================
def truncate_left(syms_to_remain: int,
                  pos_context_set: ContextSet,
                  neg_context_set: ContextSet) -> ContextSetPair:
    """Truncate the left contexts so that at most *syms_to_remain* symbols remain"""
    if cfg.verbosity >= 25:
        print(f"entering truncate_left, {syms_to_remain =}") ####
        print(f"{pos_context_set = }") ####
        print(f"{neg_context_set = }") ####
    new_pos_context_set: ContextSet = set()
    new_neg_context_set: ContextSet = set()
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

#=================================================================
def truncate_right(syms_to_remain: int,
                   pos_context_set: ContextSet,
                   neg_context_set: ContextSet) -> ContextSetPair:
    """Truncate the right contexts so that at most *syms_to_remain* symbols remain"""
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

#=============================================================
def reduce_set(set_name: str,
               symbol_set: set[str] ,
               pos_context_set: ContextSet,
               neg_context_set: ContextSet) -> ContextSetPair:
    """Occurrences on symbols in *symbol_lst* in positive and negative contest sets are replaced by *set_name* and the pair of resulting context sets is returned"""
    # print(f"in reduce_set: {set_name = }") ####
    # print(f"{symbol_set = }") ####
    new_pos_context_set: ContextSet = set()
    new_neg_context_set: ContextSet = set()
    for left_context, right_context in pos_context_set:
        new_left_ctx = [set_name if pairsym in symbol_set else pairsym
                        for pairsym in left_context.split()]
        new_rght_ctx = [set_name if pairsym in symbol_set else pairsym
                        for pairsym in right_context.split()]
        new_pos_context_set.add((" ".join(new_left_ctx),
                                 " ".join(new_rght_ctx)))
    for left_context, right_context in neg_context_set:
        new_left_ctx = [set_name if pairsym in symbol_set else pairsym
                        for pairsym in left_context.split()]
        new_rght_ctx = [set_name if pairsym in symbol_set else pairsym
                        for pairsym in right_context.split()]
        new_neg_context_set.add((" ".join(new_left_ctx),
                                 " ".join(new_rght_ctx)))
    if cfg.verbosity >= 20:
        print(f"{new_pos_context_set = }") ####
        print(f"{new_neg_context_set = }") ####
    return (new_pos_context_set, new_neg_context_set)
    

#==============================================================
def surface_all(pos_context_set: ContextSet,
                neg_context_set: ContextSet) -> ContextSetPair:
    """Return a pair of context sets where all pair symbols (e.g. "{tds}:s") have been reduced into surface symbols where the input symbol is open (e.g. ":s")."""
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
    new_pos_context_set: ContextSet = set()
    new_neg_context_set: ContextSet = set()
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

#==============================================================
def surface_some(pos_context_set: ContextSet,
                 neg_context_set: ContextSet) -> list[list]:
    """Return a list of set-reduction tasks, one for each surface symbol"""
    outsym2pairsym_map = defaultdict(set)
    outsym_set = set()
    for ctx_set in [pos_context_set, neg_context_set]:
        for ctx_pair in ctx_set:
            for ctx in ctx_pair:
                sym_lst = ctx.split()
                # print(f"{sym_lst = }") ####
                for pair_sym in sym_lst:
                    insym, outsym = pairsym2sympair(pair_sym)
                    # print(f"{pair_sym = }, {insym = }, {outsym = }") ####
                    if (pair_sym in pair_symbol_set) and (outsym != ".#."):
                        outsym_set.add(outsym)
                        outsym2pairsym_map[outsym].add(pair_sym)
    task_lst = []
    # print(f"{outsym2pairsym_map = }") ####
    for outsym in outsym2pairsym_map.keys():
        pairsym_lst = list(outsym2pairsym_map[outsym])
        # print(f"{outsym = }, {pairsym_lst = }") ####
        new_task = [":"+outsym]
        new_task.extend(pairsym_lst)
        # print(new_task) ####
        task_lst.append(new_task)
    if cfg.verbosity >= 10:
        print(f"{task_lst = }") ####
    return task_lst

#====================================================================
def search_reductions(agenda: list,
                      pos_context_set: ContextSet,
                      neg_context_set: ContextSet) -> ContextSetPair:
    """context_sets -- (positive_context_sets, negative_context_sets) where these sets are space-separated strings of pair symbols.
"""
    if cfg.verbosity >= 10:
        print(f"{agenda = }") ####

    if not agenda:                  # No more reductions to do.
        return pos_context_set, neg_context_set

    task = agenda.popleft()             # Next step to be tested.
    # print(f"{task = }") ####
    op = task[0]

    # -- Start with truncatig all and then truncating less and less --
    if op in {"truncate-left", "truncate-right"}:
        [op, target_len] = task
        if op == "truncate-left":
            max_len = max_left_len(pos_context_set, neg_context_set)
        else:
            max_len = max_right_len(pos_context_set, neg_context_set)
        if target_len <= max_len:           # possible to truncate
            if op == "truncate-left":
                (new_pos_ctx_set,
                 new_neg_ctx_set) = truncate_left(target_len,
                                                  pos_context_set,
                                                  neg_context_set)
            else:
                (new_pos_ctx_set,
                 new_neg_ctx_set) = truncate_right(target_len,
                                                   pos_context_set,
                                                   neg_context_set)
            good = new_pos_ctx_set.isdisjoint(new_neg_ctx_set)
        else:
            good = False
        # print(f"{good = }") ####
        if (not good) and (target_len < max_len): # Possible to go on trunc
            new_task = [op, target_len+1]
            # print(f"failing but pushing {new_task = }") ####
            agenda.appendleft(new_task)     # Next attempt pushed into agenda

        if good:
            # print("succeeding and no further tasks created from this") ####
            return search_reductions(agenda,
                                     new_pos_ctx_set,
                                     new_neg_ctx_set)
        else:
            return search_reductions(agenda,
                                     pos_context_set,
                                     neg_context_set)

    elif (op == "surface-some"):
        new_task_lst = surface_some(pos_context_set,
                                    neg_context_set)
        for new_task in new_task_lst:
            agenda.appendleft(new_task)
        return search_reductions(agenda,
                                 pos_context_set,
                                 neg_context_set)

    elif (op == "surface-all") or (op in cfg.definitions):
        if op == "surface-all":
            (new_pos_ctx_set,
             new_neg_ctx_set) = surface_all(pos_context_set,
                                            neg_context_set)
        elif op in cfg.definitions:
            (new_pos_ctx_set,
             new_neg_ctx_set) = reduce_set(op, cfg.definitions[op],
                                           pos_context_set,
                                           neg_context_set)
        else:
            exit(f"in search_reductions: {task = }")
        good = new_pos_ctx_set.isdisjoint(new_neg_ctx_set)
        # print(f"{good = }") ####
        if good:
            return search_reductions(agenda,
                                     new_pos_ctx_set,
                                     new_neg_ctx_set)
        else:
            return search_reductions(agenda,
                                     pos_context_set,
                                     neg_context_set)

    return (set(), set()) ## just to make mypy happy


def print_rule(pair_symbol: PairSym,
               operator: str,
               context_set: ContextSet,
               penalty: int) -> None:
    """Prints one rule"""
    print(f"{pair_symbol} {operator}\t\t! {penalty}")
    rule_lst = [f"    {lc} _ {rc}" for lc, rc in context_set]
    print(" ,\n".join(rule_lst) + " ;")

def context_to_output_str(pairsym_str: str) -> str:
    """Converts a pair symbol string into its surface string"""
    pairsym_lst = pairsym_str.split()
    sympair_lst = [pairsym2sympair(psym) for psym in pairsym_lst]
    outsym_lst = [outsym for insym, outsym in sympair_lst]
    return "".join(outsym_lst)

def right_ctx(ctx_pair):
    lft, rght = ctx_pair
    return rght

def context_set_penalty(context_set):
    width = max_ctx_len(context_set)
    height = len(context_set)
    sym_set = set()
    for ctx in context_set:
        left_str, right_str = ctx
        sym_set |= set(left_str.split())
        sym_set |= set(right_str.split())
    depth = len(sym_set)
    penalty = width * height * depth
    return penalty

def pos_neg_penalty(pos_context_set, neg_context_set):
    pos_penalty = context_set_penalty(pos_context_set)
    neg_penalty = context_set_penalty(neg_context_set)
    return (pos_penalty, neg_penalty)

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
        "-a", "--agendas",
        help="initial agenda for the context reductions",
        default="")
    arpar.add_argument(
        "-g", "--grammar",
        help="EBNF grammar which defines the syntax of the definitions",
        default="discovdef.ebnf")
    arpar.add_argument(
        "-d", "--definitions",
        help="definitions of pair symbol sets",
        default="setdefs.twol")

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
    
    parser = discopars.init(args.grammar)
    discopars.parse_defs(parser, args.definitions)
    #for nm, cs in cfg.definitions.items(): ###
    #    s_str = " ".join(sorted(list(cs))) ###
    #    print(f"{nm}: {s_str}\n")          ###

    for insym in cfg.input_symbol_set:
        pairsym_set_for_insym[insym] = set()
    for insym, outsym in cfg.symbol_pair_set:
        pair_symbol = sympair2pairsym(insym, outsym)
        pairsym_set_for_insym[insym].add(pair_symbol)

    # -- expand a plain input symbol into a list of symbol pairs --
    if args.symbol in cfg.input_symbol_set:
        pair_lst = []
        for pairsym in pairsym_set_for_insym[args.symbol]:
            pair_lst.append(pairsym)
        if cfg.verbosity >= 10:
            print(f"{pair_lst = }")
    elif args.symbol in cfg.pair_symbol_set:
        pair_lst = [args.symbol]
    else:
        print(f"Symbol {args.symbol!r} does not occur in the examples")
        lst = list(cfg.input_symbol_set)
        print("The following input symbols would be valid:\n",
              " ".join(sorted(lst)))
        exit("")

    if args.agendas:
        agenda_f = open(args.agendas, 'r')
        task_lst_lst = list(json.load(agenda_f))
        # print(f"{task_lst_lst = }") ####
    else:
        task_lst_lst = [[
            ["truncate-right", 0],
            ["truncate-left", 0],
            ["surface-all"],
        ]]
        
    # -- collect the minimal contexts for each sym pair --
    for pair_symbol in pair_lst:
        context_set_pair: ContextSetPair = relevant_contexts(pair_symbol)
        result_lst = []
        (positive_contexts,
         negative_contexts) = context_set_pair
        best_penalty = 999999999
        for task_lst in task_lst_lst:
            # print(f"in main: {task_lst = }")
            agenda = deque(task_lst.copy())
            res_ctx_pair: ContextSetPair= search_reductions(
                agenda,
                positive_contexts.copy(),
                negative_contexts.copy())
            (pos_contexts, neg_contexts) = res_ctx_pair
            # print_rule(pair_symbol, "=>", pos_contexts) ####
            # print(f"{pos_contexts = }\n{neg_contexts}") ####
            pos_pena, neg_pena = pos_neg_penalty(pos_contexts, neg_contexts)
            penalty = min(pos_pena, neg_pena)
            # print(f"In inner loop: {penalty = }") ####
            result_lst.append((pair_symbol,
                               pos_contexts, neg_contexts,
                               pos_pena, neg_pena,
                               task_lst))
            if penalty < best_penalty:
                best_penalty = penalty

        for (pair_symbol, pos_contexts, neg_contexts,
             pos_pena, neg_pena, task_lst) in result_lst:
            if cfg.verbosity > 1:
                print_rule(pair_symbol, "=>", pos_contexts, pos_pena)
            if cfg.verbosity > 1:
                print_rule(pair_symbol, "/<=", neg_contexts, neg_pena)
        
        # -- print the results collected
        pen = pos_neg_penalty(pos_contexts, neg_contexts)
        # print(f"in main, best result for {pair_symbol}, {penalty = }: ")  ####
        #if len(pos_contexts) <= len(neg_contexts) or cfg.verbosity > 1:
        #    print_rule(pair_symbol, "=>", pos_contexts, pos_pena)
        #if len(pos_contexts) > len(neg_contexts) or cfg.verbosity > 1:
        #    print_rule(pair_symbol, "/<=", neg_contexts, neg_pena)

        if cfg.verbosity > 0:
            insym, outsym = pairsym2sympair(pair_symbol)
            for lc, rc in sorted(positive_contexts, key=right_ctx):
                l_str = context_to_output_str(lc[3:])
                r_str = context_to_output_str(rc[:-3])
                print(f"!{l_str:>29}<{outsym}>{r_str}")
        # for res in result_lst: ####
        #    print(res) ####

if __name__ == "__main__":
    main()
