"""Module for compiling two-level rules out of FSTs for the components.
"""
__author__ = "© Kimmo Koskenniemi, 2018 - 2020"
__version__ = "2020-02-01"
import re
import hfst
import twol.cfg as cfg
import twol.fs as fs
import twol.twbt as twbt
import twol.twexamp as twexamp

def init():
    """Initializes the module by computing several common FSTs
    
    Assumes that twexamp.read_fst() has read in cfg.examples_fst and
    initialized sone symbol sets.
    """
    global pistar_fst, pistar_fsa, diamond_sym, diamond_fst
    global trim_pre_fst, trim_post_fst

    assert cfg.examples_fst, "cfg.examples_fst not loaded (by twexamp module)"

    cfg.definitions["PAIRS"] = cfg.all_pairs_fst.copy() 
    cfg.definitions["PI"] = cfg.all_pairs_fst.copy() 

    diamond_sym = 'DIAMOND'
    diamond_fst = hfst.regex(diamond_sym)
    pi_fst = cfg.all_pairs_fst.copy()
    pistar_fst = cfg.all_pairs_fst.copy()
    pistar_fst.repeat_star()
    pistar_fst.remove_epsilons()
    pistar_fst.minimize()
    pistar_fsa = hfst.fst_to_fsa(pistar_fst, separator='^')
    pi_in_fst = pi_fst.copy()
    pi_in_fst.input_project()
    pi_out_fst = pi_fst.copy()
    pi_out_fst.output_project()
    pi_in_star_fst = pistar_fst.copy()
    pi_in_star_fst.input_project()
    pi_out_star_fst = pistar_fst.copy()
    pi_out_star_fst.output_project()
    if cfg.verbosity >= 20:
        twbt.ppfst(pistar_fst, title="pistar_fst")

    fst1 = fs.star(fs.crossprod(fs.expr("ZERO"),
                                 pi_in_fst))
    fst2 = fs.star(fs.concat(fst1,
                             fs.expr("ZERO:BEGIN")))
    fst3 = fs.concat(fst2, pi_in_star_fst)
    fst4 = fs.star(fs.concat(fs.expr("ZERO:END"),
                             fs.star(fs.crossprod(fs.expr("ZERO"),
                                                  pi_in_fst))))
    trim_pre_fst = fs.concat(fst3, fst4)
    trim_pre_fst.set_name("trim_pre_fst")
    #trim_pre_fst =  XRC.compile(
    #    "[[ZERO .x. [PI].u]* ZERO:BEGIN]* " \
    #    "[[PI].u]* " \
    #    "[ZERO:END [ZERO .x. [PI].u]*]*"
    #)

    fst1 = fs.star(fs.crossprod(pi_out_fst, fs.expr("ZERO")))
    fst2 = fs.star(fs.concat(fst1, fs.expr("BEGIN:ZERO")))
    fst3 = fs.concat(fst2, pi_out_star_fst)
    fst4 = fs.star(fs.concat(fs.expr("END:ZERO"),
                             fs.star(fs.crossprod(pi_out_fst,
                                                  fs.expr("ZERO")))))
    trim_post_fst = fs.concat(fst3, fst4)
    trim_post_fst.set_name("trim_post_fst")
    #trim_post_fst = XRC.compile(
    #    "[[[PI].l .x. ZERO]* BEGIN:ZERO]* " \
    #    "[[PI].l]* " \
    #    "[END:ZERO [[PI].l .x. ZERO]*]*"
    #)
    if cfg.verbosity >= 20:
        twbt.ppfst(trim_pre_fst)
        twbt.ppfst(trim_post_fst)
    return


def quote(str):
    """Protect '{' and '}' with a % in xerox regular expressions.

    >>> quote("a {ij}:j [a:c | b]")
    "a %{ij%}:j [a:c | b]"
    """
    return(re.sub(r"([{'}])", r"%\1", str))

