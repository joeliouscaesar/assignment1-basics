import regex as re
import os
import functools
from cs336_basics.pretoken_stuff import Pretoken
from cs336_basics.pretoken_stuff import get_pretoken_list

def flatten(x:tuple[bytes]) -> bytes:
    return functools.reduce(lambda a,b: a+b,x)


class AlphabetPair:
    """
    Class for an alphabet pair
    - pair:tuple[bytes] is the pair of alphabet words
    - count: count of this pair in the corpus
    - pretoken_list: list of Pretokens which contain byte pair
    """
    def __init__(self, a1:bytes, a2:bytes):
        self.pair = (a1, a2)
        self.count = 0
        self.pretoken_list:list[Pretoken] = []
    # define an order for alphabet pairs
    def __le__(self, otherpair):
        if otherpair is None:
            return False
        elif self == otherpair:
            return True
        else:
            return self < otherpair
    def __ge__(self, otherpair):
        if otherpair is None:
            return True
        elif self == otherpair:
            return True
        else:
            return self > otherpair
    def __lt__(self, otherpair):
        if otherpair is None:
            return False
        elif self.count < otherpair.count:
            return True
        elif self.count == otherpair.count:
            return self.pair < otherpair.pair
            # return flatten(self.pair) <  flatten(otherpair.pair)
        else:
            return False
    def __gt__(self, otherpair):
        if otherpair is None:
            return True
        return otherpair < self
    def __eq__(self, value):
        return self.count == value.count and self.pair == value.pair

def find_index(x, xs:list):
    """
    Finds index of x in a sorted list
    """
    if xs == []:
        return 0
    lower = 0
    upper = len(xs)
    if x <= xs[lower]:
        return lower
    elif x >= xs[upper-1]:
        return upper
    # so we have xs[lower] < x < xs[upper-1]
    while (upper - lower) > 1:
        mid = (upper + lower) // 2
        if xs[mid] == x:
            return mid
        elif xs[mid] < x:
            lower = mid
        else:
            upper = mid
    return (upper)

def bpe_less_naive(
    input_path: str | os.PathLike,
    vocab_size: int,
    special_tokens: list[str],
    **kwargs
):

    # Initialize Vocabulary
    vocab = [i.to_bytes() for i in range(256)]
    vocab += [bytes(st,"utf-8") for st in special_tokens]
    merges = []

    num_processes = kwargs.get("num_processes", 1)
    num_corpus_splits = kwargs.get("num_corpus_splits", 1)
    
    # get pretoken list
    pretokens:dict = get_pretoken_list(input_path, special_tokens, num_processes, num_corpus_splits)

    # initialize our alphabet pair hash
    alphabet_pair_hash = {}
    for pretoken in pretokens.values():
        for i in range(1, len(pretoken.alphabet_list)):
            pair = (pretoken.alphabet_list[i-1], pretoken.alphabet_list[i])
            # get alphabet pairs, add to alphabet pair hash
            update_alphabet_hash(alphabet_pair_hash, pair, pretoken)

    # make a sorted list of our alphabet pairs by counts/alphabetically
    sorted_alphabet_pair_list = list(alphabet_pair_hash.values())
    sorted_alphabet_pair_list.sort()

    # While vocab is small enough
    while len(vocab) < vocab_size:
        # get max alphabet pair
        maxpair = sorted_alphabet_pair_list[-1]
        if maxpair is None:
            raise Exception("maxpair is none")
        # add to vocab/merges 
        flatmaxpair = flatten(maxpair.pair)
        vocab.append(flatmaxpair)
        merges.append(maxpair.pair)
        # dictionary of pairs we're going to update as a result of this merge
        changed_pairs:dict[tuple[bytes], AlphabetPair] = {}
        # iterate over pretokens this pair is in
        for pretoken in maxpair.pretoken_list:
            # get current indices and decrement old surrounding pair counts
            inds = get_pair_indices(pretoken, maxpair.pair)
            decrement_old_pairs(changed_pairs, pretoken, inds)
            # update this pretoken's alphabet list
            inds = update_alphabet_list(pretoken, maxpair.pair)
            # get updated alphabet pairs from this change
            new_pairs = get_new_pairs(pretoken, inds)
            for pair in new_pairs:
                if pair not in changed_pairs:
                    changed_pairs[pair] = AlphabetPair(*pair)
                changed_pairs[pair].pretoken_list.append(pretoken)
                changed_pairs[pair].count += pretoken.count
    
        # remove old pair
        alphabet_pair_hash.pop(maxpair.pair)
        sorted_alphabet_pair_list = sorted_alphabet_pair_list[:-1]
        # update alphabet pair hash/ sorted list
        for (k,v) in changed_pairs.items():
            if k in alphabet_pair_hash:
                # get old count/pretoken list, append those
                old_ap = alphabet_pair_hash.pop(k)
                v.count += old_ap.count
                v.pretoken_list += old_ap.pretoken_list
                # remove from sorted list
                sorted_list_loc = find_index(old_ap, sorted_alphabet_pair_list)
                if sorted_list_loc >= len(sorted_alphabet_pair_list):
                    if sorted_alphabet_pair_list[-1] == old_ap:
                        sorted_alphabet_pair_list.pop(-1)
                    else:
                        raise Exception("oi ve")
                else:
                    sorted_alphabet_pair_list.pop(sorted_list_loc)
            # save to hash
            alphabet_pair_hash[k] = v
            # adjust sorted list                
            new_loc = find_index(v, sorted_alphabet_pair_list)
            sorted_alphabet_pair_list.insert(new_loc, v)
    
    # convert to dict
    vocab_dict = {}
    for (i, v) in enumerate(vocab):
        vocab_dict[i] = v
    return (vocab_dict, merges)


