"""alphabet.py

Processes an alphabet definition file so that it can be used both by
aligner.py and by multialign.py.  In particular, it computes weights
for phoneme pairs or morphophonemes for the purposes of weighted
alignment.

Copyright 2017-2020, Kimmo Koskenniemi

This is free software according to GNU GPL 3 license.
"""

import sys, re
#import cfg
import twol.cfg as cfg
from twol.cfg import verbosity

cost_of_zero_c = 25
"""Additional weight for a subset of consonants if Ø belongs to it"""
cost_of_zero_v = 10

feature_lst_lst = [["Zero"], ["Zero"], ["Zero"], ["Zero"], ["Zero"], ["Zero"]]
                             # six lists, one for each group of features
feature_bit_loc_pos = {}     # bit position of the feature within the
                             # 16 bit field of the group
phoneme_to_full_bin = {}     # a 6*16 bit vector which represents the
                             # feature sets of this phoneme
full_bin_to_phoneme_set = {} # gives the phoneme set previously stored
                             # for a 96 bit integer
vowel_set = set()            # set of vowels including semivowels
consonant_set = set()        # set of consonants including semivowels
mphon_weight = {}            # a cache for morphophoneme weights
for_definitions_lst = []     # list of ... FOR X IN ... definitions
exception_lst = []           # list of weighting exceptions

def spaced_bin_int(intg):
    bs = "{:096b}".format(intg)
    spaced_str = bs[0:16] + " " + bs[16:32] + " " + bs[32:48] + " " + bs[48:64] + " " + bs[64:80] + " " + bs[80:96]
    return spaced_str

def mphon_weight(mphon):
    """Returns the weight of a morphophoneme

    :param mphon: A morphophoneme, e.g. 'ij'
    :type mphon: string
    
    :return: The weight of MPHON based on the honological features of its members
    :rtype: float"""

    global weight_c1, weight_c2, weight_c3, weight_v1, weight_v2, weight_v3
    if re.fullmatch(r"[Ø]+", mphon):
        return 999999
    mphon_int = phoneme_to_full_bin[mphon]
    if verbosity > 10:
        print("\nphoneme_to_full_bin[{}] = {}".format(mphon,
                                                      spaced_bin_int(mphon_int)))
    high = mphon_int >> 48               # extract consonantal feature bits
    if high:
        c1 = high >> 32                  # place of articulation set
        c2 = (high >> 16) & 0xffff       # voicing set
        c3 = high & 0xffff               # manner of articulation set
        w = weight_c1[c1] + weight_c2[c2] + weight_c3[c3]
        if verbosity >= 10:
            print("\nmphon_weight info of a cons set:", hex(c1), weight_c1[c1],
                  hex(c2), weight_c2[c2], hex(c3), weight_c3[c3])
    else:
        low = mphon_int & 0xffffffffffffffffffffffff # extract vocalic feature bits
        v1 = low >> 32                   # tongue height
        v2 = (low >> 16) & 0xffff        # backness
        v3 = low & 0xffff                # rounding
        w = weight_v1[v1] + weight_v2[v2] + weight_v3[v3]
        if verbosity >= 10:
            print("\nmphon_weight info of a vowel set:", hex(v1), weight_v1[v1],
                  hex(v2), weight_v2[v2], hex(v3), weight_v3[v3])
    if verbosity >= 10:
        print("\nmphon_int[{}]  = {}".format(mphon, spaced_bin_int(mphon_int)))
        print("mphon_weight[{}] = {}".format(mphon, w))
    return w

def mphon_is_valid(mphon):
    old = mphon[:-1]            # the phonemes which are already included
    new = mphon[-1:]            # the phoneme being included
    ###print(old, new) #####
    if  (old not in phoneme_to_full_bin) or (new not in phoneme_to_full_bin):
        sys.exit("** MORPHOPHONEME {} NOT SEEN EARLIER:".format(mphon))
    old_int = phoneme_to_full_bin[old]
    new_int = phoneme_to_full_bin[new]
    if re.fullmatch(r"[Ø]+", mphon):
        res = phoneme_to_full_bin["Ø"]
        phoneme_to_full_bin[mphon] = res
        if res not in full_bin_to_phoneme_set:
            full_bin_to_phoneme_set[res] = set()
        full_bin_to_phoneme_set[res].add(mphon)
        #print("{Ø}:", mphon, res) ####################
        return True
    old_high = old_int >> 48    # extract consonantal feature bits
    new_high = new_int >> 48    # 
    if old_high and new_high:
        res = (old_high | new_high) << 48
        phoneme_to_full_bin[mphon] = res
        if res not in full_bin_to_phoneme_set:
            full_bin_to_phoneme_set[res] = set()
        full_bin_to_phoneme_set[res].add(mphon)
        if verbosity > 10:
            print("\nphoneme_to_full_bin[{}] = {}".format(mphon, spaced_bin_int(res)))
        return True
    else:
        old_low = old_int & 0xffffffffffff # extract vocalic feature bits
        new_low = new_int & 0xffffffffffff
        if old_low and new_low:
            res = old_low | new_low
            phoneme_to_full_bin[mphon] = res
            if res not in full_bin_to_phoneme_set:
                full_bin_to_phoneme_set[res] = set()
            full_bin_to_phoneme_set[res].add(mphon)
            if verbosity > 10:
                print("\nphoneme_to_full_bin[{}] = {}".format(mphon, spaced_bin_int(res)))
            return True
        else:
            return False

