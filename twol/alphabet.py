"""alphabet.py

Processes an alphabet definition file so that it can be used both by
aligner.py and by multialign.py.  In particular, it computes weights
for phoneme pairs or morphophonemes for the purposes of weighted
alignment.

Copyright 2017-2020, Kimmo Koskenniemi

This is free software according to GNU GPL 3 license.
"""

import sys, re
import twol.cfg as cfg

cost_of_zero_c = 25
"""Additional weight for a subset of consonants if Ø belongs to it."""

cost_of_zero_v = 10
"""Additional weight for a subset of vowels if Ø belongs to it."""

feature_lst_lst = [["Zero"], ["Zero"], ["Zero"], ["Zero"], ["Zero"], ["Zero"]]
                             # six lists, one for each group of features

feature_bitpos = {}
"""The bit position of the feature within the 16 bit field of the group."""

mphon_to_binint_cache = {}
"""A 6*16 bit vector which represents the feature sets of this phoneme."""

binint_to_mphon_set = {}
"""For a binint, it gives the set of phoneme set previously stored for
a 96 bit integer."""

vowel_set = set()
"""The set of vowels including semivowels."""

consonant_set = set()
"""The set of consonants including semivowels."""

mphon_weight_cache = {}
"""A cache for morphophoneme weights."""

phoneme_set_weight_cache = {}
"""Given weights for phoneme sets represented by "".join(sorted(set(MPHON)))"""

for_definitions_lst = []
"""A list of ... FOR X IN ... definitions to be used in metric.py"""

exception_lst = []
"""A list of weighting exceptions to be used in metric.py"""

def spaced_bin_int(intg):
    """binint to human readable string conversion."""
    bs = "{:096b}".format(intg)
    spaced_str = (bs[0:16] + " " + bs[16:32] + " " + bs[32:48] +
                  " " + bs[48:64] + " " + bs[64:80] + " " + bs[80:96])
    return spaced_str

def mphon_to_binint(mphon):
    """Converts a morphophoneme into a binary integer that represents it.

    :param mphon: A string of phonemes and possibly Øs
    :type mphon: str
    :return: A binary integer which represents the morphophoneme
    :rtype: int
    """
    if cfg.verbosity >= 25:
        print("mphon_to_binint({})".format(mphon))
    if not mphon:
        return 0
    if mphon in mphon_to_binint_cache:
        return mphon_to_binint_cache[mphon]
    if len(mphon) == 1:
        msg = "** '{}' NOT IN ALPHABET\n\n".format(mphon)
        exit(msg)
    old = mphon[:-1]
    new = mphon[-1:]
    if new not in mphon_to_binint_cache:
        msg = "** '{}' IN '{}' NOT IN ALPHABET\n\n".format(new, mphon)
        exit(msg)
    if old in mphon_to_binint_cache:
        binint =  mphon_to_binint_cache[old] | mphon_to_binint_cache[new]
        mphon_to_binint_cache[mphon] = binint
        return binint
    else:
        return mphon_to_binint(old) | mphon_to_binint_cache[new]
    
def mphon_is_valid(mphon):
    """Tests whether a set of phonemes is possible.

    :param mphon: A sequence of phonemes a.k.a. morphophoneme, e.g. 'ij'.  
    :type mphon: str
    
    :return: True if the set consists either of vowels (and semivowels and Øs) \
    or of consonants (and semivowels and Øs), otherwise False.

    :rtype: boolean
    """

    binint = mphon_to_binint(mphon)
    if cfg.verbosity >= 30:
        print("mphon_is_valid({}) == {}".format(mphon, spaced_bin_int(binint)) )
    if not(~ binint & 0xffffffffffffffffffffffff): # (U,U,U,U,U,U)
        return False
    else:
        return True
    
