# discovery.py
# ============
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
from twol.cfg import definitions, symbol_pair_set
from twol.cfg import input_symbol_set, output_symbol_set
import twol.twexamp as twexamp
from typing import Dict, Set, Tuple

import twol.discopars as discopars

Context = Tuple[str, str]
ContextSet = Set[Context]
PairSym = str
SymPair = Tuple[str, str]

insym2pairsym_set: Dict[str, str] = defaultdict(set)
# key: input symbol, value: set of pair symbols

outsym2pairsym_set: Dict[str, str] = defaultdict(set)
# key: output symbol, value: set of pair symbols

positive_context_set = {}
negative_context_set = {}

#=============================================================
def relevant_contexts(pair_symbol: PairSym):
    """Select positive and negative contexts for a given pair-symbol
    
    pair_symbol -- the pair-symbol for which the contexts are selected
    
    positive_context_set[pair_symbol] -- set to a set of contexts in the
    examples in which the pair_symbol occurs
    
    negative_context_set[pair_symbol] -- a set of contexts where the
    input-symbol of the pair_symbol occurs with another output-symbol
    but so that there is no example in the example_set where the
    pair_symbol occurs in such a context

    """
    input_symbol, output_symbol = pairsym2sympair(pair_symbol)
    positive_ctx_set: ContextSet = set()
    negative_ctx_set: ContextSet = set()
    pairsymlist = [re.sub(r"([}{])", r"\\\1", psym) # eg. {ao}:o --> \{ao\}:o
                   for psym
                   in insym2pairsym_set[input_symbol]]
    # print(f"in relevant_contexts: {pairsymlist = }") ####
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
                positive_ctx_set.add(context)
            else:
                negative_ctx_set.add(context)
    negative_ctx_set = negative_ctx_set - positive_ctx_set

    positive_context_set[pair_symbol] = positive_ctx_set
    negative_context_set[pair_symbol] = negative_ctx_set
    
def max_left_len(pos_context_set: set) -> int:
    maxlen = max([len(lc.split()) for lc, rc in pos_context_set])
    return maxlen

def max_right_len(pos_context_set: set) -> int:
    maxlen = max([len(rc.split()) for lc, rc in pos_context_set])
    return maxlen

#================================================================
def truncate_left(syms_to_remain: int,
                  context_set: ContextSet
                  ) -> ContextSet:
    """Truncate the left contexts so that at most *syms_to_remain* symbols remain"""
    if cfg.verbosity >= 25:
        print(f"entering truncate_left, {syms_to_remain =}") ####
        print(f"{context_set = }") ####
    new_context_set: ContextSet = set()
    for left_context, right_context in context_set:
        left_lst = left_context.split()
        start = max(0, len(left_lst) - syms_to_remain)
        new_lc = " ".join(left_lst[start:])
        new_context_set.add((new_lc, right_context))

    if cfg.verbosity >= 25:
        print(f"leaving truncate_left, {syms_to_remain =}") ####
        print(f"{new_context_set = }") ####
    return new_context_set

#=================================================================
def truncate_right(syms_to_remain: int,
                   context_set: ContextSet
                   ) -> ContextSet:
    """Truncate the right contexts so that at most *syms_to_remain* symbols remain"""
    if cfg.verbosity >= 25:
        print(f"entering truncate_right, {syms_to_remain =}") ####
        print(f"{context_set = }") ####
    new_context_set = set()
    for left_context, right_context in context_set:
        right_lst = right_context.split()
        new_rc = " ".join(right_lst[0:syms_to_remain])
        # print(f"{new_rc = }") ####
        new_context_set.add((left_context, new_rc))

    if cfg.verbosity >= 25:
        print(f"leaving truncate_right, {syms_to_remain =}") ####
        print(f"{new_context_set = }") ####
    return new_context_set

#=============================================================
def reduce_set(set_name: str,
               symbol_set: set[str] ,
               pos_context_set: ContextSet,
               ) -> ContextSet:
    """Occurrences on symbols in *symbol_lst* in positive and negative contest sets are replaced by *set_name* and the pair of resulting context sets is returned"""
    # print(f"in reduce_set: {set_name = }") ####
    # print(f"{symbol_set = }") ####
    new_pos_context_set: ContextSet = set()
    for left_context, right_context in pos_context_set:
        new_left_ctx = [set_name
                        if (pairsym in symbol_set or
                            (definitions.get(pairsym,
                                             pair_symbol_set) <=
                             symbol_set)
                            ) else pairsym
                        for pairsym in left_context.split()]
        new_rght_ctx = [set_name
                        if (pairsym in symbol_set or
                            (definitions.get(pairsym,
                                             pair_symbol_set) <=
                             symbol_set)
                            ) else pairsym
                        for pairsym in right_context.split()]
        new_pos_context_set.add((" ".join(new_left_ctx),
                                 " ".join(new_rght_ctx)))
    if cfg.verbosity >= 20:
        print(f"{new_pos_context_set = }") ####
    return new_pos_context_set
    