def read_alphabet(file_name):
    global weight_c1, weight_c2, weight_c3, weight_v1, weight_v2, weight_v3
    subset_lst = []              # list of pairs (set, weight)
    feature_group = {}           # the group to which this feature belongs
    features_of_phoneme = {}     # tuples of six features for a phoneme
    with open(file_name, "r") as f:
        features_of_phoneme["Ø"] = ("Zero","Zero","Zero","Zero","Zero","Zero")
        i = 0
        for line_nl in f:
            i += 1
            line = line_nl.split("#")[0].strip()
            if not line:
                continue
            mat1 = re.fullmatch(r":?(?P<symbol>\w):? *= *(?P<feats>\w*( *, *\w*)+)",
                                line)
            if mat1:            # it defines features of a phoneme
                r_lst = [feat.strip() for feat in mat1.group("feats").split(",")]
                if len(r_lst) != 6:
                    msg = "** WRONG NUMBER OF FEATURES ON LINE {}:\n{}"
                    sys.exit(msg.format(i, line))
                if mat1.group("symbol") in features_of_phoneme:
                    msg = "** {} ALREADY DEFINED. LINE {}:\n{}"
                    sys.exit(msg.format(mat1.group("symbol"), i, line_nl))
                features_of_phoneme[mat1.group("symbol")] = tuple(r_lst)
                for ls, feat in zip(feature_lst_lst, r_lst):
                    if not feat in ls and feat:
                        ls.append(feat)
                continue
            mat2 = re.fullmatch(r"(?P<elements>\w+( +\w+)+) *= *(?P<weight>[0-9]+)",
                                line)
            if mat2:
                # it defines a subset and its weight
                l_lst = mat2.group("elements").split()
                subset_lst.append((set(l_lst), int(mat2.group("weight"))))
                continue
            mat3 = re.fullmatch(r"Zero *[+]= *(?P<consw>[0-9]+) +(?P<voww>[0-9]+)",
                                line)
            if mat3:
                # it defines the cost of including a Zero in sets
                cost_of_zero_c = int(mat3.group("consw"))
                cost_of_zero_v = int(mat3.group("voww"))
                continue
            mat4 = re.fullmatch(
                r"(?P<expr>(\w:\w +)*\w:\w::[0-9]+) +FOR +(?P<var>\w+) +IN +(?P<set>\w+)",
                line)
            if mat4:
                # it defines a FOR IN definition
                for_definitions_lst.append((mat4.group("expr"),
                                           mat4.group("var"), mat4.group("set")))
                continue
            mat5 = re.fullmatch("(?P<expr>(\w:\w +)*\w:\w::[0-9]+)", line)
            if mat5:
                exception_lst.append(mat5.group("expr"))
                continue
            msg = "** INCORRECT ALPHABET DEFINITON LINE {}:\n {}"
            sys.exit(msg.format(i, line_nl))

    feature_set_lst = [set(lst) for lst in feature_lst_lst]
    #
    # now the alphabet data has been read in and extracted
    #
    if verbosity > 10:
        print("\ncost_of_zero_c:", cost_of_zero_c)
        print("\ncost_of_zero_v:", cost_of_zero_v)
        print("\nfeature_set_lst:", feature_set_lst)
        print("\nfeature_lst_lst:", feature_lst_lst)
        print("\nsubset_lst:", subset_lst)
        print("\nfeatures_of_phoneme:", features_of_phoneme)
        print("\nfor_definitions_lst:", for_definitions_lst)
        print("\nexception_lst:", exception_lst)
    #
    # find the groups and bit positions of individual features
    #
    i = 0
    for feature_lst in feature_lst_lst:
        j = 0
        for feature in feature_lst:
            feature_group[feature] = i
            feature_bit_loc_pos[feature] = j
            j +=1
        i += 1
    del feature_group["Zero"]   # feature Zero belongs all groups and needs special care
    if verbosity > 10:
        print("\nfeature_group:", feature_group)
        print("\nfeature_bit_loc_pos:", feature_bit_loc_pos)
    #
    # An integer for each phoneme.  The integer represents six sets
    # (with one element in each set).  The sets are 16 bit long fields
    # of the binary representation of the integer, total of 96 bits.
    # Each set has a bit position reserved for each feature in the
    # respective group.  These integers or bit vectors can be combined
    # with each other using bit operations.
    #
    for phoneme, features in features_of_phoneme.items():
        intset = 0
        for feature in features:
            if feature:
                bit_pos = feature_bit_loc_pos[feature]
                bin_set = 1 << bit_pos
                intset = (intset << 16) | bin_set
            else:
                intset = (intset << 16)
            phoneme_to_full_bin[phoneme] = intset
        if intset not in full_bin_to_phoneme_set:
            full_bin_to_phoneme_set[intset] = set()
        full_bin_to_phoneme_set[intset].add(phoneme)
    if verbosity > 10:
        lst = [fon + "=" + spaced_bin_int(intg) for fon, intg in
               sorted(phoneme_to_full_bin.items())]
        s = "\n".join(lst)
        print("\nphoneme_to_full_bin")
        print(s)
        t = "\n".join([spaced_bin_int(intg) + " = " + str(fon_set)
                       for intg, fon_set in sorted(full_bin_to_phoneme_set.items())])
        print("\nfull_bin_to_phoneme_set")
        print(t)
    #
    # sets of vowels and consonants
    #
    for phoneme, features in features_of_phoneme.items():
        if features[0] and features[1] and features[2]:
            consonant_set.add(phoneme)
        elif features[3] and features[4] and features[5]:
            vowel_set.add(phoneme)    
    #
    # convert the subsets into integers which represent bit vectors of the sets
    #
    subset_bin_lst = []
    for subset, weight in subset_lst:
        group_lst = list(set([feature_group[feature] for feature in subset]))
        if len(group_lst) == 1:
            group = group_lst[0]
        else:
            sys.exit("** FEATURES FROM SEVERAL GROUPS: {} = {}".format(subset, group_lst))
        #print("\ngroup:", subset, weight, group) ###
        bin_set = 0
        for feat in subset:
            bin_set = bin_set | (1 << feature_bit_loc_pos[feat])
        if verbosity > 15:
            print("\nsubset, bin_set, weight, group:", subset, bin(bin_set), weight, group) ###
        subset_bin_lst.append((bin_set, weight, group, bin(bin_set)))
    if verbosity > 10:
        print("\nsubset_bin_lst:", subset_bin_lst)
    #
    # compute weights for all possible feature sets in each of the six groups
    #
    i = 0
    weight_dict_lst = []
    for feature_lst in feature_lst_lst:
        weight_dict = {}
        weight_dict[0] = -1     # empty set
        weight_dict[1] = 100    # {"Zero"}
        l = len(feature_lst)
        #mask = ~(~0 << l)
        mask = 0xffffffffffff
        for j in range(2, 1 << l, 2):
            w = 100
            for subset_bin, weight, group, bin_str in subset_bin_lst:
                if verbosity >= 20:
                    print("\nsubset_bin, weight, group, bin_str, i:", bin(j), weight, group, bin_str, i)
                #if group == i and ((subset_bin | ~j) & mask) == mask and weight < w:
                test = ~(subset_bin | ~j)
                if verbosity >= 15:
                    print(">>> test:", bin(test)) ###
                if group == i and not test and weight < w:
                    w = weight
            weight_dict[j] = w
            weight_dict[j+1] = w + (cost_of_zero_c if i < 3 else cost_of_zero_v)
        for j in range(1, l):
            weight_dict[1 << j] = 0
            weight_dict[(1 << j) +1] = (cost_of_zero_c if i < 3 else cost_of_zero_v)
        if verbosity > 10:
            print("\nweight_dict[{}]:".format(i), weight_dict)
            #for set_int, weight in weight_dict.items():
            #    for phoneme, feature_tuple in features_of_phoneme.items():
            #        feature = feature_tuple[i]
            #        ***
                
        weight_dict_lst.append(weight_dict)
        i += 1
    (weight_c1, weight_c2, weight_c3, weight_v1, weight_v2, weight_v3) = weight_dict_lst
    #if verbosity > 10:
    #    print("\nweight_dict_lst:", weight_dict_lst)
    return

if __name__ == "__main__":
    verbosity = 1
    read_alphabet("alphabet-et.text")
    mphon_is_valid("ei")
    print(mphon_weight("ei"))
