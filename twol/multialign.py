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


def init(alphabet_file_name, all_zero_weight=1):
    """Initializes multialign by initializing the alphabet module
alphabet_file_name -- an alphabet definition as described in https://pytwolc.readthedocs.io/en/latest/alignment.html#alphabet

all_zero_weight -- penalty for an intermediate morphophoneme of only zeros (which will get a non-zero component in the final morphophoneme)"""
    alphabet.read_alphabet(alphabet_file_name)
    cfg.all_zero_weight = all_zero_weight
    return


def print_result(aligned_result, comments, weights, layout="horizontal"):
    """Prints the result of the alignment in one of the three formats

aligned_result -- tuple of the weight and a list of aligned words where each aligned word is a list of 

comments -- possible comments which will be passed over

weights -- whether to print also the overall weight of this alignment

layout -- one of "horizontal" (a sequence of morphophonemes on a single line), "vertical" (each zero-filled word on a line of its own) or "list" (all zero-filled words on a single line)"""

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


def accum_input_labels(fst, separator=""):
    """Encode, weight and prune a transducer

fst -- transducer to be processed, input labels are strings of alphabet symbols and output labels are single alphabet symbols

separator -- null string or a symbol not part of the alphabet

Returns a transducer where input labels of thrasitions are concatenations of the input label and the output label of the original transition, the weights are according to the weights of the resulting morphophonemes and all transitions with invalid morphophoneme labels are discarded.
"""
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
            new_insym = insym + separator + outsym
            if cfg.verbosity >= 25:
                print("arc", state, tostate, insym, outsym, weight)
            if not alphabet.mphon_is_valid(new_insym):
                continue
            new_weight = alphabet.mphon_weight(new_insym)
            result_arc = hfst.HfstBasicTransition(tostate,
                                                  new_insym,
                                                  new_insym,
                                                  new_weight)
            result_bfst.add_transition(state, result_arc)
            if cfg.verbosity >= 25:
                print("after addition of transition:\n", result_bfst)
    result_fst = hfst.HfstTransducer(result_bfst)
    result_fst.minimize()
    if cfg.verbosity >= 10:
        print("accumulated fst:\n", result_fst)
    return result_fst


def list_of_aligned_words(mphon_lst):
    """Converts a list of morphophonemes into a list of aligned words

mphon_lst -- list of same length morphophonemes, e.g.
    ["lll", "ooo", "vvv", "ieØ"]

Returns a list of words constructed out of the 1st, 2nd ... alphabetic
symbols of the morphophonemes, e.g.  ["lll", "ooo", "vvv", "ieØ"] -->
["lovi", "love", "lovØ"]

    """
    if not mphon_lst:
        return []
    lgth = grapheme.length(mphon_lst[0])
    res = []
    for i in range(lgth):
        syms = [grapheme.slice(itm,start=i, end=i+1) for itm in mphon_lst]
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

Returns a sequence of (single) symbols where the zeros occur near the
end.  This normalizes gemination and lengthening so that the latter
component is the one which alternates with a zero.
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


def word_to_fsa_with_zeros(word, target_len, zero="Ø"):
    """Insert zeros freeley to make the word into a fst of target_lenth words

word -- a string

target_len -- length of the strings accepted by the result fsa

Returns a fsa that accepts all strings of length target_length where some zeros have been added to make the word be target_len long.
"""
    word_len = grapheme.length(word)
    zeros_fst = fs.string_to_fsa(zero)
    zeros_fst.repeat_n(target_len - word_len)
    fst = fs.string_to_fsa(word)
    fst.shuffle(zeros_fst)
    fst.minimize()
    return fst


