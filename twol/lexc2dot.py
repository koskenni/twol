"""twol-lexc2dot
=============

Reads in a file of LEXC sublexicons and outputs a DOT graph of the linkages

The input from stdin may be a combination of several lexicon files but
the very first sublexicon must be called "Root" and be the node where
the morpheme sequences start.

The sublexicons correspond to DOT nodes and the continuations in lexicon entries correspond to edges of the graph.

In order to structure complex lexicon system graphs, one may have a resticted control over the organising or ranking the nodes.  One option forces the nodes that are directly reachabel from Root to have mutually the same rank.  Another option does the same for any sublexicon whose name contains a slash.  OFITWOL follows a convention that lexeme entries usually continue to nodes like "/v" or "/a".  If one follows this convention, this option is usually quite useful.

If your lexicon system consists of several files, you may concatenate them all or leave some files out.  In this way, you can either describe parts of the whole lexicon system, or just leave some irregular parts out.  If the input is partial, then you may or may not include nodes that cannot be reached from the Root.

The DOT description of the graph can then be processed with graphviz dot program in order to get a PDF or PNG file which can be directly displayed.

"""

from collections import defaultdict
import re

id_dict = {}
from_to_set = set()
from_to_targets_dict = defaultdict(set)
lex_name_lst = []
ext_name_lst = []
node_rank = defaultdict(int)
id_num = 0

def new_id(lex_name):
    global id_num
    if re.fullmatch(r"[a-zA-Z][a-zA-Z0-9]*", lex_name):
        id = lex_name
    else:
        id_num += 1
        id = "ID_" + str(id_num)
    id_dict[lex_name] = id
    return id

def main():
    import argparse
    arpar = argparse.ArgumentParser("python3 lexc2dot.py")
    arpar.add_argument(
        "-u", "--unreachable",
        help="Include also unreachable nodes",
        action='store_true', default=False)
    arpar.add_argument(
        "-s", "--slash",
        help="Same rank for all lexnames that include this char",
        default="")
    arpar.add_argument(
        "-e", "--entry",
        help="""same rank for sublexs immediately connected to Root
        (i.e. often the lexicons containing the stem entries of lexemes)""",
        action='store_true', default=False)
    arpar.add_argument(
        "-v", "--verbosity",
        help="level of  diagnostic output",
        type=int, default=0)
    args = arpar.parse_args()

    import sys

    line_num = 0
    skip = True
    for line_nl in sys.stdin:
        line_num += 1
        line = line_nl.rstrip()
        lst = re.split(r"\s+", line)
        if line.startswith("!"):
            continue
        if line.startswith("Multichar_Symbols"):
            skip = True
        elif line.startswith("Definitions"):
            skip = True
        elif line_nl.startswith("LEXICON "):
            skip = False
            if len(lst) >= 2:
                lex_name = lst[1]
                id = new_id(lex_name)
                lex_name_lst.append(lex_name)
            else:
                exit("** {}: {}".format(line_num, line))
        elif not skip:
            if len(lst) >= 2:
                target = lst[1]
                from_to_set.add((lex_name, target))
                from_to_targets_dict[lex_name].add(target)
            else:
                exit("** {}: {}".format(line_num, line))

    target_nodes = {"Root"}
    for source, target in sorted(from_to_set):
        if source not in id_dict:
            src_id = new_id(source)
        if target not in id_dict:
            trg_id = new_id(target)
            ext_name_lst.append(target)
        target_nodes.add(id_dict[target])

    print("Digraph {")
    print("\tsize=7;")
    print("\trankdir=LR;")
    print("\tnewrank=true;")
    print("\tranksep=0.5;")
    print("\tfontsize=24;")
    slash_lst = []
    for ln in lex_name_lst:
        nd = id_dict[ln]
        if ln != "#" and (nd in target_nodes or args.unreachable):
            print('{} [label="{}"]'.format(nd, ln))
        if ln == "Root":
            print("{{ rank=min ; {} }}".format(nd))
        if ln == "End":
            print("{{ rank=max ; {} }}".format(nd))
        if (args.slash and (args.slash in ln)
            and (args.unreachable or nd in target_nodes)):
            slash_lst.append(nd)

    if args.slash:
        if slash_lst:
            slash_str = ", ".join(slash_lst)
            print("{{ rank=same {} }}".format(slash_str))

    if args.unreachable:
        for ln in ext_name_lst:
            nd = id_dict[ln]
            if ln != "#":
                print('{} [label="{}"]'.format(nd, ln))
            if ln in {"Root", "More"} or (nd not in target_nodes):
                print("{{ rank=min ; {} }}".format(nd))
            if ln == "End" and ln != "#":
                print("{{ rank=max ; {} }}".format(nd))

    pos_node_lst = []
    for source, target in sorted(from_to_set):
        src_id = id_dict[source]
        trg_id = id_dict[target]
        if src_id == "Root":
            pos_node_lst.append(trg_id)
        if (args.unreachable or src_id in target_nodes) and target != "#":
            print("\t{} -> {}".format(src_id, trg_id))

    if args.entry:
        if pos_node_lst:
            pos_node_str = ", ".join(pos_node_lst)
            print("{{ rank=same {} }}".format(pos_node_str))

    print("}")
    return

if __name__ == "__main__":
    main()