def e(str):
    """Convert a two-level component expression into a FST.
    
    str -- a string containing a (two-level) regular expression
    Returns an FST which performs the mapping represented by str 
    corresponding to the expression. 
    """
    global XRC
    # print("Regex string:", str) ##
    if str == "":
        return(XRC.compile("[]"))
    F = XRC.compile(str)
    F.minimize()
    F.set_name(str)
    if cfg.verbosity >= 5:
        twbt.ppfst(F) ##
    return(F)

def generalized_restriction(precondition_fst,
                            postcondition_fst):
    """Combines the precondition FST and the postcondition FST into a rule FST.

    Conditions are formed out of the center/contexts of a rule.
    Each condition contains exactly two diamond symbols.
    
    Returns the generalized restriction as an FST.
    """
    global pistar_fst, diamond_sym
    temp_fst = precondition_fst.copy()
    temp_fst.subtract(postcondition_fst)
    temp_fst.minimize()
    temp_fst.set_name("PRECOND-POSTCOND")
    # twbt.ppfst(temp_fst, True) ##
    temp_fst.substitute(diamond_sym, hfst.EPSILON)
    # print(temp_fst.get_properties().items()) ##
    temp_fst.minimize()
    temp_fst.set_name("Diamonds removed")
    # twbt.ppfst(temp_fst, True) ##
    result_fst = pistar_fst.copy()
    result_fst.minus(temp_fst)
    result_fst.minimize()
    # twbt.ppfst(result_fst, True) ##
    result_fst.set_name("Doubly negated")
    # twbt.ppfst(result_fst, True) ##
    return(result_fst)

def x_to_condition(x_fst):
    """Computes and returns a condition FST out of the center FST of a rule.

    x_fst -- the center or X-part of a rule (located in front of the
    operator)

    returns [PI* ¤ X ¤ PI*] where ¤ is the diamond (not in PI) as an FST
    """
    global pistar_fst, diamond_fst
    result_fst = pistar_fst.copy()
    result_fst.concatenate(diamond_fst)
    result_fst.concatenate(x_fst)
    result_fst.concatenate(diamond_fst)
    result_fst.concatenate(pistar_fst)
    result_fst.minimize()
    result_fst.set_name("PISTAR ¤ X ¤ PISTAR")
    # twbt.ppfst(result_fst, True) ##
    return(result_fst)

def begin_end(expr_fst):
    """Removes everything before BEGIN and after END from expr_fst

    expr_fst -- an FST representing a set of pair strings str

    Returns an FST which represents pair strings which are maximal
    substrings of the above which do not contain any BEGIN or END
    symbols.
    """
    global trim_pre_fst, trim_post_fst
    result_fst = trim_pre_fst.copy()
    result_fst.compose(expr_fst)
    # twbt.ppfst(result_fst, True) ##
    result_fst.compose(trim_post_fst)
    # twbt.ppfst(result_fst, True) ##
    result_fst.substitute("ZERO", hfst.EPSILON)
    result_fst.minimize()
    # twbt.ppfst(result_fst, True) ##
    return(result_fst)

def context_to_condition(left_context_fst,
                         right_context_fst):
    """Convert one context into a condition (for the generalized restriction)
    
    left_context_fst -- the left context as an FST
    
    right_context_fst -- the right context as an FST
    
    Returns [PI* LC ¤ PI* ¤ RC PI*] as an FST
    """
    global pistar_fst, diamond_fst
    leftc_fst = pistar_fst.copy()
    leftc_fst.concatenate(left_context_fst)
    leftc_fst.minimize()
    result_fst = begin_end(leftc_fst)
    result_fst.concatenate(diamond_fst)
    result_fst.concatenate(pistar_fst)
    result_fst.concatenate(diamond_fst)
    rightc_fst = right_context_fst.copy()
    rightc_fst.concatenate(pistar_fst)
    rightc_fst.minimize()
    rightc_fst = begin_end(rightc_fst)
    result_fst.concatenate(rightc_fst)
    result_fst.minimize()
    return(result_fst)

