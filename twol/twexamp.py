"""A module for reading two-level examples

The examples are assumed to be as space-separated one-level
representation and they are compiled into a single automaton. 
At the same time, the alphabet used in the examples is 
collected in several forms.

cfg.examples_fst -- the transducer which accepts exactly the examples

cfg.symbol_pair_set -- a tuple of string pairs suitable for e.g.
hfst.rules.restriction

"""
import re
import hfst
import twol.cfg as cfg
import twol.twbt as twbt

def pairs_to_fst(pair_set):
    """Converts a seq of symbol pairs into a fst that accepts any of them
"""
    pairs_bfst = hfst.HfstBasicTransducer()
    for pair in pair_set:
        pairs_bfst.disjunct((pair,), 0)       # arg in tokenized format
    fst = hfst.HfstTransducer(pairs_bfst)
    fst.remove_epsilons()
    fst.minimize()
    return fst

def read_fst(filename="examples.fst"):
    """Reads in a previously stored example FST file
    """
    exfile = hfst.HfstInputStream(filename)
    cfg.examples_fst = exfile.read()
    pair_symbols = cfg.examples_fst.get_property("x-pair_symbols")
    # print("pair_symbols", pair_symbols) ##
    pair_symbol_lst = re.split(r" +", pair_symbols)
    for pair in pair_symbol_lst:
        cfg.pair_symbol_set.add(pair)
        (insym, outsym) = cfg.pairsym2sympair(pair)
        cfg.symbol_pair_set.add((insym, outsym))
        cfg.input_symbol_set.add(insym)
        cfg.output_symbol_set.add(outsym)
    cfg.all_pairs_fst = pairs_to_fst(cfg.symbol_pair_set)
    if cfg.verbosity >= 30:
        twbt.ppfst(cfg.all_pairs_fst, title="cfg.all_pairs_fst")
    return
    
def read_examples(filename="test.pstr", build_fsts=True):
    """Reads the examples from the file whose name is 'filename'.
    
    The file must contain one example per line and each line consists of
    a space separated sequence of pair-symbols.
    The examples are processed to a FST which is a union of all examples.
    """
    if build_fsts:
        import hfst
        examples_bfst = hfst.HfstBasicTransducer()
    exfile = open(filename, "r")
    for line_nl in exfile:
        line = line_nl.strip()
        if not line or line.startswith("!"):
            continue
        lst = line.split("!", maxsplit=1)
        line = lst[0].strip()
        pairsym_lst = re.split("\s+", line)
        symbol_pair_lst = [cfg.pairsym2sympair(pairsym)
                           for pairsym in pairsym_lst]
        if not all([insym and outsym for insym, outsym in symbol_pair_lst]):
            print("*** example contains an invalid pair symbol")
            print(line)
            continue
        if cfg.verbosity >= 30:
            print("symbol_pair_lst:", symbol_pair_lst)
        pair_symbol_str = " ".join([cfg.sympair2pairsym(insym, outsym)
                                    for insym,outsym
                                    in symbol_pair_lst])
        if cfg.verbosity >= 30:
            print("pair_symbol_str:", pair_symbol_str)
        cfg.example_lst.append(pair_symbol_str)
        cfg.example_set.add(pair_symbol_str) # spaces normalized
        #LINE_FST = hfst.tokenized_fst(symbol_pair_lst)
        # twbt.printfst(LINE_FST, True) ##
        if build_fsts:
            examples_bfst.disjunct(symbol_pair_lst, 0)
        for insym, outsym in symbol_pair_lst:
            cfg.symbol_pair_set.add((insym, outsym))
    exfile.close()
    if cfg.verbosity >= 30:
        print("List of examples:", cfg.example_lst)
        print("List of alphabet symbol pairs:", sorted(cfg.symbol_pair_set))
    if build_fsts:
        cfg.all_pairs_fst = pairs_to_fst(cfg.symbol_pair_set)
        cfg.examples_fst = hfst.HfstTransducer(examples_bfst)
        cfg.examples_fst.set_name(filename)
        cfg.examples_fst.minimize()
        if cfg.verbosity >= 30:
            twbt.ppfst(cfg.examples_fst, False, title="Example file as FST")
    for insym, outsym in cfg.symbol_pair_set:
        cfg.input_symbol_set.add(insym)
        cfg.output_symbol_set.add(outsym)
    for insym, outsym in cfg.symbol_pair_set:
        pair_symbol = cfg.sympair2pairsym(insym, outsym)
        cfg.pair_symbol_set.add(pair_symbol)
    if build_fsts:
        pair_symbol_lst = [insym+':'+outsym for insym, outsym in cfg.symbol_pair_set]
        pair_symbol_str = " ".join(sorted(pair_symbol_lst))
        # print("symbol pairs:", pair_symbol_str) ##
        cfg.examples_fst.set_property("x-pair_symbols", pair_symbol_str)
    return

def main():
    """The ``twexamp.py`` module can also be used as a standalone script
    or command in order to convert examples in *pair string* format
    into a :term:`finite-state transducer` (FST).  Examples in pair
    string format are plain human readable text files, one example per
    line, where each example is give as a space-separated sequence of
    pair symbols, e.g.::

       k a u p {pØ}:Ø {ao}:a s s {aä}:a

    The invocation of the program could be e.g.::

       $ twol-examp examples.pstr examples.fst

    """
    import hfst
    import argparse
    arpar = argparse.ArgumentParser("python3 twexamp.py")
    arpar.add_argument("examples", help="example pair strings file",
                       default="examples.pstr")
    arpar.add_argument("output", help="file to which write the example FST",
                       default="")
    arpar.add_argument("-v", "--verbosity",
                       help="level of  diagnostic output",
                       type=int, default=0)
    args = arpar.parse_args()
    
    cfg.verbosity = args.verbosity
    
    read_examples(args.examples, build_fsts=True)
    
    if args.output:
        exfile = hfst.HfstOutputStream(filename=args.output)
        exfile.write(cfg.examples_fst)
        exfile.flush()
        exfile.close()
        print("--- example fst written to ", args.output ," ---")
    return

if __name__ == "__main__":
    main()
