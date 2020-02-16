"""multialign.py

Aligns two words or more (or morphs) by adding some zero symbols so
that phonemes in corresponding positions are optimally similar.

Copyright 2020, Kimmo Koskenniemi

This is free software according to GNU GPL 3 license.

"""

import hfst
import grapheme
import twol.fs as fs
import twol.cfg as cfg
import twol.twbt as twbt
import twol.alphabet as alphabet
import twol.metric as metric

aligner_fst = hfst.HfstTransducer()


def init(alphabet_file_name):
    global aligner_fst
    alphabet.read_alphabet(alphabet_file_name)
    aligner_fst = metric.alignment_fst()
    if cfg.verbosity >= 20:
        twbt.ppfst(aligner_fst)
    return

def accum_input_labels(fst, separator="", feat_weight_factor=0):
    if cfg.verbosity >= 10:
        twbt.ppfst(fst, title="to be accumulated")
    bfst = hfst.HfstBasicTransducer(fst)
    result_bfst = hfst.HfstBasicTransducer()
    for state in bfst.states():
        result_bfst.add_state(state)
        if bfst.is_final_state(state):
            weight = bfst.get_final_weight(state)
            result_bfst.set_final_weight(state, weight)
        for arc in bfst.transitions(state):
            tostate = arc.get_target_state()
            insym = arc.get_input_symbol()
            outsym = arc.get_output_symbol()
            weight = arc.get_weight()
            res_insym = insym + separator + outsym
            if cfg.verbosity >= 15:
                print("arc", state, tostate, insym, outsym, weight)
            if not alphabet.mphon_is_valid(res_insym):
                continue
            feat_weight = alphabet.mphon_weight(res_insym)
            weight = weight + feat_weight_factor * feat_weight
            result_arc = hfst.HfstBasicTransition(tostate,
                                                  res_insym,
                                                  outsym,
                                                  weight)
            result_bfst.add_transition(state, result_arc)
            if cfg.verbosity >= 25:
                twbt.ppfst(result_bfst, title="after addition of transition")
    if cfg.verbosity >= 10:
        twbt.ppfst(result_bfst, title="accumulated fst")
    result_fst = hfst.HfstTransducer(result_bfst)
    return result_fst

def align_words(word_lst,
                zero="Ø",
                max_zeros=1, best_count=10):
    global aligner_fst

    zero_fst = fs.string_to_fsa(zero)
    word_len_lst = [grapheme.length(x) for x in word_lst]
    word_len_max = max(word_len_lst)
    if cfg.verbosity >= 10:
        print("word_lst:", word_lst)
        print("word_len_lst:", word_len_lst)
        print("word_len_max:", word_len_max)
    word_fst_lst = [fs.string_to_fsa(word) for word in word_lst]
    zeros_fst = zero_fst.copy()
    zeros_fst.repeat_n_to_k(word_len_max - word_len_lst[0],
                            word_len_max - word_len_lst[0] + max_zeros)
    zeros_fst.minimize()
    if cfg.verbosity >= 10:
        twbt.ppfst(zeros_fst, title="first zeros_fst")
    fst = word_fst_lst[0].copy()
    fst.shuffle(zeros_fst)
    fst.minimize()
    if cfg.verbosity >= 10:
        twbt.ppfst(fst, title="shuffled first word fst")
    i = 1
    if cfg.verbosity >= 10:
        twbt.ppfst(fst, title=word_lst[0])
    for word, word_len, word_fst in zip(word_lst[1:],
                                        word_len_lst[1:], word_fst_lst[1:]):
        fst.compose(aligner_fst)
        fst.minimize()
        if cfg.verbosity >= 10:
            twbt.ppfst(fst, title="fst composed with aligner")
        zeros_fst = zero_fst.copy()
        zeros_fst.repeat_n_to_k(word_len_max - word_len,
                                word_len_max - word_len + max_zeros)
        zeros_fst.minimize()
        if cfg.verbosity >= 10:
            twbt.ppfst(zeros_fst, title="zeros_fst")
        word_fst.shuffle(zeros_fst)
        word_fst.minimize()
        if cfg.verbosity >= 10:
            twbt.ppfst(word_fst, title="shuffled word_fst")
        i += 1
        fst.compose(word_fst)
        fst.minimize()
        if cfg.verbosity >= 10:
            twbt.ppfst(fst, title="composed fst")
        ##fst.n_best(best_count + 100) ####
        ###fact = 0
        fact = 1 * len(word_lst) if i == len(word_lst) else 0
        fst = accum_input_labels(fst, feat_weight_factor=fact)
        if cfg.verbosity >= 10:
            twbt.ppfst(fst, title=word)
    
    fst.n_best(best_count)
    fst.minimize()
    if cfg.verbosity >= 10:
        twbt.ppfst(fst, title="aligned result")
    raw_paths = fst.extract_paths(output='raw')
    if cfg.verbosity >= 10:
        print("raw_paths:", raw_paths)
    return raw_paths