def mphon_weight(mphon):
    """Returns the weight of a morphophoneme

    :param mphon: A sequence of phonemes a.k.a. morphophoneme, e.g. 'ij'
    :type mphon: str
    
    :return: The weight of mphon based on the phonological features of its members 
    :rtype: float
    """
    global weight_c1, weight_c2, weight_c3, weight_v1, weight_v2, weight_v3
    if re.fullmatch(r"[Ø]+", mphon):
        return cfg.all_zero_weight
    phon_set_str = "".join(sorted(set(mphon)))
    if phon_set_str in phoneme_set_weight_cache:
        return phoneme_set_weight_cache[phon_set_str]
    if mphon in mphon_weight_cache:
        return mphon_weight_cache[mphon]
    mphon_int = mphon_to_binint_cache[mphon]
    if cfg.verbosity >= 25:
        print("\nmphon_to_binint_cache[{}] = {}".format(mphon,
                                                      spaced_bin_int(mphon_int)))
    w_cons = 999999
    w_vow = 999999
    high = mphon_int >> 48               # extract the 48 cons feature bits
    low = mphon_int & 0xffffffffffff     # extract the 48 voc feature bits
    if cfg.verbosity >= 25:
        print("{:048b}".format(high), "high")
        print("{:048b}".format(low), "low")
    if high != 0xffffffffffff:
        c1 = high >> 32                  # place of articulation set
        c2 = (high >> 16) & 0xffff       # voicing set
        c3 = high & 0xffff               # manner of articulation set
        if cfg.verbosity >= 25:
            print("{:012b}, {:012b}, {:012b}".format(c1, c2, c3))
        w_cons = weight_c1[c1] + weight_c2[c2] + weight_c3[c3]
        if cfg.verbosity >= 25:
            print("\nmphon_weight info of a cons set:", hex(c1), weight_c1[c1],
                  hex(c2), weight_c2[c2], hex(c3), weight_c3[c3])
    if low != 0xffffffffffff:
        v1 = low >> 32                   # tongue height
        v2 = (low >> 16) & 0xffff        # backness
        v3 = low & 0xffff                # rounding
        if cfg.verbosity >= 25:
            print("{:012b}, {:012b}, {:012b}".format(v1, v2, v3))
        w_vow = weight_v1[v1] + weight_v2[v2] + weight_v3[v3]
        if cfg.verbosity >= 25:
            print("\nmphon_weight info of a vowel set:", hex(v1), weight_v1[v1],
                  hex(v2), weight_v2[v2], hex(v3), weight_v3[v3])
    w = min(w_cons, w_vow)
    if cfg.verbosity >= 25:
        print("\nmphon_int[{}]  = {}".format(mphon, spaced_bin_int(mphon_int)))
        print("mphon_weight[{}] = {}".format(mphon, w))
    mphon_weight_cache[mphon] = w
    phoneme_set_weight_cache[phon_set_str] = w
    return w

