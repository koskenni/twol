"""Aligns multiple morphs according to phonological features
by adding zero symbols.

Copyright 2015-2020, Kimmo Koskenniemi

This is free software according to GNU GPL 3 License.
"""

import re, sys
import hfst
import grapheme
import twol.cfg as cfg
import twol.alphabet as alphabet

def remove_bad_transitions(fsa):
    """Copy the FSA excluding transitions with consonants and vowels"""
    old_bfsa = hfst.HfstBasicTransducer(fsa)
    new_bfsa = hfst.HfstBasicTransducer()
    for state in old_bfsa.states():
        new_bfsa.add_state(state)
        if old_bfsa.is_final_state(state):
            new_bfsa.set_final_weight(state, 0.0)
        for arc in old_bfsa.transitions(state):
            in_sym = arc.get_input_symbol()
            ##print(in_sym, "is")#####
            if alphabet.mphon_is_valid(in_sym):
                ##print("valid")#####
                target_st = arc.get_target_state()
                new_bfsa.add_transition(state, target_st, in_sym, in_sym, 0)
    result_fsa = hfst.HfstTransducer(new_bfsa)
    result_fsa.minimize()
    if cfg.verbosity >= 20:
        print("remove_bad_transitions:")
        print(result_fsa)
    return result_fsa

def shuffle_with_zeros(string, target_length):
    """Return a fsa where zeros are inserted in all possible ways
    
    string -- the string to which zero symbols are inserted

    target_length -- how long the strings after insertions must be

    Returns a fsa which accepts all the strings with the inserted zeros.
    All strings have exactly target_length symbols.
    """
    from twol.fs import string_to_fsa
    
    ### result_fsa = hfst.fst(string) # not correct for composed graphemes !!!
    result_fsa = string_to_fsa(string)
    l = grapheme.length(string)
    if l < target_length:
        n = target_length - l
        n_zeros_fsa = hfst.regex(" ".join(n * "Ø"))
        result_fsa.shuffle(n_zeros_fsa)
    result_fsa.minimize()
    result_fsa.set_name(string)
    if cfg.verbosity >= 30:
        print("shuffle_with_zeros:")
        print(result_fsa)
    return result_fsa

def set_weights(fsa):
    """Sets weights to transitions using mphon_weight()
    """
    bfsa = hfst.HfstBasicTransducer(fsa)
    for state in bfsa.states():
        for arc in bfsa.transitions(state):
            tostate = arc.get_target_state()
            insym = arc.get_input_symbol()
            outsym = arc.get_output_symbol()
            w = alphabet.mphon_weight(insym)
            arc.set_weight(w)
    weighted_fsa = hfst.HfstTransducer(bfsa)
    if cfg.verbosity >=20:
        print("set_weights:\n", weighted_fsa)
    return weighted_fsa

def multialign(strings, target_length):
    """Align a list of strings by making them target_lenght long
    
    Zero symbols are added optimally so that the sets of corresponding
    phonemes are similar.  Note that the alignment need not be feasible
    if the target lenght is too small and also that there may be
    all-zero correspondences if the target length is too long.
    """
    s1 = strings[0]
    fsa = shuffle_with_zeros(s1, target_length)
    for string in strings[1:]:
        suf_fsa = shuffle_with_zeros(string, target_length)
        fsa.cross_product(suf_fsa)      # results in a transducer
        if cfg.verbosity >=30:
            print("fsa\n", fsa)
        prod_fsa = hfst.fst_to_fsa(fsa)      # encodes the fst as a fsa
        fsa = remove_bad_transitions(prod_fsa)
        fsa.minimize()
    wfsa = set_weights(fsa)
    if cfg.verbosity >=20:
        print("multialign:\n", wfsa)
    return wfsa

def list_of_aligned_words(sym_lst):
    if not sym_lst:
        return []
    l = grapheme.length(sym_lst[0])
    res = []
    for i in range(l):
        syms = [grapheme.slice(itm,start=i, end=i+1) for itm in sym_lst]
        res.append("".join(syms))
    return res

def prefer_final_zeros(sym_lst_lst):
    """Select the symbol pair sequence where the zeros are near the end

    sym_lst_lst -- a list of results, each consisting of a list
    of symbols (already selected according to other criteria)

    Returns a sequence of (single) symbols where the zeros occur near
    the end.  This normalizes gemination and lengthening so that the
    latter component is the one which alternates with a zero.
    """
    best_bias = -1
    for sym_lst in sym_lst_lst:
        lst = [isym for isym in sym_lst]
        bias = 0
        i = 0
        for isym in lst:
            bias = bias + i * isym.count("Ø")
            i = i + 1
        #print("  ".join(lst), w, bias) ##
        if bias > best_bias:
            best_bias = bias
            best_sym_lst = lst
    return best_sym_lst

def classify_sym(sym):
    #from twolalign.alphabet import consonant_set
    char_set = set(sym)
    if char_set <= alphabet.consonant_set:
        if "Ø" in char_set:
            return "c"
        else: return "C"
    elif "Ø" in char_set:
        return "v"
    else: return "V"