def contexts_to_condition(*contexts):
    """A list of contexsts is converted into a condition.
    
    Each context in the list is converted separately and
    the result is the union of these and is returned as an FST.
    """
    global pistar_fst
    result_fst = hfst.HfstTransducer()
    for leftc, rightc in contexts:
        #twbt.ppfst(leftc, title="leftc") ##
        #twbt.ppfst(rightc, title="rightc") ##
        context_fst = context_to_condition(leftc, rightc)
        result_fst.disjunct(context_fst)
        result_fst.minimize()
        leftc_name = leftc.get_name()
        rightc_name = rightc.get_name()
        result_fst.set_name(leftc_name + "_" + rightc_name)
        #twbt.ppfst(result_fst, title="result") ##
    return(result_fst)

def mix_output(x_fst):
    """Computes an FSA that is used when creating negative examples
    
    First, it computes an expression Y which represent all possible
    (correct and incorrect) realizations of the input side of X.  Then,
    Y is transformed into an encoded FSA which can be a component of the
    transformation of correct examples into incorrect ones.
    
    x_fst -- the center FST (X part) of a rule Returns [X.u .o. PI*]
    encoded as an FSA (i.e. maps pairs to themselves)
    """
    global pistar_fst
    result_fst = x_fst.copy()
    result_fst.input_project()
    result_fst.compose(pistar_fst)
    result_fst.minimize()
    result_encod_fsa = hfst.fst_to_fsa(result_fst, separator="^")
    # twbt.ppfst(result_fsa, True) ##
    return result_encod_fsa

def mix_input(x_fst):
    """Computes an FSA that is used when creating negative examples
    
    First, it computes an expression Y which represent all possible
    (correct and incorrect) inputs for the output side of X.  Then,
    Y is transformed into an encoded FSA which can be a component of the
    transformation of correct examples into incorrect ones.
    
    x_fst -- the center FST (X part) of a rule Returns [PI* .o. X.l]
    encoded as an FSA (i.e. maps pairs to themselves)
    """
    global pistar_fst
    result_fst = pistar_fst.copy()
    temp_fst = x_fst.copy()
    temp_fst.output_project()
    result_fst.compose(temp_fst)
    result_fst.minimize()
    result_encod_fsa = hfst.fst_to_fsa(result_fst, separator="^")
    # twbt.ppfst(result_fsa, True) ##
    return result_encod_fsa

def selector_from_x(x_fst):
    """Compute and return [PI* X PI*]"""
    selector_fst = pistar_fst.copy() # starting to build it
    selector_fst.concatenate(x_fst)
    selector_fst.concatenate(pistar_fst) # now complete
    selector_fst.set_name("Selector " + x_fst.get_name())
    return selector_fst

def correct_to_incorrect(x_fst, side):
    """used for creating negative examples for <= rules
    
    In order to make negative examples for <= rules we need to transform
    the examples so that some correct input:output pairs are
    changed so that the output part becomes different.  The computed
    encoded FST maps correct inputs to any possible outputs (correct or
    incorrect).

    x_fst -- the FST for the X part of the rule

    side -- either "input" or "output"

    returns: an fst (encoded as a fsa) which maps correct examples into
    incorrect exs
    """
    global pistar_fst, pistar_fsa
    if side == "input":
        mixed_fsa = mix_input(x_fst)
    else:
        mixed_fsa = mix_output(x_fst)
    temp_encod_fsa = hfst.fst_to_fsa(x_fst, separator="^")
    temp_encod_fsa.cross_product(mixed_fsa) # now maps corr X to all variations
    # twbt.ppfst(temp_encod_fsa, True) ##
    corr_to_incorr_encod_fst = pistar_fsa.copy()
    corr_to_incorr_encod_fst.concatenate(temp_encod_fsa)
    corr_to_incorr_encod_fst.concatenate(pistar_fsa)
    corr_to_incorr_encod_fst.minimize() # now complete
    corr_to_incorr_encod_fst.set_name("Correct to incorrect")
    return corr_to_incorr_encod_fst