def update_alphabet_hash(alphabet_pair_hash, alphabet_pair:tuple[bytes], pretoken:Pretoken):
    if alphabet_pair in alphabet_pair_hash:
        ap = alphabet_pair_hash[alphabet_pair]
    else:
        ap = AlphabetPair(*alphabet_pair)
    ap.count += pretoken.count
    ap.pretoken_list.append(pretoken)
    alphabet_pair_hash[alphabet_pair] = ap
    return

def get_pair_indices(pretoken:Pretoken, pair:tuple[bytes]) -> list[int]:
    inds = []
    pair_bytes = flatten(pair)
    for i in range(1, len(pretoken.alphabet_list)):
        current_pair = pretoken.alphabet_list[i-1] + pretoken.alphabet_list[i]
        if current_pair == pair_bytes:
            inds.append(i-1)    
    return inds

def decrement_old_pairs(changed_pairs, pretoken:Pretoken, inds:list[int]):
    for ind in inds:
        if ind > 0:
            # lower pair
            old_low = (pretoken.alphabet_list[ind-1], pretoken.alphabet_list[ind])
            if old_low not in changed_pairs:
                changed_pairs[old_low] = AlphabetPair(*old_low)
            changed_pairs[old_low].count -= pretoken.count
        if ind + 1 < len(pretoken.alphabet_list) - 1:
            old_high = (pretoken.alphabet_list[ind+1], pretoken.alphabet_list[ind+2])
            if old_high not in changed_pairs:
                changed_pairs[old_high] = AlphabetPair(*old_high)
            changed_pairs[old_high].count -= pretoken.count
    return

def update_alphabet_list(pretoken:Pretoken, pair:tuple[bytes]) -> list[int]:
    # returns locations of new pretoken pairs
    # updates the alphabet list for a prektoken
    locs = []
    ind = 1
    while ind < len(pretoken.alphabet_list):
        current_pair = (pretoken.alphabet_list[ind-1], pretoken.alphabet_list[ind])
        if pair == current_pair:
            pretoken.alphabet_list.pop(ind-1)
            pretoken.alphabet_list.pop(ind-1)
            pretoken.alphabet_list.insert(ind-1, flatten(pair))
            locs.append(ind-1)
        ind += 1
    return locs


def get_new_pairs(pretoken:Pretoken, inds:list[int]):
    if len(pretoken.alphabet_list) <= 1:
        return []
    new_pairs = []
    for ind in inds:
        if ind > 0:
            if pretoken.alphabet_list[ind-1] != pretoken.alphabet_list[ind]:
                # backwards pair
                new_pairs.append((pretoken.alphabet_list[ind-1], pretoken.alphabet_list[ind]))
        if ind < (len(pretoken.alphabet_list) - 1):
            # forwards pair
            new_pairs.append((pretoken.alphabet_list[ind], pretoken.alphabet_list[ind+1]))
    return new_pairs
        
if __name__ == "__main__":
    (vocab, merges) = bpe_less_naive("tests/fixtures/corpus.en", 356, [])
    print(f"merges {merges}")
    with open("merges.txt", "w") as fi:
        for m in merges:
            fi.write(f"{m}\n")



