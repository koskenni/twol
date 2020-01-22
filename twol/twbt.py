"""Module for detailed handling basic transducers 

Copyright 2015-2020, Kimmo Koskenniemi

This program is free software under Gnu GPL 3 or later
"""

import hfst

def pairname(insym, outsym):
    """Convert a pair of symbols into a single label

    insym -- input symbol as a string
    outsym -- output symbol as a string

    Returns a string notation of the pair, eg.

    >>> pairname ('a', 'a')
    a
    >>> pairname('i','j')
    i:j
    
    """

    if insym == outsym:
        return(insym)
    else:
        return(insym + ":" + outsym)

def equivpairs(bfst):
    """Find and print all sets of equivalent transition pairs.

    bfst -- a HfstBasicTransducer whose transition symbol pairs are
    analyzed

    Sets of transition symbol pairs behaving identicaly are computed.
    The sets are printed if they contain more than one element.

    """

    transitions_for_pairsymbol = {} # {pairsym: list of trs, ..}
    for state in bfst.states():
        for arc in bfst.transitions(state):
            target = arc.get_target_state()
            pair_symbol = pairname(arc.get_input_symbol(),
                               arc.get_output_symbol())
            if pair_symbol not in transitions_for_pairsymbol:
                transitions_for_pairsymbol[pair_symbol] = set()
            transitions_for_pairsymbol[pair_symbol].add((state,target))
    pairsymbols_for_transition_sets = {} # {tr set: pair syms, ..}
    for pair_symbol, st in transitions_for_pairsymbol.items():
        froz = frozenset(st)
        if froz not in pairsymbols_for_transition_sets:
            pairsymbols_for_transition_sets[froz] = []
        pairsymbols_for_transition_sets[froz].append(pair_symbol)
    labelsym = {} # {sym: sym representing it in pprinting}
    for fs, sl in pairsymbols_for_transition_sets.items():
        sorted_sl = sorted(sl)
        model = sorted(sl)[0]
        for sym in sorted(sl):
            if len(sym) < len(model): model = sym 
        for sym in sorted(sl):
            labelsym[sym] = model
    #print("labelsym: ", labelsym) ##
    return(labelsym, pairsymbols_for_transition_sets)

def fst2dicfst(FST):
    """Returns a dict which gives the transition dict for each state"""
    BFST = hfst.HfstBasicTransducer(FST)
    dicfst = {}
    for state in BFST.states():
        tdir = {}
        for arc in BFST.transitions(state):
            prnm = pairname(arc.get_input_symbol(),
                            arc.get_output_symbol())
            tdir[prnm] = arc.get_target_state()
        dicfst[state] = (BFST.is_final_state(state), tdir)
    return(dicfst)

def fst_to_fsa(FST, separator='^'):
    """Converts FST into an FSA by joining input and output symbols with separator"""
    FB = hfst.HfstBasicTransducer(FST)
    sym_pairs = FB.get_transition_pairs()
    dict = {}
    for sym_pair in sym_pairs:
        in_sym, out_sym = sym_pair
        joint_sym = in_sym + separator + out_sym
        dict[sym_pair] = (joint_sym, joint_sym)
    FB.substitute(dict)
    FSA = hfst.HfstTransducer(FB)
    # print("fst_to_fsa:\n", FSA) ##
    return FSA

def fsa_to_fst(FSA, separator='^'):
    """hfst.fsa_to_fst does the same """
    BFSA = hfst.HfstBasicTransducer(FSA)
    sym_pairs = BFSA.get_transition_pairs()
    dic = {}
    for sym_pair in sym_pairs:
        insym, outsym = sym_pair
        in_sym, out_sym = outsym.split(separator)
        dic[sym_pair] = (in_sym, out_sym)
    BFSA.substitute(dic)
    FST = hfst.HfstTransducer(BFSA)
    return FST

def ppfst(FST, print_equiv_classes=True, title=""):
    """Pretty-prints a HfstTransducer or a HfstBasicTransducer.

    FST -- the transducer to be pretty-printed
    print_equiv_classes -- if True, then print also the equivalence classes
    title -- an explicit additional title to be printed

    If the transducer has a name, it is printed as a heading.

    >>> twbt.ppfst(hfst.regex("a* [b:p|c] [c|b:p]"), True)
    0 . -> 0  a ; -> 1  b:p ; 
    1 . -> 2  b ; 
    2 : 
    Classes of equivalent symbols:
    b:p c
    """
    name = FST.get_name()
    if name:
        print("\n" + name)
    if title:
        print("\n" + title)
    BFST = hfst.HfstBasicTransducer(FST)
    labsy, transy = equivpairs(BFST)
    for state in BFST.states():
        d = {}
        for arc in BFST.transitions(state):
            target = arc.get_target_state()
            if target not in d: d[target] = []
            prnm = pairname(arc.get_input_symbol(),
                            arc.get_output_symbol())
            d[target].append(prnm)
        print(" ", state, (": " if BFST.is_final_state(state) else ". "),
              end="")
        for st, plist in d.items():
            ls = [p for p in plist if p == labsy[p]]
            print( " " + (" ".join(ls)) + " -> " + str(st), end=" ;" )
        print()
    #print(transy) ##
    if print_equiv_classes:
        all_short = True
        for ss, pl in transy.items():
            if len(pl) > 1:
                all_short = False
                break
        if not all_short:
            print("Classes of equivalent symbols:")
            for ss, pl in transy.items():
                if len(pl) > 1:
                    print(" ", " ".join(sorted(pl)))
    return

def ppdef(XRC, name, displayed_formula):
    FST = XRC.compile(name)
    BFST = hfst.HfstBasicTransducer(FST)
    FST = hfst.HfstTransducer(BFST)
    FST.set_name(name + " = " + displayed_formula)
    ppfst(FST, True)
    #alph = [pairname(insym, outsym) for insym, outsym
    #        in FST.get_transition_pairs()]
    #print(name, '=',', '.join(sorted(alph)))
    return

def pp_paths(TR, heading, limit=30):
    results = paths(TR, limit)
    print(heading, end="")
    if len(results) == 0:
        print("  None")
    else:
        print()
        for line in results:
            print(line)

def paths(TR, limit=30):
    path_tuple = TR.extract_paths(output='raw', max_number=limit)
    results = []
    for weight, path in path_tuple:
        lst = [pairname(insym, outsym) for insym, outsym in path]
        str = " ".join(lst)
        results.append(str)
    return(results)

def expanded_examples(TR, insyms, symbol_pair_set):
    # print("symbol_pair_set =", symbol_pair_set) ##
    BT = hfst.HfstBasicTransducer(TR)
    # print("BT.get_transition_pairs() =", BT.get_transition_pairs()) ##
    for insym in insyms:
        lst = [(ins, outs)
               for ins, outs
               in symbol_pair_set if ins == insym]
        for sympair in lst:
            # print("sympair, lst =", sympair, lst) ##
            BT.substitute(sympair, tuple(lst))
    T = hfst.HfstTransducer(BT)
    T.set_name("negative and positive together")
    T.minimize()
    # ppfst(T, True) ##
    #T.minus(TR)
    #T.minimize()
    return(T)

if __name__ == "__main__":
    print("twbt module is not meant to be used as a script")
