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
from typing import List, Dict, Set, Tuple, DefaultDict, Deque

import twol.discopars as discopars

Context = Tuple[str, str]
ContextSet = Set[Context]
PairSym = str
SymPair = Tuple[str, str]
Result = Dict
ResultList = List[Result]

insym2pairsym_set: DefaultDict[str, set] = defaultdict(set)
# key: input symbol, value: set of pair symbols

outsym2pairsym_set: DefaultDict[str, set] = defaultdict(set)
# key: output symbol, value: set of pair symbols

positive_context_set = {}
negative_context_set = {}

#=============================================================
def relevant_contexts(pair_symbol: PairSym) -> None:
    """Select positive and negative contexts for a given pair-symbol
    
    :parameter pair_symbol:  The pairsym for which the contexts are selected.
    
    Sets a global variable ``positive_context_set[pair_symbol]`` to a set of those contexts in the examples in which the pair_symbol occurs
    
    Sets a global variable ``negative_context_set[pair_symbol]`` to a set of contexts where the input-symbol of the pair_symbol occurs with another output-symbol but so that there is no example in the example_set where the pair_symbol occurs in such a context.

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
    """Truncate the left contexts

    :parameter syms_to_remain: A minimum number of pair symbols to remain in the left context.

    :parameter context_set:  A set of (positive) contexts to be truncated.

    :returns: A new context set where left contexts are truncated

"""
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
    """Truncate the right contexts

    :parameter syms_to_remain: A minimum number of pair symbols to remain in the right context.

    :parameter context_set:  A set of (positive) contexts to be truncated.

    :returns: A new context set where right contexts are truncated

"""
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
               pos_context_set: ContextSet,
               ) -> ContextSet:
    """
    Reduce contexts by substituting pair symbols with set names

    :parameter set_name: A name of a pairsym set in definitions.

    :parameter pos_context_set:  A set of contexts to which the reduction is to be applied.

    :returns: A new set of contexts where every occurrence of pairsyms in ``definitions[set_name]`` have been substituted with ``set_name``.

"""
    symbol_set = definitions[set_name]
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
    """
    Reduce the contexts by substituting insym:outsym pairs with :outsym

    :parameter pos_context_set:  The set of contexts to be reduced

    :parameter subset_name:  A defined subset whose sympairs are considered for reduction.

    :returns:  A new context set where all occurences of pairsyms (``insym:outsym``) in ``definitions[subset_name]`` are replaced with (``:outsym``), e.g. ``{tds}:s`` have been reduced into e.g. ``:s``.

"""
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
    """Reduces a set of contexts by replacing e.g. {ij}:i with {ij}:

    :param pos_context_set:  A set of positive context which might be truncated and already reduced.

    :param subset_name:  Only pairs which are in definitions[subset_name] are reduced.

    :returns: A modified context set where pair symbols (insym:outsym) belonging to the given subset have been reduced into (insym:).

"""
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

def print_context_set(msg: str, context_set: ContextSet) -> None:
    print(msg)
    rule_lst = [f"    {lc} _ {rc}" for lc, rc in context_set]
    print(" ,\n".join(rule_lst) + " ;")

#====================================================================

def overlap(set_lst: list[str],
            pairsym_lst: list[str]) -> bool:
    """Tests whether list of set names covers the list of pairsyms

    :param set_lst:  List of pair symbols or names of defined sets

    :param pairsym_lst:  List of pair symbols.  If shorter than set_lst, the match fails.

    :returns: True if each pairsym in the latter list is included in a respective set name (or pairsym) in the former list

    """
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
                        other_ctx_set: ContextSet) -> bool:
    """
    Tests whether a pos context set is disjoint from a negative one

    :parameter pos_ctx_set:  A set of left and right context pairs where the contexts are represented as space-separated strings of pair symbols or set names.  

    :parameter other_ctx_set:  A context set to which the pos context is compared.  The contexts are space-separated strings of pair symbols.

    :returns:  True if the context sets are logically disjoint.