def incorrect_to_correct(x_fst):
    """Compute a transformation for right-arrow (=>) rules
    
    In order to make negative examples for the => rules we need to
    modify the examples so that some correct occurrences of X are
    modified so that the output part of X becomes something else,
    i.e. incorrect because it is in an unexpected context.
    
    x_fst -- FST for the center part (X) of a rule
    
    Returns: scrambler_fst -- an encoded FST which maps encoded
    instances of X into all possible correct and incorrect pairs (where
    the input symbol is the same but the output symbol perhaps
    different).
    """
    global pistar_fst, pistar_fsa
    x_encod_fsa = hfst.fst_to_fsa(x_fst, separator="^")
    mix_fst = mix_output(x_fst) # still an encoded fsa
    mix_fst.cross_product(x_encod_fsa) # now fst
    scrambler_fst = pistar_fsa.copy()
    scrambler_fst.concatenate(mix_fst)
    scrambler_fst.concatenate(pistar_fsa)
    scrambler_fst.minimize() # now complete
    scrambler_fst.set_name("Scrambler " + x_fst.get_name())
    return scrambler_fst

def rightarrow(name, x_fst, *contexts):
    """Compiles rules like X => [LC1,RC1),...(LCk,RCk)]
    
    name -- name to be given to the rule FST
    
    x_fst -- the center (X) of the rule
    
    \*contexts -- list of contexts, i.e. pairs of left and right context
    
    Returns a triple:
    rule_fst -- the compiled rule
    
    selector_fst -- FST which selects examples which are relevant for
    this rule
    
    scrambler_fst -- an encoded FST which produces negative examples
    """
    precondition_fst = x_to_condition(x_fst)
    postcondition_fst = contexts_to_condition(*contexts)
    rule_fst = generalized_restriction(precondition_fst, postcondition_fst)
    rule_fst.set_name(name)
    # twbt.ppfst(rule_fst, True) ##
    selector_fst = selector_from_x(x_fst)
    scrambler_fst = incorrect_to_correct(x_fst)
    # twbt.ppfst(scrambler_fst, True) ##
    return rule_fst, selector_fst, scrambler_fst

def output_coercion(name, x_fst, *contexts):
    """Compiles rules like X <= LC1 _ RC1, ..., LCk _ RCk
    
    name -- name to be given to the rule FST
    
    x_fst -- the center (X) of the rule
    
    \*contexts -- list of contexts, i.e. pairs of left and right context
    
    Returns a triple:
    rule_fst -- the compiled rule
    
    selector_fst -- FST which selects examples which are relevant for
    this rule
    
    scrambler_fst -- an encoded FST which produces negative examples
    """
    global pistar_fst
    postcondition_fst = x_to_condition(x_fst)
    x_all_fst = x_fst.copy()
    x_all_fst.input_project()
    x_all_fst.compose(pistar_fst)
    precondition_fst = x_to_condition(x_all_fst)
    context_condition_fst = contexts_to_condition(*contexts)
    precondition_fst.intersect(context_condition_fst)
    rule_fst = generalized_restriction(precondition_fst, postcondition_fst)
    rule_fst.set_name(name)
    if cfg.verbosity >= 20:
        twbt.ppfst(rule_fst, True)
    x_any_fst = x_fst.copy()
    x_any_fst.input_project()
    x_any_fst.compose(pistar_fst)
    ###x_any_fst.minus(x_fst)
    selector_fst = selector_from_x(x_any_fst)
    scrambler_fst = correct_to_incorrect(x_fst, "output")
    return rule_fst, selector_fst, scrambler_fst

