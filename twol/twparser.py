# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import sys, re, json
from codecs import open
from pprint import pprint

import tatsu
from tatsu import compile
from tatsu.ast import AST
#from tatsu import ast
#from ast import AST
from tatsu.walkers import NodeWalker
#from tatsu import walkers
#from walkers import NodeWalker

from tatsu.exceptions import ParseException, FailedParse, ParseError, FailedSemantics

import hfst
import twol.cfg as cfg
import twol.twexamp as twexamp

class TwolRegexSemantics(object):

    def define(self, ast):
        cfg.definitions[ast.left] = ast.right
        return ("=", ast.left, ast.right)
    
    def identifier(self, ast):
        string = ast.token.strip()
        return string

    def right_arrow_rule(self, ast):
        result = ("=>", ast.left, ast.right)
        return result

    def left_arrow_rule(self, ast):
        result = ("<=", ast.left, ast.right)
        return result

    def double_arrow_rule(self, ast):
        result = ("<=>", ast.left, ast.right)
        return result

    def exclusion_rule(self, ast):
        result = ("/<=", ast.left, ast.right)
        return result

    def context_lst(self, ast):
        result = ast.left.extend(ast.right)
        return result

    def context(self, ast):
        lc = ast.left if ast.left else ""
        rc = ast.right if ast.right else ""
        result = [(lc, rc)]
        return result

    def union(self, ast):
        return "[{} | {}]".format(ast.left, ast.right)

    def intersection(self, ast):
        return "[{} & {}]".format(ast.left, ast.right)

    def difference(self, ast):
        return "[{} - {}]".format(ast.left, ast.right)

    def concatenation(self, ast):
        return "[{} {}]".format(ast.left, ast.right)

    def composition(self, ast):
        return "[{} .o. {}]".format(ast.left, ast.right)

    def crossproduct(self, ast):
        return "[{} .x. {}]".format(ast.left, ast.right)

    def Kleene_star(self, ast):
        return "[{}]*".format(ast.expr)

    def Kleene_plus(self, ast):
        return "[{}]+".format(ast.expr)

    def Upper(self, ast):
        return "[{}].u".format(ast.expr)

    def Lower(self, ast):
        return "[{}].l".format(ast.expr)

    def One_but_not(self, ast):
        return r"[PI - [{}]]".format(ast.expr)

    def optexpression(self, ast):
        return "({})".format(ast.expr)

    def subexpression(self, ast):
        return "[{}]".format(ast.expr)

    def symbol_or_pair(self, ast):
        string = ast.token.strip()
        failmsg = []
        pat = re.compile(r"""^
        (?P<up>[^{}:\s]*
         |
         \{[^{}:\s]+\})
        :
        (?P<lo>[^{}:\s]*)
        $""", re.X)
        m = re.match(pat, string)
        if m:                       # it is a pair with a colon
            up = m.group("up")
            up_quoted = re.sub(r"([{}])", r"%\1", up)
            lo = m.group("lo")
            if up and (up not in cfg.input_symbol_set):
                failmsg.append("input symbol '{}'".format(up))
            if lo and (lo not in cfg.output_symbol_set):
                failmsg.append("output symbol '{}'".format(lo))
            if up and lo and ((up, lo) not in cfg.symbol_pair_set):
                failmsg.append("symbol pair '{}'".format(string))
            if failmsg:
                cfg.error_message = " and ".join(failmsg) + " not in alphabet"
                raise FailedSemantics(cfg.error_message)
            elif up and lo:         # it is a valid pair with a colon
                return "{}:{}".format(up_quoted, lo)
            elif up and (not lo):
                return "[{} .o. PI]".format(up_quoted)
            elif (not up) and lo:
                return "[PI .o. {}]".format(lo)
            else:
                return "PI"
        m = re.fullmatch(r"[^{}\s:]+", string)
        if m:                       # its either a defined sym or a surf ch
            if string in cfg.definitions:
                return "{}".format(string)
            elif (string in cfg.output_symbol_set) and (string in cfg.input_symbol_set):
                return "{}:{}".format(string, string)
            elif string in {'BEGIN', 'END'}:
                return string
        cfg.error_message = "'" + string + "' is an invalid pair/definend symbol"
        raise FailedSemantics(cfg.error_message)