"""
    #print_context_set(f"in pos_neg_is_disjoint: {pair_symbol = }",
    #                  pos_ctx_set) #####
    for pos_left_str, pos_rght_str in pos_ctx_set:
        pos_left_lst = list(reversed(pos_left_str.split()))
        #print(f"in pos_neg_is_disjoint: {pos_left_lst = }") #####
        pos_rght_lst = pos_rght_str.split()
        #print(f"in pos_neg_is_disjoint: {pos_rght_lst = }") #####
        for neg_left_str, neg_rght_str in other_ctx_set:
            neg_left_lst = list(reversed(neg_left_str.split()))
            neg_rght_lst = neg_rght_str.split()
            if (overlap(pos_left_lst, neg_left_lst)
                and
                overlap(pos_rght_lst, neg_rght_lst)):
                #print(f"{pos_left_lst} _ {pos_rght_lst}") #####
                #print(f"{neg_left_lst} _ {neg_rght_lst}\n") #####
                #print("in pos_neg_is_disjoint: return False") #####
                return(False)
    #print("in pos_neg_is_disjoint: return True\n") #####
    return True
    
def pos_neg_is_subset(pos_ctx_set: ContextSet,
                      ctx_set: ContextSet) -> bool: # *** not needed any more
    """
    Tests whether the first context set is logically subset of the second

    :parameter pos_ctx_set:  A positive context set which has gone through reductions such as truncation or replacements.

    :parameter ctx_set:  An intact negative context set which has not been reduced.

    :returns: True if all context in the first set match some context in the second set.  