#==============================================================
def surface_subset(pos_context_set: ContextSet,
                   subset_name: str
                   ) -> ContextSet:
    """Return a pair of context sets where all pair symbols in a given subset (e.g. "{tds}:s") have been reduced into surface symbols where the input symbol is open (e.g. ":s")."""
    pairsym2outsym_map = {}
    for ctx_pair in pos_context_set:
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
    subset = definitions[subset_name]
    for left_context, right_context in pos_context_set:
        new_left_ctx = [pairsym2outsym_map.get(pairsym, pairsym)
                        if pairsym in subset else pairsym
                        for pairsym in left_context.split()]
        new_rght_ctx = [pairsym2outsym_map.get(pairsym, pairsym)
                        if pairsym in subset else pairsym
                        for pairsym in right_context.split()]
        new_pos_context_set.add((" ".join(new_left_ctx),
                                 " ".join(new_rght_ctx)))
    if cfg.verbosity >= 20:
        print(f"{new_pos_context_set = }") ####
    return new_pos_context_set

#==============================================================
def mphon_subset(pos_context_set: ContextSet,
                 subset_name: str
                 )-> ContextSet:
    """Return a pair of context sets where pair symbols in a given subset (e.g. "{ij}:i") have been reduced into mphonemic symbols where the output symbol is open (e.g. "{ij}:")."""
    pairsym2insym_map = {}
    for ctx_pair in pos_context_set:
        for ctx in ctx_pair:
            sym_lst = ctx.split()
            # print(f"{sym_lst = }") ####
            for pair_sym in sym_lst:
                insym = pairsym2sympair(pair_sym)[0]
                # print(f"{pair_sym = }, {insym = }") ####
                if insym == ".#.":
                    pairsym2insym_map[pair_sym] = insym
                else:
                    pairsym2insym_map[pair_sym] =  insym + ":"
    # print(f"{pairsym2outsym_map = }") ####
    new_pos_context_set: ContextSet = set()
    subset = definitions[subset_name]
    for left_context, right_context in pos_context_set:
        new_left_ctx = [pairsym2insym_map.get(pairsym, pairsym)
                        if pairsym in subset else pairsym
                        for pairsym in left_context.split()]
        new_rght_ctx = [pairsym2insym_map.get(pairsym, pairsym)
                        if pairsym in subset else pairsym
                        for pairsym in right_context.split()]
        new_pos_context_set.add((" ".join(new_left_ctx),
                                 " ".join(new_rght_ctx)))
    if cfg.verbosity >= 20:
        print(f"{new_pos_context_set = }") ####
    return new_pos_context_set

#====================================================================

def overlap(set_lst: list[str],
            pairsym_lst: list[str]) -> bool:
    #print("in overlap: set_lst = {}".format(" ".join(set_lst))) #####
    #print("in overlap: pairsym_lst = {}".format(" ".join(pairsym_lst))) #####
    if len(set_lst) > len(pairsym_lst):
        pairsym_lst = pairsym_lst + ["XYZ"]*(len(set_lst) - len(pairsym_lst))
    for s, p in zip(set_lst, pairsym_lst):
        if s in definitions:
            if p not in definitions[s]:
                break
        else:
            if p != s:
                break
    else:
        #print(f"in overlap: return True") #####
        return True
    #print(f"in overlap: return False") #####
    return False

