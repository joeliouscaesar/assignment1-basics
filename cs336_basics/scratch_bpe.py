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
    pretokens = get_pretoken_list(input_path, special_tokens, num_processes, num_corpus_splits)

    # initialize our alphabet pair hash
    alphabet_pair_hash = {}
    for pretoken in pretokens:
        for i in range(1, len(pretoken.alphabet_list)):
            pair = (pretoken.alphabet_list[i-1], pretoken.alphabet_list[i])
            # get alphabet pairs, add to alphabet pair hash
            update_alphabet_hash(alphabet_pair_hash, pair, pretoken)
    
    # While vocab is small enough
    while len(vocab) < vocab_size:
        # get max alphabet pair
        maxpair = max(alphabet_pair_hash.values())
        if maxpair is None:
            raise Exception("maxpair is none")
        # add to vocab/merges 
        flatmaxpair = flatten(maxpair.pair)
        vocab.append(flatmaxpair)
        merges.append(maxpair.pair)
        # iterate over pretokens this pair is in
        for pretoken in maxpair.pretoken_list:
            # get current indices and decrement old surrounding pair counts
            inds = get_pair_indices(pretoken, maxpair.pair)
            decrement_old_pairs(alphabet_pair_hash, pretoken, inds)
            # update this pretoken's alphabet list
            inds = update_alphabet_list(pretoken, maxpair.pair)
            # get updated alphabet pairs from this change
            new_pairs = get_new_pairs(pretoken, inds)
            for pair in new_pairs:
                # update alphabet_pair_hash
                update_alphabet_hash(alphabet_pair_hash, pair, pretoken)
        # remove old pair
        alphabet_pair_hash.pop(maxpair.pair)

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

def decrement_old_pairs(alphabet_pair_hash, pretoken:Pretoken, inds:list[int]):
    for ind in inds:
        if ind > 0:
            # lower pair
            old_low = (pretoken.alphabet_list[ind-1], pretoken.alphabet_list[ind])
            alphabet_pair_hash[old_low].count -= pretoken.count
            # if alphabet_pair_hash[old_low].count == 0:
                # alphabet_pair_hash.pop(old_low)
        if ind + 1 < len(pretoken.alphabet_list) - 1:
            old_high = (pretoken.alphabet_list[ind+1], pretoken.alphabet_list[ind+2])
            alphabet_pair_hash[old_high].count -= pretoken.count
            # if alphabet_pair_hash[old_high].count == 0:
                # alphabet_pair_hash.pop(old_high)
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



