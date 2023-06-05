# -*- coding: utf-8 -*-

###from __future__ import absolute_import, division, print_function, unicode_literals

import sys, re, json

###from codecs import open

from pprint import pprint

import tatsu
from tatsu import compile
from tatsu.ast import AST
from tatsu.walkers import NodeWalker
from tatsu.exceptions import ParseException, FailedParse, ParseError, FailedSemantics

import twol.cfg as cfg
import twol.twexamp as twexamp

from collections import deque, defaultdict
from typing import List, Dict, Set, Tuple, DefaultDict

insym2pairsym_set: DefaultDict[str, set] = defaultdict(set)
# key: input symbol, value: set of pair symbols

outsym2pairsym_set: DefaultDict[str, set] = defaultdict(set)
# key: output symbol, value: set of pair symbols


class DiscovDefSemantics(object):

    def define(self, ast):
        #print(f"in define: {ast = }") ####
        cfg.definitions[ast.left] = ast.right
        return
    
    def identifier(self, ast):
        string = ast.strip()
        #print(f"in identifier: {string}") ####
        return string

    def union(self, ast):
        #print(f"in union: {ast.left = }, {ast.right = }") ####
        return ast.left | ast.right

    def intersection(self, ast):
        return ast.left & ast.right

    def difference(self, ast):
        return ast.left - ast.right

    def Morphophonemic(self, ast):
        """Surface completion

        Returns a set which contains valid pair symbols x:y
        such that for x there is some pair x:z in the original set.
        For a single symbol pair k:g.m it is equivalent to k:
        """
        # print(f"in Morphophonemic: {ast = }") ####
        pairsym_set = ast.expr
        result_set = set()
        insym_set = set()
        for pairsym in pairsym_set:
            insym, outsym = cfg.pairsym2sympair(pairsym)
            insym_set.add(insym)
        for insymbol, outsymbol in cfg.symbol_pair_set:
            if insymbol in insym_set:
                result_set.add(cfg.sympair2pairsym(insymbol, outsymbol))
        # print(f"in Morphophonemic: {result_set = }") ####
        return result_set

    def Surface(self, ast):
        """Morphophonemic completion

        Returns a set which contais valid pair symbols whose
        ouput side cepted by the output side of the argument.
        For a single pair symbol k:g.s it is equivalent to :g
        """
        pairsym_set = ast.expr
        result_set = set()
        outsym_set = set()
        for pairsym in pairsym_set:
            insym, outsym = cfg.pairsym2sympair(pairsym)
            outsym_set.add(outsym)
        for insymbol, outsymbol in cfg.symbol_pair_set:
            if outsymbol in outsym_set:
                result_set.add(cfg.sympair2pairsym(insymbol, outsymbol))
        return result_set

    def pair(self, ast):
        #print(f"in pair: {ast = }") ####
        up, lo = ast
        up_quoted = re.sub(r"([{}])", r"%\1", up)
        lo_quoted = lo                         ### ????
        lo = re.sub(r"%(.)", r"\1", lo_quoted)
        #print(f"in pair: {up= }, {lo = }") ####

        failmsg = []
        if up and (up not in cfg.input_symbol_set):
            failmsg.append(f"input symbol '{up}'")
        if lo and (lo not in cfg.output_symbol_set):
            failmsg.append(f"outputput symbol '{lo}'")
        if (up and lo and
            (up, lo) not in cfg.symbol_pair_set):
               failmsg.append(f"symbol pair '{up}:{lo}'")
        if failmsg:
            cfg.error_message = " and ".join(failmsg) + " not in alphabet"
            raise FailedSemantics(cfg.error_message)

        if up and lo:         # it is e.g. "{aØ}:a"
            result_set = set([f"{up}:{lo}"])
            return result_set
        elif up and (not lo):   # it is e.g. "{aØ}:"
            result_set = set()
            for insym, outsym in cfg.symbol_pair_set:
                if insym == up:
                    result_set.add(cfg.sympair2pairsym(insym, outsym))
            return result_set
        elif (not up) and lo:   # it is e.g. ":i"
            result_set = set()
            for insym, outsym in cfg.symbol_pair_set:
                if outsym == lo:
                    result_set.add(cfg.sympair2pairsym(insym, outsym))
            return result_set
        else:                   # it is ":"
            result_set = cfg.pair_symbol_set.copy()
            return result_set

    def defined(self, ast):
        #print(f"in defined: {ast = }") ####
        string = ast
        if string in cfg.definitions:
            # print(f"in defined: {string} is a defined symbol") ####
            result_set = cfg.definitions[string].copy()
            return result_set
        else:
            cfg.error_message = f"in defined: {string} is not defined"
            raise FailedSemantics(cfg.error_message)

    def outsym(self, ast):
        #print(f"in outsym: {ast = }") ####
        string = ast
        lo_quoted = string                      ### ????
        lo = re.sub(r"%(.)", r"\1", lo_quoted)
        # print(f"in outsym: {lo = }, {lo_quoted = }") ####
        if (lo in cfg.output_symbol_set and
            (lo,lo) in cfg.symbol_pair_set):
            # print(f"symbol_or_pair: {string} is a surface symbol") ####
            result_set =  set(cfg.sympair2pairsym(lo, lo))
            return result_set
        else:
            cfg.error_message = f"in outsym: {string} is not in alphabet"
            raise FailedSemantics(cfg.error_message)

