# twol.py
# =======
# A compiler and tester for simplified two-level rules.
# Copyright (c) Kimmo Koskenniemi, 2019
# This orogram is free software according to GPL 3 license
#
import sys, re
import hfst
import twol.cfg as cfg
import twol.twbt as twbt
import twol.twexamp as twexamp
import twol.twrule as twrule
from twol.twparser import init as twparser_init
from twol.twparser import parse_rule


def print_raw_paths(paths):
    """For debugging only: print a FST path as a space-separated pairstring"""
    for path in paths:
        weight, sym_pairs = path
        sym_list = [(insym if insym == outsym else insym + ":" + outsym)
                    for insym, outsym in sym_pairs]
        print(' '.join(sym_list))
    return

def main():

    version = "2020-02-11"
    import argparse
    arpar = argparse.ArgumentParser(
        description="A compiler and tester for two-level rules."\
        " Version {}."\
        " See https://pytwolc.readthedocs.io/en/latest/index.html"\
        " or https://github.com/koskenni/twol"\
        " for more information.".format(version))
    arpar.add_argument(
        "-o", "--output",
        help="File to which write the compiled rules if a name is given",
        default="")
    arpar.add_argument(
        "-l", "--lost",
        help="File to which write the examples"\
        " that were not accepted by all rules"\
        " -- it is written as a FST",
        default="")
    arpar.add_argument(
        "-w", "--wrong",
        help="file to which write the wrong strings"\
        " that are accepted by all rules -- it is written as a FST",
        default="")
    arpar.add_argument(
        "-t", "--thorough",
        help="test each rule separately: 0 if no testing is desired,"\
        " 1 if against positive examples,"
        " 2 against both positive and negative examples."\
        " Default is 2.",
        type=int, choices=[0, 1, 2], default=2)
    arpar.add_argument(
        "-r", "--recursion",
        help="set the limit for recursion depth",
        type=int)
    arpar.add_argument(
        "-v", "--verbosity",
        help="level of  diagnostic output",
        type=int, default=0)
    arpar.add_argument(
        "examples",
        help="name of the examples FST file or"\
        " example pair symbol string file",
        default="examples.fst")
    arpar.add_argument(
        "rules", help="name of the rule file",
        default="test.rules")
    args = arpar.parse_args()

    cfg.verbosity = args.verbosity
    if args.recursion:
        sys.setrecursionlimit(args.recursion)

    if args.examples.endswith(".fst"):
        twexamp.read_fst(args.examples)
    else:
        twexamp.read_examples(args.examples)

    if cfg.verbosity >= 30:
        twbt.ppfst(cfg.examples_fst, title="examples_fst")

    parser = twparser_init()

    examples_fsa = hfst.fst_to_fsa(cfg.examples_fst, separator="^")

    examples_up_fsa = cfg.examples_fst.copy()
    examples_up_fsa.input_project()
    if cfg.verbosity >= 30:
        twbt.ppfst(examples_up_fsa, title="examples_up_fsa")

    twrule.init()

    i = 0
    skip = False
    all_rules_fst_lst = []
    rule_file = open(args.rules, 'r')
    line_lst = []

    for line_nl in rule_file:
        i += 1
        if not line_lst:
            line_nl_lst = []
        line_nl_lst.append(line_nl)
        line = line_nl.split('!', maxsplit=1)[0].strip()
        if line == "START":
            skip = False
            continue
        elif line == "STOP":
            skip = True
        if skip or (not line) or line.startswith("!"):
            continue
        line_lst.append(line)
        if not line.endswith(";"):
            continue
        else:
            rule_str = " ".join(line_lst)
            line_lst = []

        op, left, right = parse_rule(parser, rule_str, i, line_nl_lst)
        if op == "?" or not (left and right):
            continue

        if (args.thorough > 0 and op != "=") or cfg.verbosity > 0:
            print("\n")
            print(rule_str)

        if op == "=":
            #        if cfg.verbosity > 0:
            #            print(line)
            if cfg.verbosity >= 10:
                print(left, op)
                twbt.ppfst(right)
            continue
        elif op == "=>":
            R, selector_fst, MIXe = twrule.rightarrow(line, left, *right)
        elif op == "<=":
            R, selector_fst, MIXe = twrule.output_coercion(line, left, *right)
        elif op == "<--":
            R, selector_fst, MIXe = twrule.input_coercion(line, left, *right)
        elif op == "<=>":
            R, selector_fst, MIXe = twrule.doublearrow(line, left, *right)
        elif op == "/<=":
            R, selector_fst, MIXe = twrule.center_exclusion(line, left, *right)
        else:
            print("Error: not a valid type of a rule", op)
            continue
        if cfg.verbosity >= 10:
            twbt.ppfst(R)
        if args.lost or args.wrong or args.output:
            all_rules_fst_lst.append(R)
        if args.thorough > 0:
            selector_fst.intersect(cfg.examples_fst)
            # selector_fst.n_best(5)
            selector_fst.minimize()
            if cfg.verbosity >= 20:
                paths = selector_fst.extract_paths(output='raw')
                print_raw_paths(paths[0:20])
            passed_pos_examples_fst = selector_fst.copy()
            passed_pos_examples_fst.intersect(R)
            if args.thorough > 0:
                if passed_pos_examples_fst.compare(selector_fst):
                    print("All positive examples accepted")
                else:
                    lost_examples_fst = selector_fst.copy()
                    lost_examples_fst.minus(passed_pos_examples_fst)
                    lost_examples_fst.minimize()
                    print("** Some positive examples were rejected:")
                    lost_paths = lost_examples_fst.extract_paths(output='raw')
                    print_raw_paths(lost_paths[0:20])
        if args.thorough > 1 and op in {"=>", "<=", "<=>", "<--"}:
            neg_examples_fsa = examples_fsa.copy()
            neg_examples_fsa.compose(MIXe)
            neg_examples_fsa.output_project()
            neg_examples_fst = hfst.fsa_to_fst(neg_examples_fsa, separator="^")
            neg_examples_fst.minus(cfg.examples_fst)
            NG = examples_up_fsa.copy()
            NG.compose(neg_examples_fst)
            npaths = NG.extract_paths(output='raw')
            #print_raw_paths(npaths)
            passed_neg_examples_fst = NG.copy()
            passed_neg_examples_fst.intersect(R)
            if passed_neg_examples_fst.compare(hfst.empty_fst()):
                print("All negative examples rejected")
            else:
                print("** Some negative examples accepted:")
                npaths = passed_neg_examples_fst.extract_paths(output='raw')
                print_raw_paths(npaths[0:20])

    if args.lost or args.wrong:
        RESU = examples_up_fsa.copy()
        print(RESU.number_of_arcs(), "arcs in RESU")
        RESU.compose_intersect(tuple(all_rules_fst_lst))
        RESU.minimize()
    if args.lost:
        lost_positive_examples_fst = cfg.examples_fst.copy()
        lost_positive_examples_fst.minus(RESU)
        lost_positive_examples_fst.minimize()
        lost_stream = hfst.HfstOutputStream(filename=args.lost)
        lost_stream.write(lost_positive_examples_fst)
        lost_stream.flush()
        lost_stream.close()
        print("wrote lost examples to", args.lost)
    if args.wrong:
        WRONG = RESU.copy()
        WRONG.subtract(cfg.examples_fst)
        WRONG.minimize()
        wrong_stream = hfst.HfstOutputStream(filename=args.wrong)
        wrong_stream.write(WRONG)
        wrong_stream.flush()
        wrong_stream.close()
        print("wrote wrongly accepted examples to", args.wrong)
    if args.output:
        outstream = hfst.HfstOutputStream(filename=args.output)
        for fst in all_rules_fst_lst:
            outstream.write(fst)
        outstream.flush()
        outstream.close()
        print("wrote {} rule transducers to {}".format(len(all_rules_fst_lst),
                                                        args.output))
    return

if __name__ == "__main__":
    main()
