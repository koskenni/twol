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


def init(alphabet_file_name, all_zero_weight=1):
    global aligner_fst
    alphabet.read_alphabet(alphabet_file_name)
    aligner_fst = metric.alignment_fst()
    if cfg.verbosity >= 20:
        twbt.ppfst(aligner_fst)
    cfg.all_zero_weight = all_zero_weight
    return

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

def accum_input_labels(fst, separator="", feat_weight_factor=5):
    if cfg.verbosity >= 10:
        print("to be accumulated:\n", fst)
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
            if cfg.verbosity >= 25:
                print("arc", state, tostate, insym, outsym, weight)
            if not alphabet.mphon_is_valid(res_insym):
                continue
            feat_weight = alphabet.mphon_weight(res_insym)
            ###weight = weight + feat_weight_factor * feat_weight
            weight = feat_weight
            result_arc = hfst.HfstBasicTransition(tostate,
                                                  res_insym,
                                                  outsym,
                                                  weight)
            result_bfst.add_transition(state, result_arc)
            if cfg.verbosity >= 25:
                print("after addition of transition:\n", result_bfst)
    result_fst = hfst.HfstTransducer(result_bfst)
    result_fst.minimize()
    if cfg.verbosity >= 10:
        print("accumulated fst;\n", result_fst)
    return result_fst

def list_of_aligned_words(sym_lst):
    if not sym_lst:
        return []
    lgth = grapheme.length(sym_lst[0])
    res = []
    for i in range(lgth):
        syms = [grapheme.slice(itm,start=i, end=i+1) for itm in sym_lst]
        res.append("".join(syms))
    return res

def print_best(fst, num):
    bests_fst = fst.copy()
    bests_fst.n_best(num)
    bests_fst.minimize()
    raw_paths = bests_fst.extract_paths(output='raw')
    for raw_path in raw_paths:
        weight, pairs_tuple = raw_path
        alg_syms_lst = [alg_syms for alg_syms, out_sym in pairs_tuple]
        alg_syms_str = " ".join(alg_syms_lst)
        print(weight, alg_syms_lst)

def prefer_final_zeros(raw_paths):
    """Select the symbol pair sequence where the zeros are near the end
    sym_lst_lst -- a list of results, each consisting of a list
    of symbols (already selected according to other criteria)
    Returns a sequence of (single) symbols where the zeros occur near
    the end.  This normalizes gemination and lengthening so that the
    latter component is the one which alternates with a zero.
    """
    if cfg.verbosity >= 20:
        print("prefer_final_zeros(raw_paths):", raw_paths)
    max_path_len = max([len(p) for w, p in raw_paths])
    raw_path_lst = []
    for weight, pairs_tuple in raw_paths:
        if cfg.verbosity >= 20:
            print(weight, pairs_tuple)
        mphon_lst = [insym for insym, outsym in pairs_tuple]
        mphon_lst_len = len(mphon_lst)
        if cfg.verbosity >= 20:
            print(mphon_lst)
        i = 5 * mphon_lst_len
        weight += 20 * (mphon_lst_len - max_path_len)
        for mphon in mphon_lst:
            if "Ø" in mphon:
                weight = weight + i
            i -= 5
        raw_path_lst.append((weight, pairs_tuple))
    result_path_lst = sorted(raw_path_lst, key=lambda raw_path: raw_path[0])
    if cfg.verbosity == 20:
        print("result_path_lst:", result_path_lst)
    return result_path_lst

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
        print("first zeros_fst:\n", zeros_fst)
    fst = word_fst_lst[0].copy()
    fst.shuffle(zeros_fst)
    fst.minimize()
    i = 1
    if cfg.verbosity >= 10:
        twbt.ppfst(fst, title=word_lst[0])
    fact = 10 * len(word_lst) if i == len(word_lst) else 0
    for word, word_len, word_fst in zip(word_lst[1:],
                                        word_len_lst[1:], word_fst_lst[1:]):
        fst.compose(aligner_fst)
        ###fst.n_best(best_count + 20) ####
        fst.minimize()
        fact = 5
        fst = accum_input_labels(fst, feat_weight_factor=fact) #########
        if cfg.verbosity >= 10:
            print("fst composed with aligner:\n", fst)
        zeros_fst = zero_fst.copy()
        zeros_fst.repeat_n_to_k(word_len_max - word_len,
                                word_len_max - word_len + max_zeros)
        zeros_fst.minimize()
        if cfg.verbosity >= 10:
            print("zeros_fst:\n", zeros_fst)
        word_fst.shuffle(zeros_fst)
        word_fst.minimize()
        if cfg.verbosity >= 10:
            print("shuffled word_fst:\n", word_fst)
        i += 1
        fst.compose(word_fst)
        fst.n_best(best_count + 50) ####
        fst.minimize()
        if cfg.verbosity >= 10:
            print("composed fst:\n", fst)
        fst.minimize()
        ##fst = accum_input_labels(fst, feat_weight_factor=fact)
        if cfg.verbosity >= 1:
            print_best(fst, 1) #########
        if cfg.verbosity >= 10:
            print(word + "\n", fst)
    
    fst.n_best(best_count)
    fst.minimize()
    if cfg.verbosity >= 10:
        print("aligned result:\n", fst)
    raw_paths = fst.extract_paths(output='raw')
    if not raw_paths:
        return []
    if cfg.verbosity >= 10:
        print("raw_paths:", raw_paths)
    preferred_raw_path_lst = prefer_final_zeros(raw_paths)
    return preferred_raw_path_lst

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
                            best_count=best_count+9)
    aligned_results_lst = []
    for raw_path in raw_paths[:best_count]:
        weight, pairs_tuple = raw_path
        alg_syms_lst = [alg_syms for alg_syms, out_sym in pairs_tuple]
        #** calculate here a penalty for word internal deletions **
        if cfg.verbosity >= 10:
            print("alg_syms_lst", alg_syms_lst)
        aligned_words_lst = list_of_aligned_words(alg_syms_lst)
        d = {}
        for uniqw, aligw in zip(unique_words_lst, aligned_words_lst):
            d[uniqw] = aligw
        aligned_orig_words_lst = [d[word] for word in word_lst]
        aligned_results_lst.append((weight, aligned_orig_words_lst))
    if cfg.verbosity >= 20:
        print("aligned_results_lst:", aligned_results_lst)
    return aligned_results_lst
        
def main():

    version = cfg.timestamp(__file__)
    
    import argparse
    arpar = argparse.ArgumentParser(
        "twol-multialign",
        description="""Version {}\nAligns lists of words separated by
        a DELIMITER.  See
        https://pytwolc.readthedocs.io/en/latest/alignment.html for
        detailed instructions. """.format(version))
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
        "-x", "--extra-zeros", default=0, type=int,
        help="number of extra zeros to be tried in alignment")
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
                                         max_zeros=args.extra_zeros,
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