ebnf_str = """
@@grammar::DiscovDefSyntax
@@left_recursion :: False

start = define $ ;

define = left:identifier op:'=' ~ right:expression ';' ;

#identifier = /\b[^\W_0-9][^\W_]+\b/ ;
#identifier = /[A-ZÅÄÖØ][A-ZÅÄÖØa-zåäöšž]+/ ;
identifier = /[^\W_0-9][^\W_]+(?=[ \t\n]*=[ \t\n]*)/ ;

expression = term ;

term = union | difference | intersection | factor ;

union = left:factor op:'|' ~ right:term ;

difference = left:factor op:'-' ~ right:term ;

intersection = left:factor op:'&' ~ right:term ;

factor = unit ;

unit = Morphophonemic
    | Surface
    | atom
    ;

Morphophonemic = expr:atom '.m' ;

Surface = expr:atom '.s' ;

atom
    = '[' ~ @:expression ']'
    | pair
    | outsym
    | defined
    ;

#pair = /(\{[^ _{}]+\}|):([^\W0-9_]\b|[']|%\W|)/ ;
#pair = /(\{[A-ZÅÖÄØa-zåöäšž]+\}|):([A-ZÅÖÄØa-zåäöšž']|%\W|)/ ;
pair = /(\{[^ _{}]+\}|):([^\W0-9_]|[']|%\W|)(?![^\W0-9_]|[']|%[-%])/ ;

#defined = /\b[^\W0-9_][^\W_]+\b/ ;
#defined = /[A-ZØ][A-ZØa-z]+/ ;
defined = /[^\W0-9_][^\W_]+/ ;

#outsym = /\b([^\W0-9_]|[']|%[-%])\b/ ;
#outsym = /[A-ZÅÖÄØa-zåäöšž]|[']|%[-%]/ ;
outsym = /([^\W0-9_]|[']|%[-%])(?![^\W0-9_]|[']|%[-%])/;

"""

def init():
    """Initializes the module and compiles and returns a tatsu parser

    grammar_file -- the name of the file containing the EBNF grammar
    for rules
    """
    # print("in init:", ebnf_str) ####
    parser = compile(ebnf_str, trace=False)
    return parser

def parse_defs(parser, defs_filename):
    defs_str = open(defs_filename, "r").read()
    defs_lst = defs_str.split(";")
    line_no = 0
    for defi in defs_lst:
        try:
            line_lst = [l.strip() for l in defi.split("\n")]
            set_def_str = (" ".join(line_lst)) + " ;"
            # print(f"{set_def_str = }") ####
            if set_def_str.strip() == ";": continue
            parser.parse(set_def_str,
                         start="start",
                         semantics=DiscovDefSemantics(),
                         trace=False)
            line_no += len(line_lst)
            #print(f"{cfg.definitions = }") ####
        except ParseException as e:
            print("\n" + 40 * "*")
            print("ERROR WAS IN INPUT LINES:",
                  line_no, "-", line_no + len(line_lst) - 1)
            print("".join(line_lst))
            print("THE ERROR IS PROBABLY ABOVE THE '^' OR BEFORE IT")
            msg = str(e)
            lst = msg.split("\n")
            if len(lst) >= 3:
                print(lst[1])
                print(lst[2], "<---", e.__class__.__name__, "HERE")
                if cfg.error_message:
                    print("EXPLANATION:")
                    print("    ", cfg.error_message)
                    cfg.error_message = ""
            else:
                print(e) ###
                print(str(e))
            print(40 * "*" + "\n")
    return defs_str

def main():
    import os
    import argparse

    arpar = argparse.ArgumentParser(
        description="A compiler for discovery set definitions")
    arpar.add_argument("-e", "--examples",
                       help="examples file",
                       default="ksk-examples.pstr")
    arpar.add_argument("-d", "--definitions", default="setdefs.twol")
    args = arpar.parse_args()

    twexamp.read_examples(filename_lst=[args.examples], build_fsts=False)

    for insym, outsym in cfg.symbol_pair_set:
        pair_symbol = cfg.sympair2pairsym(insym, outsym)
        insym2pairsym_set[insym].add(pair_symbol)
        outsym2pairsym_set[outsym].add(pair_symbol)

    parser = init()
    parse_defs(parser, args.definitions)
    
    for nm, cs in cfg.definitions.items():
        s_str = " ".join(sorted(list(cs)))
        print(f"{nm}: {s_str}\n")


if __name__ == '__main__':
    main()
    
    
