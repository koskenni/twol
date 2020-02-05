"""A module for dicovering raw two-level rules from a set of carefully chosen examples

Examples, contexts and rules are treated in terms of strings without any
finite-state machinery or rule compilation.  Examples and contexts are
space separated sequences of pair-symbols. 

© Kimmo Koskenniemi, 2017-2018. Free software under the GPL 3 or later.
"""

import sys
import re
import twol.cfg as cfg
import twol.twexamp as twexamp

pair_symbols_for_input = {}   # key: input symbol, value: set of pair symbols
pair_symbols_for_output = {}

def relevant_contexts(pair_symbol):
    """Select positive and negative contexts for a given pair-symbol
    
    pair_symbol -- the pair-symbol for which the contexts are selected
    
    returns a tuple of:
    
    pos_context_set -- a set of contexts in the examples where the
    pair_symbol occurs
    
    neg_context_set -- a set of contexts where the input-symbol of the
    pair_symbol occurs with another output-symbol but so that there is
    no example in the example_set where the pair_symbol occurs in such a
    context
    """
    input_symbol, output_symbol = cfg.pairsym2sympair(pair_symbol)
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
    
def ppcontexts(ctxs, title):
    """Print a list of context for tracing and debugging"""
    print(title)
    for lc, rc in sorted(ctxs):
        print(lc, "_", rc)

def shorten_contexts(contexts, left_length, right_length):
    """Computes a new set of truncated contexts"""
    if cfg.verbosity >= 25:
        print("left and right length:",
              left_length, right_length)
        ppcontexts(contexts,
                   "contexts as given to shorten_contexts()")
    new_contexts = set()
    for left_context, right_context in contexts:
        left_lst = left_context.split(" ")
        start = max(0, len(left_lst) - left_length)
        new_lc = " ".join(left_lst[start:])
        # print("start:", start, "new_lc:", new_lc)
        right_lst = right_context.split(" ")
        new_rc = " ".join(right_lst[0:right_length])
        new_contexts.add((new_lc, new_rc))
    return(new_contexts)

def minimal_contexts(pair_symbol, pos_contexts, neg_contexts):
    """Shortens the left and right contexts step by step
    
    Finds shortest contexts which accept correct occurrences of
    pair_symbol and still reject the incorrect occurrences of it.
    
    pair_symbol -- a pair-symbol, e.g. '{aä}:a' for which the optimal
    contexts are computed
    
    pos_context, neg_contexts -- selected from the examples
    
    returns a tuple: (positive_contexts, negative_contexts)
    """
    if cfg.verbosity >= 25:
        ppcontexts(pos_contexts, "positive contexts for " + pair_symbol)
        ppcontexts(neg_contexts, "negative contexts for " + pair_symbol)
    # find maximum lengths (in psyms) of left and right contexts
    left_len = 0
    right_len = 0
    for left_context, right_context in pos_contexts:
        lcount = left_context.count(" ")
        if lcount >= left_len: left_len = lcount + 1
        rcount = right_context.count(" ")
        if rcount >= right_len: right_len = rcount + 1
    for left_context, right_context in neg_contexts:
        lcount = left_context.count(" ")
        if lcount >= left_len: left_len = lcount + 1
        rcount = right_context.count(" ")
        if rcount >= right_len: right_len = rcount + 1

    # shorten the contexts stepwise while the positive and
    # the negative contexts stay disjoint
    p_contexts = pos_contexts.copy()
    n_contexts = neg_contexts.copy()
    left_incomplete = True
    right_incomplete = True
    while left_incomplete or right_incomplete:
        # print(left_len, right_len) ##
        if left_incomplete and left_len > 0:
            new_p_contexts = shorten_contexts(p_contexts, left_len-1, right_len)
            new_n_contexts = shorten_contexts(n_contexts, left_len-1, right_len)
            if new_p_contexts.isdisjoint(new_n_contexts):
                # print("still disjoint") ##
                p_contexts = new_p_contexts
                n_contexts = new_n_contexts
                left_len = left_len - 1
            else:
                if cfg.verbosity >= 25:
                    print("left side now complete") ##
                    ppcontexts(new_p_contexts & new_n_contexts,
                               "intersection of new pos and neg contexts")
                left_incomplete = False
        elif right_incomplete and right_len > 0:
            new_p_contexts = shorten_contexts(p_contexts, left_len, right_len-1)
            new_n_contexts = shorten_contexts(n_contexts, left_len, right_len-1)
            if new_p_contexts.isdisjoint(new_n_contexts):
                # print("still disjoint") ##
                p_contexts = new_p_contexts
                n_contexts = new_n_contexts
                right_len = right_len - 1
            else:
                # print("left side now complete") ##
                right_incomplete = False
        else:
            break
    if cfg.verbosity >= 25:
        ppcontexts(p_contexts, "positive contexts")
        ppcontexts(n_contexts, "negative contexts")
    return p_contexts, n_contexts