def pos_neg_is_disjoint(pos_ctx_set: ContextSet,
                        pair_symbol: PairSym) -> bool:
    #print(f"in pos_neg_is_disjoint: {pair_symbol = }")
    for pos_left_str, pos_rght_str in pos_ctx_set:
        pos_left_lst = list(reversed(pos_left_str.split()))
        #print(f"in pos_neg_is_disjoint: {pos_left_lst = }") #####
        pos_rght_lst = pos_rght_str.split()
        #print(f"in pos_neg_is_disjoint: {pos_rght_lst = }") #####
        for neg_left_str, neg_rght_str in negative_context_set[pair_symbol]:
            neg_left_lst = list(reversed(neg_left_str.split()))
            neg_rght_lst = neg_rght_str.split()
            if (overlap(pos_left_lst, neg_left_lst)
                and
                overlap(pos_rght_lst, neg_rght_lst)):
                #print("in pos_neg_is_disjoint: return False") #####
                #print(f"{pos_left_lst} _ {pos_rght_lst}") #####
                #print(f"{neg_left_lst} _ {neg_rght_lst}\n") #####
                return(False)
    #print("in pos_neg_is_disjoint: return True\n") #####
    return True
    
def pos_neg_is_subset(pos_ctx_set: ContextSet,
                      ctx_set: ContextSet) -> bool:
    for pos_left_str, pos_rght_str in pos_ctx_set:
        pos_left_lst = list(reversed(pos_left_str.split()))
        #print(f"in pos_neg_is_subset: {pos_left_lst = }") #####
        pos_rght_lst = pos_rght_str.split()
        #print(f"in pos_neg_is_subset: {pos_rght_lst = }") #####
        for neg_left_str, neg_rght_str in ctx_set:
            neg_left_lst = list(reversed(neg_left_str.split()))
            #print(f"in pos_neg_is_subset: {neg_left_lst = }") #####
            neg_rght_lst = neg_rght_str.split()
            #print(f"in pos_neg_is_subset: {neg_rght_lst = }") #####
            if (overlap(pos_left_lst, neg_left_lst)
                and
                overlap(pos_rght_lst, neg_rght_lst)):
                break
        else:
            #print("in pos_neg_is_subset: return False\n") #####
            return False
    #print("in pos_neg_is_subset: return True\n") #####
    return True
    

#====================================================================
def search_reductions(agenda: list,
                      pair_symbol: PairSym,
                      pos_context_set: ContextSet,
                      ) -> ContextSet:
    """context_sets -- (positive_context_sets, negative_context_sets)
where these sets are space-separated strings of pair symbols.

    """
    if cfg.verbosity >= 10:
        print(f"in search_reductions, {agenda = }") ####

    if not agenda:                  # No more reductions to do.
        return pos_context_set

    task = agenda.popleft()             # Next step to be tested.
    if type(task) is str:
        op = task
    elif type(task) is dict:
        op = task["op"]
    else:
        exit(1)
    if cfg.verbosity >= 10:
        print(f"in search_reductions: {op = }, {task = }")

    # -- Start with truncatig all and then truncating less and less --
    if op == "truncate":
        side = task["side"]
        target_len = task.get("minimum", 0)
        if side == "left":
            max_len = max_left_len(pos_context_set)
        else:
            max_len = max_right_len(pos_context_set)
        if target_len <= max_len:           # possible to truncate
            if side == "left":
                new_pos_ctx_set = truncate_left(target_len,
                                                pos_context_set)
            else:
                new_pos_ctx_set = truncate_right(target_len,
                                                   pos_context_set)
            good = pos_neg_is_disjoint(new_pos_ctx_set, pair_symbol) # ***
        else:
            good = False
        # print(f"{good = }") ####
        if (not good) and (target_len < max_len): # Possible to go on trunc
            new_task = {"op": op, "side": side, "minimum": target_len+1}
            # print(f"in search_reductions, failing but pushing {new_task = }") ####
            agenda.appendleft(new_task)     # Next attempt pushed into agenda

        if good:
            # print("succeeding and no further tasks created from this") ####
            return search_reductions(agenda, pair_symbol, new_pos_ctx_set)
        else:
            return search_reductions(agenda, pair_symbol, pos_context_set)

    elif (op == "surface"):
        subset_name = task.get("set", "None")
        new_pos_ctx_set = surface_subset(pos_context_set,
                                         subset_name)
        # print_context_set(f"from surface_subset {subset_name}", new_pos_ctx_set) ######
        if pos_neg_is_disjoint(new_pos_ctx_set,
                               pair_symbol): # ***
            return search_reductions(agenda, pair_symbol,
                                     new_pos_ctx_set)
        else:
            return search_reductions(agenda, pair_symbol,
                                     pos_context_set)
    elif (op == "mphon"):
        subset_name = task.get("set", "None")
        new_pos_ctx_set = mphon_subset(pos_context_set,
                                       subset_name)
        if pos_neg_is_disjoint(new_pos_ctx_set,
                               pair_symbol): # ***
            return search_reductions(agenda, pair_symbol,
                                     new_pos_ctx_set)
        else:
            return search_reductions(agenda, pair_symbol,
                                     pos_context_set)
    elif (op in definitions):
        # print(f"in search_reductions, entering reduce_set({op},...)") ####
        new_pos_ctx_set = reduce_set(op, definitions[op],
                                     pos_context_set)
        #print_context_set(f"from reduce_set {op}", new_pos_ctx_set) ######
        if pos_neg_is_disjoint(new_pos_ctx_set,
                               pair_symbol): # ***
            return search_reductions(agenda, pair_symbol,
                                     new_pos_ctx_set)
        else:
            return search_reductions(agenda, pair_symbol,
                                     pos_context_set)
    elif m := re.match("^:(?P<outsym>[^\W_0-9])$", op):
        if ((outsym := m.group("outsym")) not in input_symbol_set):
            print(f"in search_reductions, invalid surf sym: {outsym}") ####
            exit(1)
        # print(f"in search_reductions, entering surface_one({op})") ####
        new_pos_ctx_set = surface_one(m.group("outsym"),
                                      pos_context_set)
        if pos_neg_is_disjoint(new_pos_ctx_set, pair_symbol): # ***
            return search_reductions(agenda, pair_symbol,
                                     new_pos_ctx_set)
        else:
            return search_reductions(agenda, pair_symbol,
                                     pos_context_set)
        
    else:
        print(f"in search_reductions, exiting with invalid task: {task = }")
        exit(1)
    return set() ## just to make mypy happy