"""
    #print_context_set("in pos_neg_is_subset, neg set", ctx_set) #####
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
def search_reductions(agenda: Deque,
                      pair_symbol: PairSym,
                      pos_context_set: ContextSet,
                      ) -> ContextSet:
    """Tests and executes context reductions according to a recipe
    
    :parameter agenda:  Initially a recipe. Consumed and updated during the process.

    :parameter pair_symbol:  The pairsym for which a rule is deduced.

    :parameter pos_context_set:  set of contexts, i.e. pairs (left_context, right_context) where the contexts are space-separated strings of pairsyms.  The context are reduced during the process.

    """
    if cfg.verbosity >= 10:
        print(f"in search_reductions: {agenda = }") ####

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
            good = pos_neg_is_disjoint(new_pos_ctx_set,
                                       negative_context_set[pair_symbol])
        else:
            good = False
        #print_context_set("in search_reductions, new_pos_ctx_set:",
        #                  new_pos_ctx_set) ####
        #print_context_set("in search_reductions, negative_context_set:",
        #                  negative_context_set[pair_symbol]) ####
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
                               negative_context_set[pair_symbol]): # ***
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
                               negative_context_set[pair_symbol]):
            return search_reductions(agenda, pair_symbol,
                                     new_pos_ctx_set)
        else:
            return search_reductions(agenda, pair_symbol,
                                     pos_context_set)
    elif (op in definitions):
        # print(f"in search_reductions, entering reduce_set({op},...)") ####
        new_pos_ctx_set = reduce_set(op, pos_context_set)
        #print_context_set(f"from reduce_set {op}", new_pos_ctx_set) ######
        if pos_neg_is_disjoint(new_pos_ctx_set,
                               negative_context_set[pair_symbol]):
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

def context_set_penalty(context_set: ContextSet):
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

def print_rule(result: Result,
               operator: str) -> None:
    """Prints one rule"""
    if cfg.verbosity >= 2:
        print("\n! recipe:")
        for task in result["recipe"]:
            print(f"!\t\t{task}")
    pair_symbol = result["pairsym"]
    context_set = result["posctx"]
    weight = result["weight"]
    print(f"{pair_symbol} {operator}\t\t! {weight}")
    rule_lst = [f"    {lc} _ {rc}" for lc, rc in context_set]
    print(" ,\n".join(rule_lst) + " ;")

#====================================================================
def process_results_into_rules(pairsym_lst: List[PairSym],
                               result_lst_lst: List[List[Result]]):
    # process rule candidates for each recipe
    cand_rule_lst_dict = defaultdict(list)
    for result_lst in result_lst_lst:
        assert len(pairsym_lst) == len (result_lst)
        recipe = result_lst[0]["recipe"]
        srt_res_lst = sorted(result_lst, key=lambda x: x["weight"])
        for result in srt_res_lst:
            pair_sym = result["pairsym"]
            weight = result["weight"]
            pos_ctx_set = result["posctx"]
            exclusive = True
            for other_result in srt_res_lst:
                if other_result == result:
                    continue
                other_pair_sym = other_result["pairsym"]
                other_pos_ctx_set = negative_context_set[other_pair_sym]
                if not pos_neg_is_disjoint(pos_ctx_set,
                                           other_pos_ctx_set):
                    exclusive = False
                    break
            if exclusive:
                cand_rule_lst_dict[pair_sym].append((weight, recipe,
                                                     "<=>", pos_ctx_set))
                if cfg.verbosity >= 4:
                    print_rule(result, "<=>")
            else:
                cand_rule_lst_dict[pair_sym].append((weight+1000, recipe,
                                            "=>", pos_ctx_set))
                if cfg.verbosity >= 4:
                    print_rule(result, "=>")

    if cfg.verbosity >= 4:
        print("!\n! selected rules:\n!")
    res_lst = []
    for pairsym in pairsym_lst:
        cand_rule_lst = sorted(cand_rule_lst_dict[pairsym],
                               key=lambda x: x[0])
        #print(f"{cand_rule_lst = }") #####
        for (weight, recipe, rule_op, pos_ctx_set) in cand_rule_lst[:1]:
            res = {"pairsym": pairsym,
                   "posctx": pos_ctx_set,
                   "recipe": recipe,
                   "weight": weight,
                   "ruleop": rule_op}
            res_lst.append(res)
 
    #print(f"{res_lst = }") #####

    res_lst.sort(key=lambda x: x["weight"])
    #print(f"{res_lst = }") #####

    exclusive = True
    for res in res_lst:
        rule_op = res["ruleop"]
        if (not exclusive) or res != res_lst[-1]:
            print_rule(res, rule_op)
        if rule_op != "<=>":
            exclusive = False
        
#====================================================================
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
        "-r", "--recipes",
        help="Initial list of recipes for the context reductions.",
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
        "-m", "--max-examples",
        help="Maximun number of examples per morphophoneme to be printed"\
        " as comments.  Default is 20 for each pair symbol.",
        type=int, default=20)

    arpar.add_argument(
        "-v", "--verbosity",
        help="Level of  diagnostic output, default is 1. Set to"\
        " 0 to omit the printing of relevant examples for the rules",
        type=int, default=1)
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

    if args.recipes:
        recipe_f = open(args.recipes, 'r')
        task_lst_lst = list(json.load(recipe_f))
        # print(f"{task_lst_lst = }") ####
    else:
        task_lst_lst = [[{"op": "truncate", "side": "left"},
	                 {"op": "truncate", "side": "right"}]]

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
        input_symbol_lst = [args.symbol]
    elif not args.symbol:
        input_symbol_lst = sorted(list({x for x in input_symbol_set
                                        if not len(x) < 3 }))
    else:
        print(f"Symbol {args.symbol!r} does not occur in the examples")
        lst = list(input_symbol_set)
        print("The following input symbols would be valid:\n",
              " ".join(sorted(lst)))
        exit("")

    for input_symbol in input_symbol_lst:
        pairsym_lst: List[PairSym]  = []
        for pairsym in insym2pairsym_set[input_symbol]:
            pairsym_lst.append(pairsym)
        pairsym_lst.sort()
        if cfg.verbosity >= 10:
            print(f"{pairsym_lst = }")

        if len(pairsym_lst) <= 2:
            continue
        for pairsym in pairsym_lst:
            relevant_contexts(pairsym)

        result_lst_lst = []
        # try each recipe in the task_lst_lst
        for task_lst in task_lst_lst:
            result_lst: ResultList = []
            agenda: Deque = deque(task_lst.copy())
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
                                   "weight": pos_pena,
                                   "recipe": task_lst})

            for result in result_lst:
                if cfg.verbosity >= 5 :
                    print_rule(result, "=>")
                result_lst_lst.append(result_lst)
        
        process_results_into_rules(pairsym_lst, result_lst_lst)
    
        if cfg.verbosity >= 1:
            for pair_symbol in pairsym_lst:
                insym, outsym = pairsym2sympair(pair_symbol)
                pos_ctx_lst = list(positive_context_set[pair_symbol])
                srt_ctx_lst = sorted(pos_ctx_lst,
                                     key=lambda x: x[1])
                step = len(srt_ctx_lst) // args.max_examples
                if step == 0: step = 1
                for lc, rc in srt_ctx_lst[::step]:
                    l_str = context_to_output_str(lc[3:])
                    r_str = context_to_output_str(rc[:-3])
                    print(f"!{l_str:>29}<{outsym}>{r_str}")
        print("\n!-------------------------------------------------")

if __name__ == "__main__":
    main()