def align_words(word_lst, zero="Ø", extra_zeros=0, best_count=10):
    """Aligns a list of words

word_lst -- the list of words to be aligned

zero -- the symbol inserted as a mark for deletion or epenthesis

extra_zeros -- the maximun number of zeros to be added in the longest
    words (the shorter may have more)

best_count -- the maximum number of results to be returned (maybe less
    if no feasible results are found)

Returns a list of tuples where each tuple consists of a weight and a
list morphophonemes.
    """
    target_len = max([grapheme.length(x) for x in word_lst]) + extra_zeros
    fst = word_to_fsa_with_zeros(word_lst[0], target_len, zero)
    if cfg.verbosity >= 10:
        print("first fst with shuffled zeros:\n", fst)
    i = 1
    for word in word_lst[1:]:
        word_fsa = word_to_fsa_with_zeros(word, target_len, zero)
        fst.cross_product(word_fsa)
        fst = accum_input_labels(fst)
        if cfg.verbosity >= 10:
            print("fst accumulated with", word, ":\n", fst)

    fst.n_best(best_count)
    fst.minimize()
    if cfg.verbosity >= 10:
        print("aligned result:\n", fst)
    weight_path_lst = fst.extract_paths(output='raw')
    weight_mphon_lst_lst = []
    for weight, path_lst in weight_path_lst:
        mphon_lst = [insym for insym, outsym in path_lst]
        weight_mphon_lst_lst.append((weight, mphon_lst))
    if cfg.verbosity >= 10:
        print("weight_mphon_lst_lst:", weight_mphon_lst_lst)
    return weight_mphon_lst_lst


def adjustment(mphon_lst):
    """Computes an context based adjustment of a result

mphon_lst -- a list of morphophonemes from the result of align_words

Returns a number to be added to the weight.
    """
    adj = 10 * len(mphon_lst)
    phon_set_lst = [set(mphon)  for mphon in mphon_lst]
    if phon_set_lst[-1] <= alphabet.vowel_set | set("Ø"):
        adj -= 20
    for this_set, next_set in zip(phon_set_lst[:-1], phon_set_lst[1:]):
        if len(this_set) == 1 and next_set == this_set | set("Ø"):
            adj -= 20
    return adj

def multialign(word_lst,
               zero="Ø",
               max_zeros=1, best_count=1):
    """Aligns a list of words according to similarity of their phonemes

word_lst -- a list of words (or morphs) to be aligned

zero -- the symbol that will mark deletions or epentheses

max_zeros -- maximum number of zeros to be inserted into the longest
    word

best_count -- number of results to returned

Returns a list of results each of which is a tuple of a weight and a
list of words aligned by inserting zeros in an optimal way.

    """
    if len(word_lst) < 1:
        return []                 # nothing to align
    elif len(word_lst) == 1:
        return ((0,(word_lst),),) # only one word to align

    # process only the subset of unique words starting from the longest
    unique_words_lst = sorted(list(set(word_lst)),
                              key= lambda word: -len(word))
    aligned_results_lst = []
    for i in range(max_zeros + 1):
        result_lst = align_words(unique_words_lst,
                                 zero=zero,
                                 extra_zeros=i,
                                 best_count=best_count+9)
    
        for weight, alg_syms_lst in result_lst[:best_count]:
            if weight >= 1000:
                continue
            if cfg.verbosity >= 10:
                print("alg_syms_lst", alg_syms_lst)
            weight += adjustment(alg_syms_lst)
        
            aligned_words_lst = list_of_aligned_words(alg_syms_lst)

            # apply the alignment to the original word list with possible duplicates
            d = {}
            for uniqw, aligw in zip(unique_words_lst, aligned_words_lst):
                d[uniqw] = aligw
            aligned_orig_words_lst = [d[word] for word in word_lst]
            aligned_results_lst.append((weight, aligned_orig_words_lst))
    
    if cfg.verbosity >= 10:
        print("aligned_results_lst:", aligned_results_lst)
    return sorted(aligned_results_lst, key = lambda r: r[0])[:best_count]
        
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

    init(args.alphabet, all_zero_weight=1000)

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
