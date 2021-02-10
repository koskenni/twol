
"""twol-tester tests a set of two-level rules against examples

This program is useful for checking complete rule sets where all morphophonemes are constrained by some rules.  The twol-comp rule compiler checks indidual rules as it compiles them, so this program becomes useful when initial versions all rules have been written.  The formulae::

    lost = examples & rule[1] & rule[2] & ... & rule[n]

    neg = [pos.u .o. pairs*] - examples

    wrong = neg & rule[1] & rule[2] & ... & rule[n]

"""
import os
import re
import hfst
import twol.cfg as cfg
import twol.twexamp as twexamp
import twol.twbt as twbt

def paths(heading, fst):
    if cfg.verbosity >= 10:
        print(heading + "\n" + fst.extract_paths(max_cycles=1, output="text"))
    return

def main():
    import argparse
    arpar = argparse.ArgumentParser(
        "twol-tester",
        description = """A program for testing complete sets of twol rules""")
    arpar.add_argument(
        "-e", "--examples", action='store', nargs='+',
        help="""Either one name of a FST file that contains the examples or
            a list of names of files which contain the PSTR form examples
            used for compiling the rules.""",
        default=[None])
    arpar.add_argument(
        "-r", "--rules", action='store', nargs='+',
        help="""One or more files which contain the compiled rules as FSTs.
            The set  of rules ought to cover (almost) all morphophonemes.""",
        default=[None])
    arpar.add_argument(
        "-l", "--lost",
        help="""an FST that lists positive examples that are not
            accepted by all rules""",
        default="")
    arpar.add_argument(
        "-w", "--wrong",
        help="""an FST that lists the negative examples that are
            accepted gy by all rules""",
        default="")
    arpar.add_argument(
        "-v", "--verbosity",
        help="level of  diagnostic output",
        type=int, default=0)

    args = arpar.parse_args()
    cfg.verbosity = args.verbosity
    #
    # Build the FST of the example pair strings and
    # store in cfg.examples_fst and the cfg.input_symbol_set,
    # cfg.output_symbol_set, cfg.symbol_pair_set and
    # cfg.all_pairs_set
    #
    if len(args.examples) and args.examples[0].endswith(".fst"):
        twexamp.read_fst(args.examples)
    elif len(args.examples) > 0:
        twexamp.read_examples(args.examples, build_fsts=True)
    else:
        error("ERROR IN EXAMPLE FILE NAMES: {}".format(args.examples))
        #
    # Read in the compiled twol rule FST or FSTs
    #
    rule_fst_lst = []
    for rule_file_name in args.rules:
        if (not os.path.isfile(rule_file_name) and
            rule_file_name.endswith(".fst")):
            exit("RULE FST FILE {} DOES NOT EXIST",format(rule_file))
        fst_stream = hfst.HfstInputStream(rule_file_name)
        while not fst_stream.is_eof():
            fst = fst_stream.read()
            rule_fst_lst.append(fst)
        fst_stream.close()
    #
    # Build positive and negative examples 
    #
    pos_fst = cfg.examples_fst.copy()
    neg_fst = pos_fst.copy()
    paths("positive examples", neg_fst)
    neg_fst.input_project()
    pistar_fst = cfg.all_pairs_fst.copy()
    pistar_fst.repeat_star()
    neg_fst.compose(pistar_fst)
    neg_fst.minimize()
    neg_fst.subtract(pos_fst)
    paths("negative examples", neg_fst)
    #
    # Lost and wrong examples
    #
    if args.lost:
        remain_fst = pos_fst.copy()
        for fst in rule_fst_lst:
            remain_fst.intersect(fst)
        lost_fst = pos_fst.copy()
        lost_fst.subtract(remain_fst)
        lost_stream = hfst.HfstOutputStream(filename=args.lost)
        lost_stream.write(lost_fst)
        lost_stream.close()
    if args.wrong:
        wrong_fst = neg_fst.copy()
        for fst in rule_fst_lst:
            wrong_fst.intersect(fst)
        wrong_stream = hfst.HfstOutputStream(filename=args.wrong)
        wrong_stream.write(wrong_fst)
        wrong_stream.close()

if __name__ == "__main__":

    main()