def list_of_aligned_words(sym_lst):
    if not sym_lst:
        return []
    lgth = grapheme.length(sym_lst[0])
    res = []
    for i in range(lgth):
        syms = [grapheme.slice(itm,start=i, end=i+1) for itm in sym_lst]
        res.append("".join(syms))
    return res

def multialign(word_lst,
               zero="Ø",
               max_zeros=1, best_count=1):
    if len(word_lst) < 1:
        return []
    elif len(word_lst) == 1:
        return ((0,(word_lst),),)
    
    unique_words_lst = sorted(list(set(word_lst)),
                              key= lambda word: -len(word))
    raw_paths = align_words(unique_words_lst,
                            zero=zero,
                            max_zeros=max_zeros,
                            best_count=best_count)
    aligned_results_lst = []
    for raw_path in raw_paths:
        weight, pairs_tuple = raw_path
        alg_syms_lst = [alg_syms for alg_syms, out_sym in pairs_tuple]
        if cfg.verbosity >= 10:
            print("alg_syms_lst", alg_syms_lst)
        aligned_words_lst = list_of_aligned_words(alg_syms_lst)
        d = {}
        for uniqw, aligw in zip(unique_words_lst, aligned_words_lst):
            d[uniqw] = aligw
        aligned_orig_words_lst = [d[word] for word in word_lst]
        aligned_results_lst.append((weight, aligned_orig_words_lst))
    if cfg.verbosity >= 10:
        print("aligned_results_lst:", aligned_results_lst)
    return aligned_results_lst
        
def print_result(aligned_result, comments, weights, layout="horizontal"):

    weight, aligned_words_lst = aligned_result
    if cfg.verbosity >= 10:
        print("aligned_result", aligned_result)
    
    if layout == "horizontal":
        lgth = grapheme.length(aligned_words_lst[0])
        mphon_lst = []
        for i in range(lgth):
            lst = []
            for aligned_word in aligned_words_lst:
                symbol = grapheme.slice(aligned_word, start=i, end=i+1)
                lst.append(symbol)
            if len(set(lst)) == 1:
                mphon_str = lst[0]  # abbreviate if all identical
            else:
                mphon_str = "".join(lst)
            mphon_lst.append(mphon_str)
        zstem_pairsym_str = " ".join(mphon_lst)

        mphonemic_str = " ".join(mphon_lst)
        if weights:
            print(mphonemic_str.ljust(40), weight)
        else:
            print(mphonemic_str)
    elif layout == "vertical":
        print("\n".join(aligned_words_lst))
        print()
    elif layout == "list":
        print(" ".join(aligned_words_lst))
    return

def main():

    version = "2020-02-15"
    
    import argparse
    arpar = argparse.ArgumentParser(
        "twol-aligner",
        description="""Aligns lists of words separated by
        a COMMENT-SEPARATOR.  See
        https://pytwolc.readthedocs.io/en/latest/alignment.html for
        detailed instructions. Version {}""".format(version))
    arpar.add_argument(
        "alphabet",
        help="An alphabet definition file with features and similarity sets.")
    arpar.add_argument(
        "-d", "--delimiter",
        help="Separates the two cognates, default is ' '",
        default=" ")
    arpar.add_argument(
        "-l", "--layout",
        choices=["vertical","list","horizontal"],
        help="output layout",
        default="vertical")
    arpar.add_argument(
        "-c", "--comment-separator",
        help="""Comment separator. Comments in input after this
        character are just copied to output. Input words are then
        also copied to the end of comments. Default separator is ''
        i.e. no comments.  Comments come to the output only in
        horizontal layout.""",
        default="")
    arpar.add_argument(
        "-w", "--weights",
        help="print also the weight of each alignment."
        " Default is not to print."
        " Works only if a comment separator is also set.",
        action="store_true")
    arpar.add_argument(
        "-n", "--number",
        help="number of best results to be printed. Default is 1",
        type=int, default=1)
    arpar.add_argument(
        "-v", "--verbosity",
        help="Level of diagnostic information to be printed. "
        "Default is 0",
        type=int, default=0)

    args = arpar.parse_args()

    if args.verbosity:
        cfg.verbosity = args.verbosity

    init(args.alphabet)

    separator = args.delimiter
    import sys
    for line in sys.stdin:
        if args.comment_separator:
            word_str, comm, comments = \
                line.strip().partition(args.comment_separator)
        else:
            word_str, comm, comments = line.strip(), "", ""
        if args.verbosity > 0:
            print(word_str, args.comment_separator, comm)
        word_lst =  word_str.strip().split(args.delimiter)

        aligned_results_lst = multialign(word_lst,
                                         zero="Ø",
                                         best_count=args.number)
        if cfg.verbosity >= 10:
            print("aligned_results_lst:", aligned_results_lst)
        for aligned_result in aligned_results_lst:
            print_result(aligned_result,
                         comments,
                         args.weights,
                         layout=args.layout)
    return

if __name__ == "__main__":
    main()