def context_to_output_str(pairsym_str: str) -> str:
    """Converts a pair symbol string into its surface string"""
    pairsym_lst = pairsym_str.split()
    sympair_lst = [pairsym2sympair(psym) for psym in pairsym_lst]
    outsym_lst = [outsym for insym, outsym in sympair_lst]
    return "".join(outsym_lst)

def context_set_penalty(context_set):
    width = max_left_len(context_set) + max_right_len(context_set)
    height = len(context_set)
    sym_set = set()
    for ctx in context_set:
        left_str, right_str = ctx
        sym_set |= set(left_str.split())
        sym_set |= set(right_str.split())
    depth = len(sym_set)
    penalty = width * height * depth
    return penalty

def print_rule(result,
               penalty: int,
               operator: str) -> None:
    """Prints one rule"""
    pair_symbol = result["pairsym"]
    context_set = result["posctx"]
    print(f"{pair_symbol} {operator}\t\t! {penalty}")
    rule_lst = [f"    {lc} _ {rc}" for lc, rc in context_set]
    print(" ,\n".join(rule_lst) + " ;")

def print_context_set(msg: str, context_set: ContextSet) -> None:
    print(msg)
    rule_lst = [f"    {lc} _ {rc}" for lc, rc in context_set]
    print(" ,\n".join(rule_lst) + " ;")

def process_results_into_rules(pairsym_lst, result_lst_lst):
    # process resulte for each recipe
    for result_lst in result_lst_lst:
        assert len(pairsym_lst) == len (result_lst)
        recipe = result_lst[0]["recipe"]
        if cfg.verbosity > 0:
            print("\n! recipe:")
            for task in recipe:
                print(f"!\t\t{task}")
        srt_res_lst = sorted(result_lst, key=lambda x: x["pospena"])
        # simpler if just two possible outsyms for this insym
        if len(result_lst) == 2222:
            result = srt_res_lst[0]
            pair_symbol = result["pairsym"]
            set_lst = result["posctx"]
            #print_context_set("positive contexts", set_lst) ####
            other_result = srt_res_lst[1]
            other_pairsym = other_result["pairsym"]
            ctx_set = negative_context_set[other_pairsym]
            # print_context_set(f"neg ctx set of {other_pairsym = }", ctx_set) ######
            if pos_neg_is_subset(set_lst,
                                 ctx_set):
                weight = result["pospena"]
                print_rule(result, result["pospena"], "<=>")
            else:
                weight = (other_result["pospena"] +
                          result["pospena"])
                print_rule(result, result["pospena"], "=>")
                print_rule(other_result, other_result["pospena"], "=>")
        # the general case with any num of outsyms for this insym
        else:
            success = True
            for result in srt_res_lst:
                pair_sym = result["pairsym"]
                weight = result["pospena"]
                pos_ctx_set = result["posctx"]
                exclusive = True
                for other_result in srt_res_lst:
                    if other_result == result:
                        continue
                    other_pair_sym = other_result["pairsym"]
                    other_neg_ctx_set = negative_context_set[other_pair_sym]
                    if not pos_neg_is_subset(pos_ctx_set,
                                             other_neg_ctx_set):
                        exclusive = False
                        success = False
                        break
                if exclusive:
                    if not(success and result == srt_res_lst[-1]):
                        print_rule(result, weight, "<=>")
                else:
                    print_rule(res, res["posctx"], "=>")

