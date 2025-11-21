from typing import List, Dict, Set, Tuple, DefaultDict, Deque, NewType
from collections.abc import Sequence

import hfst as hfst
import re

PairSym = str
InSym = str # one mophophonemic symbol as a string
OutSym = str # ine surface symbol as a string
SymPair = Tuple[str, str]
InSymWord = str # a concatenation of InSyms
OutSymWord = str # a concatenation of OutSyms

State = int
FST = NewType("FST", hfst.libhfst.HfstTransducer)
# <class 'hfst.libhfst.HfstTransducer'>
# <class 'hfst.libhfst.HfstInputStream'>

input_alphabet: Set[InSym] = set()
pairs_with_insym: dict[InSym,
                       set[tuple[InSym, OutSym]]] = {}

RuleTransition = dict[SymPair, State] 
RuleDict = dict[State, RuleTransition]  # A HFST transducer converted into a Python Dict
rule_dict_lst: List[RuleDict] = []
finality_dict_lst = []

def dict_rule(rule_fst: FST
              ) -> tuple[RuleDict,
                         Set[State]]:
    global rule_dict_lst
    brule = hfst.HfstBasicTransducer(rule_fst)
    rule_dict = {}
    final_states: Set[State] = set()
    for state in brule.states():
        if brule.is_final_state(state):
            final_states.add(state)
        trans_dict: dict[tuple[InSym, OutSym], State] = {}
        for transition in brule.transitions(state):
            insym = InSym(transition.get_input_symbol())
            if not insym in input_alphabet:
                input_alphabet.add(insym)
            outsym = OutSym(transition.get_output_symbol())
            target = transition.get_target_state()
            trans_dict[(insym,outsym)] = State(target)
            if insym not in pairs_with_insym:
                pairs_with_insym[insym] = set()
            pairs_with_insym[insym].add((insym, outsym))
        rule_dict[state] = trans_dict
    return rule_dict, final_states

def init(rule_file_name: str) -> None:
    global rule_dict_lst
    istream = hfst.HfstInputStream(rule_file_name)
    while not (istream.is_eof()):
        fst = FST(istream.read())
        rule_d, final_states = dict_rule(fst)
        rule_dict_lst.append(RuleDict(rule_d))
        finality_dict_lst.append(final_states)
    istream.close()
    return

result_lst: list[OutSymWord] = []

def search(state_lst: List[State],
           insym_lst: List[InSym],
           outsym_lst: List[OutSym]):
    global result_lst, rule_dict_lst
    if not insym_lst:
        for state, finality in zip(state_lst, finality_dict_lst):
            if state not in finality:
                return
        res = "".join(outsym_lst)
        result_lst.append(res)
        return
    insym = insym_lst[0]
    pair_set = pairs_with_insym[insym]
    for insym, outsym in pair_set:
        new_state_lst = []
        for state, rule_d in zip(state_lst, rule_dict_lst):
            if (insym, outsym) in rule_d[state]:
                new_state_lst.append(rule_d[state][(insym, outsym)])
            else:
                break
        else:
            new_outsym_lst = outsym_lst.copy()
            new_outsym_lst.append(outsym)
            search(new_state_lst, insym_lst[1:], new_outsym_lst)
        continue
    
    return

def generate(word: InSymWord) -> list[OutSymWord]:
    global result_lst, rule_dict_lst
    result_lst = []
    insym_lst = re.findall(r"{[^{}]+}|[^{}]", word)
    for insym in insym_lst:
        if insym not in input_alphabet:
            print(insym, "not in input alphabet")
            return []
    start_state_lst = [0 for r in rule_dict_lst]
    search(start_state_lst, insym_lst, [])
    return result_lst

def main():
    import sys, re
    import argparse

    arpar = argparse.ArgumentParser(
        "twol-generate",
        description = (
            "Generates surface forms out of morphophonemic"
            " representations."))
    arpar.add_argument(
        "rulesfst",
        help = "A .fst file containing all compiled rules of the grammar.",
        default = "~/github/ofitwol/ofitwol/rules/rules-norm.fst")
    args = arpar.parse_args()
    
    init(args.rulesfst)
    for line_nl in sys.stdin:
        line = line_nl.strip().replace(" ", "")
        res = generate(InSymWord(line))
        print("  -> ", res)
        print()

if __name__ == "__main__":
    main()