def prefer_syl_struct(results):
    """Selects alignments according to syllable structure and zero count

    results -- list of tuples (weight, sym_pair_seq) (out of which the
    result list is chosen).  The sym_pair_seq is in the format that
    hfst.extract_paths() produces.

    Returns a list the best alternatives, i.e. those getting the lowest
    scores of the sum of syllable count and the number of instances
    where the former component of a CC or VV corresponds to zero.
    Elements in the returned list are sequences of symbols.
    """
    best_weight = results[0][0]
    best_bias = 99999
    best_lst = []
    for weight, sym_pair_seq in results:
        if weight > best_weight: break
        sym_lst = [isym for isym,outsym in sym_pair_seq]
        #print("sym_lst:", "  ".join(sym_lst)) ##
        csym_lst = [classify_sym(sym) for sym in sym_lst]
        csym_str = "".join(csym_lst)
        #print("csym_lst:", "  ".join(csym_lst)) ##
        syl_bias = len(re.findall(r"(C|c)+|(V|v)+", csym_str))
        #print("syl_bias:", syl_bias)###
        zero_bias = len(re.findall(r"(cC|vV)", csym_str))
        #print("zero_bias:", zero_bias)###
        bias = 3 * syl_bias + 2 * zero_bias
        if bias < best_bias:
            best_bias = bias
            best_lst = []
        if bias <= best_bias:
            best_lst.append(sym_lst)
            
    #print("best:", best_lst, "\n")####
    return best_lst

def aligner(words, max_zeros_in_longest, line):
    """Aligns a list of words according to similarity of their phonemes

    words -- a list of words (or morphs) to be aligned

    max_zeros_in_longest -- maximum number of zeros to be inserted into
    the longest word

    line -- the input line (used only in warning messages)

    cfg.all_zero_weight -- if phoneme set is {"Ø"} (default 100.0)

    Returns the best alignment as a list of raw morphophoneme.
    """

    if max([len(w) for w in words]) == 0:
        return []

    max_length = max([grapheme.length(x) for x in words])
    weighted_fsa = hfst.empty_fst()
    for m in range(max_length, max_length + max_zeros_in_longest + 1):
        R = multialign(words, m)
        if R.compare(hfst.empty_fst()):
            if cfg.verbosity > 1:
                print("target length", m, "failed")
            continue
        weighted_fsa.disjunct(R)
        weighted_fsa.minimize()
    weighted_fsa.n_best(10) 
    weighted_fsa.minimize() # accepts 10 best results
    results = weighted_fsa.extract_paths(output="raw")
    if cfg.verbosity >= 5:
        for w, sym_pair_seq in results:
            lst = [isym for isym, outsym in sym_pair_seq]
            mpw = ["{}::{:.2f}".format(x, alphabet.mphon_weight(x)) for x in lst]
            print(" ".join(mpw), "total weight = {:.3f}".format(w))
    if len(results) < 1:
        print("*** NO ALIGNMENTS FOR:", line, "***", results)
        return([])
    best_syl_struct = prefer_syl_struct(results)
    if cfg.final:
        best = prefer_final_zeros(best_syl_struct)
    else:
        best = best_syl_struct[0]
    return best

def main():
    import re, sys
    import hfst
    import grapheme

    version = "2020-02-01"
    import argparse
    arpar = argparse.ArgumentParser(
        "twol-multialign",
        description="Aligns sets of words separated by blanks"\
        " by inserting Ø symbols to make them equal length so that"\
        " similar phonemes correspond to each other. See"\
        " https://pytwolc.readthedocs.io/en/latest/alignment.html"\
        " for detailed instructions. Version {}".format(version))
    arpar.add_argument("alphabet",
        help="A file which defines the phonemes through their distinctive features",
        default="")
    arpar.add_argument("-l", "--layout",
        choices=["vertical","list","horizontal"],
        help="Output layout",
        default="vertical")
    arpar.add_argument("-f", "--final",
        help="Prefer deletion at the end",
        action="store_false")
    arpar.add_argument("-w", "--weights",
        help="Print the weight of each alignment",
        action="store_true")
    arpar.add_argument("-c", "--comments",
        help="Copy input words to the output lines as comments",
        default=False,
        action="store_true")
    arpar.add_argument("-v", "--verbosity",
        help="Level of diagnostic output",
        type=int, default=0)
    arpar.add_argument("-x", "--extra-zeros",
        help="Number of extra zeros allowed beyond the minimum",
        type=int, default=1)
    args = arpar.parse_args()

    cfg.verbosity = args.verbosity

    alphabet.read_alphabet(args.alphabet)

    if args.final:
        cfg.final = args.final
    valid_letters = alphabet.vowel_set | alphabet.consonant_set | set(" ")

    for line in sys.stdin:
        line = line.strip()
        lst = line.split("!", maxsplit=1)
        if len(lst) > 1:
            line = lst[0].strip()
            number = lst[1].strip() + " "
        else:
            number = ""
        if set(line) - valid_letters:
            print("** SOME LETTERS NOT VALID:",
                  set(line) - valid_letters,
                  "ON LINE: ", line)
            continue
        words = line.split()
        comment = number + " ".join(words)
            
        best = aligner(words, args.extra_zeros, line) # returns a list of morphoponemes
        if args.weights:
            weight = 0
            for mphon in best:
                weight += alphabet.mphon_weight(mphon)
            comment = "{:.2f} ".format(weight) + comment

        if args.layout == "horizontal":
            mphonemic_best = []
            for cc in best:
                grapheme_list = list(grapheme.graphemes(cc))
                lab = grapheme_list[0] if len(set(grapheme_list)) == 1 else cc
                mphonemic_best.append(lab)
            if args.comments:
                print(" ".join(mphonemic_best).ljust(40),"!", comment)
            else:
                print(" ".join(mphonemic_best))
        elif args.layout == "vertical":
            #print("best:", best) ###
            #print("len(best):", [len(x) for x in best]) ###
            print("\n".join(list_of_aligned_words(best)))
            print()
        elif args.layout == "list":
            print(" ".join(list_of_aligned_words(best)))
    return

if __name__ == "__main__":
    main()