def main():
    
    version = cfg.timestamp(__file__)

    global outsym2pairsym_set
    import argparse
    import json
    
    arpar = argparse.ArgumentParser(
        "twol-discov",
        description=f"Deduces two-level rules out of"\
        " a file of examples.  The file must consist of"\
        " lines of space-separated pair string.  Such a file"\
        " can be produced e.g. by twol-raw2renamed program."\
        " Version: {version}")
    arpar.add_argument(
        "examples",
        help="Example pair strings file.",
        default="test.pstr")
    arpar.add_argument(
        "-s", "--symbol",
        help="Input symbol for which rules are produced.",
        default="")
    arpar.add_argument(
        "-a", "--agendas",
        help="Initial agenda for the context reductions.",
        default="")
    arpar.add_argument(
        "-g", "--grammar",
        help="EBNF grammar which defines the syntax of the definitions.",
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
    if cfg.verbosity >= 10:
        for nm, cs in definitions.items():
            s_str = " ".join(sorted(list(cs)))
            print(f"{nm}: {s_str}\n")

    for insym, outsym in symbol_pair_set:
        pair_symbol = sympair2pairsym(insym, outsym)
        insym2pairsym_set[insym].add(pair_symbol)
        outsym2pairsym_set[outsym].add(pair_symbol)
    for insym, symset in insym2pairsym_set.items():
        definitions[insym + ":"] = symset
    for outsym, symset in outsym2pairsym_set.items():
        definitions[":" + outsym] = symset
    #print(f"in main: {definitions =}") ####

    # -- expand a plain input symbol into a list of symbol pairs --
    if args.symbol in input_symbol_set:
        pairsym_lst = []
        for pairsym in insym2pairsym_set[args.symbol]:
            pairsym_lst.append(pairsym)
        if cfg.verbosity >= 10:
            print(f"{pairsym_lst = }")
    elif args.symbol in pair_symbol_set:
        pairsym_lst = [args.symbol]
    else:
        print(f"Symbol {args.symbol!r} does not occur in the examples")
        lst = list(input_symbol_set)
        print("The following input symbols would be valid:\n",
              " ".join(sorted(lst)))
        exit("")

    for pairsym in pairsym_lst:
        relevant_contexts(pairsym)

    if args.agendas:
        agenda_f = open(args.agendas, 'r')
        task_lst_lst = list(json.load(agenda_f))
        # print(f"{task_lst_lst = }") ####
    else:
        task_lst_lst = [[{"op": "truncate", "side": "left"},
	                 {"op": "truncate", "side": "right"}]]

    result_lst_lst = []
    # try each recipe in the task_lst_lst
    for task_lst in task_lst_lst:
        result_lst = []
        agenda = deque(task_lst.copy())
        # -- collect the minimal contexts for each sym pair --
        for pair_symbol in pairsym_lst:
            result_pos_ctx_set: ContextSet = search_reductions(
                agenda.copy(),
                pair_symbol,
                positive_context_set[pair_symbol].copy())
            # print(f"{pos_contexts = }\n{neg_contexts}") ####
            pos_pena = context_set_penalty(result_pos_ctx_set)
            result_lst.append({"pairsym": pair_symbol,
                               "posctx": result_pos_ctx_set,
                               "pospena": pos_pena,
                               "recipe": task_lst})

        for result in result_lst:
            if cfg.verbosity > 1 :
                print_rule(result, result["pospena"], "=>")
        result_lst_lst.append(result_lst)
        
    process_results_into_rules(pairsym_lst, result_lst_lst)
    
    if cfg.verbosity > 1:
        for pair_symbol in pairsym_lst:
            insym, outsym = pairsym2sympair(pair_symbol)
            pos_ctx_lst = list(positive_context_set[pair_symbol]) # ********
            for lc, rc in pos_ctx_lst:
                l_str = context_to_output_str(lc[3:])
                r_str = context_to_output_str(rc[:-3])
                print(f"!{l_str:>29}<{outsym}>{r_str}")

if __name__ == "__main__":
    main()