class TwolFstSemantics(object):

    def define(self, ast):
        expr_fst = ast.right.copy()
        def_name = ast.left
        cfg.definitions[def_name] = expr_fst
        return ("=", ast.left, ast.right)
    
    def identifier(self, ast):
        string = ast.token.strip()
        return string

    def right_arrow_rule(self, ast):
        result = ("=>", ast.left, ast.right)
        return result

    def output_coercion_rule(self, ast):
        result = ("<=", ast.left, ast.right)
        return result

    def input_coercion_rule(self, ast):
        result = ("<--", ast.left, ast.right)
        return result

    def double_arrow_rule(self, ast):
        result = ("<=>", ast.left, ast.right)
        return result

    def exclusion_rule(self, ast):
        result = ("/<=", ast.left, ast.right)
        return result

    def context_lst(self, ast):
        left_lst = ast.left.copy()
        right_lst = ast.right.copy()
        result = left_lst.copy()
        result.extend(right_lst)
        return result

    def context(self, ast):
        lc = ast.left.copy() if ast.left else hfst.epsilon_fst()
        rc = ast.right.copy() if ast.right else hfst.epsilon_fst()
        lc.substitute("END", "BEGIN")
        #print(lc)###
        #print(rc)###
        result = [(lc, rc)]
        return result

    def union(self, ast):
        name = "[{} | {}]".format(ast.left.get_name(), ast.right.get_name())
        result_fst = ast.left.copy()
        result_fst.disjunct(ast.right)
        result_fst.minimize()
        result_fst.set_name(name)
        return result_fst

    def intersection(self, ast):
        name = "[{} & {}]".format(ast.left.get_name(), ast.right.get_name())
        result_fst = ast.left.copy()
        result_fst.conjunct(ast.right)
        result_fst.minimize()
        result_fst.set_name(name)
        return result_fst

    def difference(self, ast):
        name = "[{} - {}]".format(ast.left.get_name(), ast.right.get_name())
        result_fst = ast.left.copy()
        result_fst.minus(ast.right)
        result_fst.minimize()
        result_fst.set_name(name)
        return result_fst

    def concatenation(self, ast):
        name = "[{} {}]".format(ast.left.get_name(), ast.right.get_name())
        result_fst = ast.left.copy()
        result_fst.concatenate(ast.right)
        result_fst.minimize()
        result_fst.set_name(name)
        return result_fst

    def composition(self, ast):
        name = "[{} .o. {}]".format(ast.left.get_name(), ast.right.get_name())
        result_fst = ast.left.copy()
        result_fst.compose(ast.right)
        result_fst.minimize()
        result_fst.set_name(name)
        return result_fst

    def crossproduct(self, ast):
        name = "[{} .x. {}]".format(ast.left.get_name(), ast.right.get_name())
        result_fst = ast.left.copy()
        result_fst.cross_product(ast.right)
        result_fst.set_name(name)
        return result_fst

    def Kleene_star(self, ast):
        name = "[{}]*".format(ast.expr.get_name())
        result_fst = ast.expr.copy()
        result_fst.repeat_star()
        result_fst.minimize()
        result_fst.set_name(name)
        return result_fst

    def Kleene_plus(self, ast):
        name = "[{}]+".format(ast.expr.get_name())
        result_fst = ast.expr.copy()
        result_fst.repeat_plus()
        result_fst.minimize()
        result_fst.set_name(name)
        return result_fst

    def Upper(self, ast):
        """Input projection

        Note that the result is outside the Pi*, i.e. not a valid
        two-level expression.  This operator should be avoided at all
        costs.
        """
        name = "[{}].u".format(ast.expr.get_name())
        result_fst = ast.expr.copy()
        result_fst.input_project()
        result_fst.set_name(name)
        return result_fst

    def Lower(self, ast):
        """Output projection

        Note that the result is outside the Pi*, i.e. not a valid
        two-level expression.  This operator should be avoided at all
        costs.
        """
        name = "[{}].l".format(ast.expr.get_name())
        result_fst = ast.expr.copy()
        result_fst.output_project()
        result_fst.minimize()
        result_fst.set_name(name)
        return result_fst

    def Morphophonemic(self, ast):
        """Surface completion

        Returns a FST which accepts sequences of valid pairs whose
        input side is accepted by the input side of the argument.
        For a single symbol pair k:g it is equivalent to k:
        """
        name = "[{}].m".format(ast.expr.get_name())
        result_fst = ast.expr.copy()
        result_fst.input_project()
        all_pairs_fst = cfg.all_pairs_fst.copy()
        result_fst.compose(all_pairs_fst)
        result_fst.minimize()
        result_fst.set_name(name)
        return result_fst

    def Surface(self, ast):
        """Morphophonemic completion

        Returns a FST which accepts sequences of valid pairs whose
        ouput side is accepted by the output side of the argument.
        For a single symbol pair k:g it is equivalent to :g
        """
        name = "[{}].s".format(ast.expr.get_name())
        temp_fst = ast.expr.copy()
        temp_fst.output_project()
        result_fst = cfg.all_pairs_fst.copy()
        result_fst.compose(temp_fst)
        result_fst.minimize()
        result_fst.set_name(name)
        return result_fst

    def One_but_not(self, ast):
        name = r"\[{}]".format(ast.expr.get_name())
        result_fst = cfg.all_pairs_fst.copy()
        result_fst.minus(ast.expr)
        result_fst.minimize()
        result_fst.set_name(name)
        return result_fst

    def optexpression(self, ast):
        result_fst = ast.expr.copy()
        name = result_fst.get_name()
        result_fst.optionalize()
        result_fst.minimize()
        result_fst.set_name("({})".format(name))
        return result_fst

    def subexpression(self, ast):
        name = "[{}]".format(ast.expr.get_name())
        result_fst = ast.expr.copy()
        result_fst.set_name(name)
        return result_fst

    def symbol_or_pair(self, ast):
        string = ast.token.strip()
        failmsg = []
        #pat = re.compile(r"""^
        #(?P<up>[a-zšžåäöüõA-ZÅÄÖ0-9'´`]*
        # |
        # \{[a-zåäöüõA-ZÅÄÖØ'´`]+\})
        #:
        #(?P<lo>[a-zšžåäöüõA-ZÅÄÖØ'´`]*)
        #$""", re.X)
        pat = re.compile(r"""^
        (?P<up>[^- \[\]\/<>=_;,.|&*+\\()\{\}]*
         |
         \{[^{}:\s]+\})
        :
        (?P<lo>[^- \[\]\/<>=_;,.|&*+\\()\{\}]*)
        $""", re.X)
        m = re.match(pat, string)
        if m:                       # it is a pair with a colon
            up = m.group("up")
            up_quoted = re.sub(r"([{}])", r"%\1", up)
            lo = m.group("lo")
            if up and (up not in cfg.input_symbol_set):
                failmsg.append("input symbol '{}'".format(up))
            if lo and (lo not in cfg.output_symbol_set):
                failmsg.append("output symbol '{}'".format(lo))
            if up and lo and ((up, lo) not in cfg.symbol_pair_set):
                failmsg.append("symbol pair '{}'".format(string))
            if failmsg:
                cfg.error_message = " and ".join(failmsg) + " not in alphabet"
                raise FailedSemantics(cfg.error_message)
            elif up and lo:         # it is a valid pair with a colon
                result_fst = hfst.regex(up_quoted + ':' + lo)
                result_fst.set_name(string)
                return result_fst
            elif up and (not lo):
                result_fst = hfst.regex(up_quoted)
                result_fst.compose(cfg.all_pairs_fst)
                result_fst.set_name(string)
                return result_fst
            elif (not up) and lo:
                result_fst = cfg.all_pairs_fst.copy()
                lo_fst = hfst.regex(lo)
                result_fst.compose(lo_fst)
                result_fst.set_name(string)
                return result_fst
            else:
                result_fst = cfg.all_pairs_fst.copy()
                result_fst.set_name("PI")
                return result_fst
        m = re.fullmatch(r"[^][|+*{}:\s]+", string)
        if m:                       # its either a defined sym or a surf ch
            if string in cfg.definitions:
                result_fst = cfg.definitions[string].copy()
                result_fst.set_name(string)
                return result_fst
            elif (string in cfg.output_symbol_set) and (string in cfg.input_symbol_set):
                result_fst =  hfst.regex(string)
                result_fst.set_name(string)
                return result_fst
            elif string in {'BEGIN', 'END'}:
                result_fst = hfst.regex(string)
                result_fst.set_name(string)
                return result_fst
        cfg.error_message = "'" + string + "' is an invalid pair/definend symbol"
        raise FailedSemantics(cfg.error_message)

    def boundary(self, ast):
        result_fst = hfst.regex("END")
        #print(result_fst)####
        result_fst.set_name(".#.")
        return result_fst