def print_rule(pair_symbol, operator, contexts):
    """Prints one rule"""
    print(pair_symbol, operator)
    rule_lst = ["    {} _ {}".format(lc, rc) for lc, rc in contexts]
    print(",\n".join(rule_lst) + " ;")
    return

def context_to_output_str(pairsym_str):
    """Converts a pair symbol string into its surface string"""
    pairsym_lst = pairsym_str.split(" ")
    sympair_lst = [cfg.pairsym2sympair(psym) for psym in pairsym_lst]
    outsym_lst = [outsym for insym, outsym in sympair_lst]
    return "".join(outsym_lst)

def main():
    version = "2020-02-01"
    
    import argparse
    arpar = argparse.ArgumentParser(
        "twol-discov",
        description="Deduces two-level rules out of"\
        " a file of examples.  The file must consist of"\
        " lines of space-separated pair string.  Such a file"\
        " can be produced e.g. by twol-renamed program."\
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
        "-v", "--verbosity",
        help="Level of  diagnostic output, default is 5. Set to"\
        " 0 to omit the printing of relevant examples for the rules",
        type=int, default=5)
    args = arpar.parse_args()

    cfg.verbosity = args.verbosity
    
    twexamp.read_examples(filename=args.examples, build_fsts=False)
    if cfg.verbosity >= 10:
        print("--- all examples read in ---")
    
    for insym in cfg.input_symbol_set:
        pair_symbols_for_input[insym] = set()
    for insym, outsym in cfg.symbol_pair_set:
        pair_symbol = cfg.sympair2pairsym(insym, outsym)
        pair_symbols_for_input[insym].add(pair_symbol)

    if args.symbol:
        if args.symbol in pair_symbols_for_input:
            pair_set = pair_symbols_for_input[args.symbol]
            pair_lst = []
            for pairsym in pair_set:
                insym, outsym = cfg.pairsym2sympair(pairsym)
                pair_lst.append((insym, outsym))
            if cfg.verbosity >= 10:
                print("pair_lst:", pair_lst)
        else:
            print("Symbol {} not in the input alphabet of examples".format(args.symbol))
            lst = [insym for insym in
                   pair_symbols_for_input.keys() if len(insym) > 2]
            print("The following symbols are:", " ".join(sorted(lst)))
            exit("")
    else:
        pair_lst = sorted(cfg.symbol_pair_set)

    for insym, outsym in pair_lst:
        if len(pair_symbols_for_input[insym]) <= 1:
            continue
        pair_symbol = cfg.sympair2pairsym(insym, outsym)
        posi_contexts, nega_contexts = relevant_contexts(pair_symbol)
        pos_contexts, neg_contexts = minimal_contexts(pair_symbol,
                                                      posi_contexts.copy(),
                                                      nega_contexts.copy())
        if len(pos_contexts) <= len(neg_contexts) or cfg.verbosity > 0:
            print_rule(pair_symbol, "=>", pos_contexts)
        else:
            print_rule(pair_symbol, "/<=", neg_contexts)
        if args.verbosity >= 5:
            for lc, rc in posi_contexts:
                l_str = context_to_output_str(lc)
                r_str = context_to_output_str(rc)
                print("!{:>29}<{}>{}".format(l_str, outsym, r_str))

if __name__ == "__main__":
    main()