def input_coercion(name, x_fst, *contexts):
    """Compiles rules like X <-- LC1 _ RC1, ..., LCk _ RCk
    
    name -- name to be given to the rule FST
    
    x_fst -- the center (X) of the rule
    
    \*contexts -- list of contexts, i.e. pairs of left and right
    context
    
    Returns a triple:
    rule_fst -- the compiled rule
    
    selector_fst -- FST which selects examples which are relevant for
    this rule
    
    scrambler_fst -- an encoded FST which produces negative examples
    """
    global pistar_fst
    postcondition_fst = x_to_condition(x_fst)
    x_all_fst = pistar_fst.copy()
    temp_fst = x_fst.copy()
    temp_fst.output_project()
    x_all_fst.compose(temp_fst) # PI* .o. X.l
    precondition_fst = x_to_condition(x_all_fst)
    context_condition_fst = contexts_to_condition(*contexts)
    precondition_fst.intersect(context_condition_fst)
    rule_fst = generalized_restriction(precondition_fst, postcondition_fst)
    rule_fst.set_name(name)
    if cfg.verbosity >= 20:
        twbt.ppfst(rule_fst, True)
    selector_fst = selector_from_x(x_all_fst)
    scrambler_fst = correct_to_incorrect(x_fst, "input")
    return rule_fst, selector_fst, scrambler_fst

def doublearrow(name, x_fst, *contexts):
    """Compiles rules like X <=> [LC1,RC1),...(LCk,RCk)]
    
    name -- name to be given to the rule FST
    
    x_fst -- the center (X) of the rule
    
    \*contexts -- list of contexts, i.e. pairs of left and right
    context
    
    Returns a triple:
    
    rule_fst -- the compiled rule
    
    selector_fst -- FST which selects examples which are relevant for
    this rule
    
    scrambler_fst -- an encoded FST which produces negative examples

    """
    rule_fst, selector_fst, scrambler_fst = rightarrow(name, x_fst, *contexts)
    rule2_fst, selector2_fst, scrambler2_fst = output_coercion(name, x_fst, *contexts)
    rule_fst.intersect(rule2_fst)
    rule_fst.minimize()
    rule_fst.set_name(name)
    scrambler_fst.disjunct(scrambler2_fst)
    scrambler_fst.minimize()
    selector_fst.disjunct(selector2_fst)
    selector_fst.minimize()
    # twbt.ppfst(rule_fst, True) ##
    return rule_fst, selector_fst, scrambler_fst

def center_exclusion(name, x_fst, *contexts):
    """Compiles rules like X /<= [LC1,RC1),...(LCk,RCk)]
    
    name -- name to be given to the rule FST
    
    x_fst -- the center (X) of the rule
    
    \*contents -- list of contexts, i.e. pairs of left and right context
    
    Returns a triple:
    
    rule_fst -- the compiled rule
    
    selector_fst -- FST which selects examples which are relevant for this rule
    
    scrambler_fst -- empty_fst (negative examples not relevant for these rules)
    """
    context_condition_fst = contexts_to_condition(*contexts)
    x_condition_fst = x_to_condition(x_fst)
    context_condition_fst.intersect(x_condition_fst)
    null_fst = hfst.empty_fst()
    rule_fst = generalized_restriction(context_condition_fst, null_fst)
    rule_fst.set_name(name)
    # twbt.ppfst(rule_fst, True) ##
    selector_fst = selector_from_x(x_fst)
    scrambler_fst = hfst.empty_fst()
    return rule_fst, selector_fst, scrambler_fst

if __name__ == "__main__":
    """This module forms the rule FSTs out of the collection of component
FSTs which have been compiled out of the center parts, left and right
contexts of the rules.  The formulas used in the module are those from
[ylijyrä2006]_.  """
    
    twex.read_examples()
    init(1)
    #define("V", "PI .o.[a|e|i|o|ä|ö]")
    #define("C", "[PI .o. [h|l|n|s|t|v]] | %{ij%}:j")
    R1 = doublearrow("{ao}:o <=> _ {ij}:",
                     e("%{ao%}:o"),
                     (e("[]"), e("[%{ij%} .o. PI]")))
    twbt.ppfst(R1, True)
    rule2_fst = doublearrow("{ij}:j <=> V :Ø* _ :Ø* V",
                     "%{ij%}:j",
                     ("V [PI .o. Ø]*", "[PI .o. Ø]* V"))
    twbt.ppfst(rule2_fst, True)
    R3 = doublearrow("{tl}:l <=> _ CLOSED",
                     "%{tl%}:l",
                     ("[]", "V %{ij%}:i* C [C | [PI .o. Ø]* END]"))
    twbt.ppfst(R3, True)