def init():
    """Initializes the module and compiles and returns a tatsu parser

    grammar_file -- the name of the file containing the EBNF grammar for rules
"""
    import os
    dir = os.path.dirname(os.path.abspath(__file__))
    grammar_file = dir + "/twolcsyntax.ebnf"
    grammar = open(grammar_file).read()
    parser = compile(grammar)
    return parser

def parse_rule(parser, line_nl, line_no, line_lst, start="expr_start"):
    """Parse one rule or definiton or any constituent given as start

    parser -- a tatsu parser which parses the EBNF grammar for two-level rules
    line_nl -- the string that contains the rule or definition to be parsed

    keyword arguments:
    start -- the element in the EBNF grammar where to start the parsing
"""
    line = line_nl.strip()
    if (not line) or line[0] == '!':
        return "!", None, None  # it was a comment or an empty line
    rulepat = r"^.* +(=|<=|=>|<=>|/<=|<--) +.*$"
    try:
        m = re.match(rulepat, line)
        if m:
            #print("groups:", m.groups())###
            if m.group(1) == '=':
                op, name, expr_fst = parser.parse(line, start='def_start',
                                                  semantics=TwolFstSemantics())
                return op, name, expr_fst
            elif m.group(1) in {'=>', '<=', '<=>', '/<=', '<--'}:
                op, x_fst, contexts = parser.parse(line, start='rul_start',
                                                   semantics=TwolFstSemantics())
                return op, x_fst, contexts
        else:
             return "?", None, None
    except ParseException as e:
        print("\n" + 40 * "*")
        print("ERROR WAS IN INPUT LINES:",
              line_no, "-", line_no + len(line_lst) - 1)
        print("".join(line_lst))
        print("THE ERROR IS LIKELY ABOVE THE '^' OR BEFORE IT")
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
        return "?", None, None

def main():
    import hfst
    import argparse
    import twol.twbt as twbt
    import twol.cfg as cfg
    import twol.twexamp as twexamp
    arpar = argparse.ArgumentParser(
        description="A compiler and tester for two-level rules")
    arpar.add_argument("start",
                        help="start parsing from",
                        default="expr_start")
    args = arpar.parse_args()
    twexamp.read_fst(filename="nounex.fst")
    parser = init()
    for line_nl in sys.stdin:
        line = line_nl.strip()
        #print(line)
        result = parser.parse(line, start=args.start,
                              semantics=TwolFstSemantics())
        if args.start == "def_start":
            op, left, right, source = result
            print(left, "=")
            twbt.ppfst(right)
        elif args.start == "rul_start":
            op, left, right, source = result
            twbt.ppfst(left)
            print(op)
            for lc, rc in right:
                twbt.ppfst(lc, title="left context")
                twbt.ppfst(rc, title="right context")
        elif args.start == "expr_start":
            fst = result
            #print(fst)
            twbt.ppfst(fst, True)
        elif op == "?":
            print("Incorrect: " + line)
        return

if __name__ == '__main__':
    main()