def read_alphabet(file_name):
    """Reads phoneme features, feature subsets with weights, and other definitions
    
    :param file_name: Name of the file that contains the alphabet definition
    :type file_name: str

    Stores the computed sets and weights for feature subsets and other
    info in module variables for the use of other modules.

    """
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
            mat_phon_feat = re.fullmatch(
                r":?(?P<symbol>(\w|')):? *= *(?P<feats>\w*( *, *\w*)+)",
                line)
            if mat_phon_feat:
                # it defines features of a phoneme
                r_lst = [feat.strip() for feat in mat_phon_feat.group("feats").split(",")]
                if len(r_lst) != 6:
                    msg = "** WRONG NUMBER OF FEATURES ON LINE {}:\n{}"
                    sys.exit(msg.format(i, line))
                if mat_phon_feat.group("symbol") in features_of_phoneme:
                    msg = "** {} ALREADY DEFINED. LINE {}:\n{}"
                    sys.exit(msg.format(mat_phon_feat.group("symbol"), i, line_nl))
                features_of_phoneme[mat_phon_feat.group("symbol")] = tuple(r_lst)
                for ls, feat in zip(feature_lst_lst, r_lst):
                    if not feat in ls and feat:
                        ls.append(feat)
                continue
            mat_feat_set = re.fullmatch(
                r"(?P<elements>\w\w\w+( +\w\w\w+)+) *= *(?P<weight>[0-9]+)",
                line)
            if mat_feat_set:
                # it defines a subset of features and its weight
                l_lst = mat_feat_set.group("elements").split()
                subset_lst.append((set(l_lst), int(mat_feat_set.group("weight"))))
                continue
            mat_phon_set = re.fullmatch(
                r"(?P<weight>[0-9]+) *= *(?P<elements>(\w|')+( +(\w|')+)+)",
                line)
            if mat_phon_set:
                # it defines a subset of features and its weight
                phon_set_str_lst = mat_phon_set.group("elements").split()
                weight = int(mat_phon_set.group("weight"))
                for phon_str in phon_set_str_lst:
                    phon_set_str = "".join(sorted(set(phon_str)))
                    phoneme_set_weight_cache[phon_set_str] = weight
                continue
            mat_zero = re.fullmatch(
                r"Zero *[+]= *(?P<consw>[0-9]+) +(?P<voww>[0-9]+)",
                line)
            if mat_zero:
                # it defines the cost of including a Zero in feature sets
                cost_of_zero_c = int(mat_zero.group("consw"))
                cost_of_zero_v = int(mat_zero.group("voww"))
                continue
            mat_for_in = re.fullmatch(
                r"(?P<expr>(\w:\w +)*\w:\w::[0-9]+) +FOR +(?P<var>\w+) +IN +(?P<set>\w+)",
                line)
            if mat_for_in:
                # it defines a FOR IN definition
                for_definitions_lst.append((mat_for_in.group("expr"),
                                            mat_for_in.group("var"),
                                            mat_for_in.group("set")))
                continue
            mat_exception = re.fullmatch("(?P<expr>(\w:\w +)*\w:\w::[0-9]+)", line)
            if mat_exception:
                # it defines an exception list
                exception_lst.append(mat_exception.group("expr"))
                continue
            msg = "** INCORRECT ALPHABET DEFINITON LINE {}:\n {}"
            sys.exit(msg.format(i, line_nl))

    feature_set_lst = [set(lst) for lst in feature_lst_lst]
    #
    # now the alphabet data has been read in and extracted
    #
    if cfg.verbosity >= 20:
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
            feature_bitpos[feature] = j
            j +=1
        i += 1
    del feature_group["Zero"]   # feature Zero belongs all groups and
                                # needs special care
    if cfg.verbosity >= 20:
        print("\nfeature_group:", feature_group)
        print("\nfeature_bitpos:", feature_bitpos)
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
                bit_pos = feature_bitpos[feature]
                bin_set = 1 << bit_pos
                intset = (intset << 16) | bin_set
            else:
                intset = (intset << 16) | 0xffff
        mphon_to_binint_cache[phoneme] = intset
        if intset not in binint_to_mphon_set:
            binint_to_mphon_set[intset] = set()
        binint_to_mphon_set[intset].add(phoneme)
    if cfg.verbosity >= 20:
        lst = [fon + "=" + spaced_bin_int(intg) for fon, intg in
               sorted(mphon_to_binint_cache.items())]
        s = "\n".join(lst)
        print("\nmphon_to_binint_cache")
        print(s)
        t = "\n".join([spaced_bin_int(intg) + " = " + str(fon_set)
                       for intg, fon_set in sorted(binint_to_mphon_set.items())])
        print("\nbinint_to_mphon_set")
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
            bin_set = bin_set | (1 << feature_bitpos[feat])
        if cfg.verbosity > 25:
            print("\nsubset, bin_set, weight, group:", subset, bin(bin_set), weight, group)
        subset_bin_lst.append((bin_set, weight, group, bin(bin_set)))
    if cfg.verbosity > 20:
        print("\nsubset_bin_lst:", subset_bin_lst)
    #
    # compute weights for all possible feature sets in each of the six groups
    #
    i = 0
    weight_dict_lst = []
    for feature_lst in feature_lst_lst:
        weight_dict = {}
        weight_dict[0] =  -1 # for the empty set
        weight_dict[1] = -1   # {"Zero"}
        weight_dict[0xffff] = 999999 # for the universal set U
        l = len(feature_lst)
        for j in range(2, 1 << l, 2):
            w = 100
            for subset_bin, weight, group, bin_str in subset_bin_lst:
                if cfg.verbosity >= 25:
                    print("\nsubset_bin, weight, group, bin_str, i:",
                          bin(j), weight, group, bin_str, i)
                test = ~(subset_bin | ~j)
                if cfg.verbosity >= 25:
                    print(">>> test:", bin(test)) ###
                if group == i and not test and weight < w:
                    w = weight
            weight_dict[j] = w
            weight_dict[j+1] = w + (cost_of_zero_c if i < 3 else cost_of_zero_v)
        for j in range(1, l):
            weight_dict[1 << j] = 0
            weight_dict[(1 << j) +1] = (cost_of_zero_c if i < 3 else cost_of_zero_v)
        if cfg.verbosity > 20:
            print("\nweight_dict[{}]:".format(i), weight_dict)
            #for set_int, weight in weight_dict.items():
            #    for phoneme, feature_tuple in features_of_phoneme.items():
            #        feature = feature_tuple[i]
            #        ***
                
        weight_dict_lst.append(weight_dict)
        i += 1
    (weight_c1, weight_c2, weight_c3, weight_v1, weight_v2, weight_v3) = weight_dict_lst
    return

if __name__ == "__main__":
    cfg.verbosity = 1
    read_alphabet("alphabet-test.text")
    mphon_is_valid("ei")
    print(mphon_weight("ei"))
