from scratch_bpe import bpe_less_naive

FIXTURES_PATH = "../tests/fixtures/"
input_path = FIXTURES_PATH + "tinystories_sample_5M.txt"
vocab, merges = bpe_less_naive(
    input_path=input_path,
    vocab_size=1000,
    special_tokens=["<|endoftext|>"],
)

words = [w for w in vocab.values() if w != b"<|endoftext|>"]


b'<|' in words

offenders = [w for w in words if b'<|' in w]

import regex as re
PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
re.split(r"""'(?:boy|loves)""", "I'm just a poor boy nobody loves me")


import regex as re
import os
# chr(0)
# print(chr(0))
# ord('0')

# test_string = "🏡"

# utf8_encoded = test_string.encode("utf-8")

# byte_list = list(utf8_encoded)

# # pre-tokenize
# def decode_utf8_bytes_to_str_wrong(bytestring: bytes):
#     return "".join([bytes([b]).decode("utf-8") for b in bytestring])


# test_string[:2]
# decode_utf8_bytes_to_str_wrong(utf8_encoded)
# utf8_encoded.decode()

# house_bytes = utf8_encoded[:2]
# house_bytes.decode()

# x = 'a'.encode()



###########################################################################

def bpe_naive(
    # input_path: str | os.PathLike,
    input: str,
    vocab_size: int
    # special_tokens: list[str],
    # **kwargs,
):
    # Pretokenize 
    PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
    pretokens = re.findall(PAT, input)
    # Initialize Vocabulary
    vocab = [(x,) for x in range(256)]
    # While vocab is small enough
    while len(vocab) < vocab_size:
        # encode the pretokens
        encoded_pretokens = [tuple(pretoken.encode()) for pretoken in pretokens]
        pair_counts = {}
        for pretoken in encoded_pretokens:
            vocablist = bytelist_to_vocablist(pretoken, vocab)
            vocabpairs = vocablist_to_vocabpairs(vocablist)
            for vocabpair in vocabpairs:
                pair_counts[tuple(vocabpair)] = pair_counts.get(tuple(vocabpair), 0) + 1
        most_common_pair = get_most_common_pair(pair_counts)
        vocab.append(most_common_pair)
    # convert to dict
    vocab_dict = {}
    for (i, v) in enumerate(vocab):
        vocab_dict[i] = v
    merges = vocab[256:]
    return (vocab_dict, merges)

# (vocab, merges) = bpe_naive(input, 262)

# clean_merges = []
# for m in merges:
#     cleaned = [chr(b) for b in m]
#     clean_merges.append(tuple(cleaned))

# pretokenizer
def get_word(bytelist, vocab):
    """
    Get's word for this set of bytes
    """
    longest_match = 0
    match = None
    for v in vocab:
        if v == bytelist[:len(v)] and len(v) > longest_match:
            longest_match = len(v)
            match = v
    return match

def bytelist_to_vocablist(bytelist, vocab):
    """
    Get's list of vocab words corresponding to our byte list
    """
    vocablist = []
    i = 0
    while i < len(bytelist):
        word = get_word(bytelist[i:], vocab)
        vocablist.append(word)
        i += len(word)
    return vocablist

def vocablist_to_vocabpairs(vocablist):
    vocabpairs = []
    for i in range(1, len(vocablist)):
        vocabpairs.append(vocablist[i-1]+vocablist[i])
    return vocabpairs

def get_most_common_pair(pair_counts):
    maxcount = 0
    for (pair, count) in pair_counts.items():
        if count > maxcount:
            maxpair = pair
            maxcount = count
        elif count == maxcount and pair > maxpair:
            maxpair = pair
            maxcount = count
    return maxpair

# okay 
# input = "cat catas"
# ca 2
# at 2
# ta 1
# as 1

# first one is word, second one is position
# ca (0,0), (1,0) : 2
# at (0, 1), (1,1) : 2
# ta (1,2) : 1
# as (1,3) : 1

# first round we see ca is the most common
# go to word 0, spot 1, add (ca, t) to index because it's (a,t), remove the (a,t) pair
# next go to word (1, 0), same deal

# (ca, t) (0,0), (1,0) : 2
# (t,a) (1,2) : 1
# (a,s) (1,3) : 1

# (cat, a) (1, 0) : 1
# (a, s) (1, 3) : 1

# I think we want organized so that the 






# alphabet pairs
# pretokens

# hash of alphabet pairs, I think the size of this will be relatively flat
# this will store the counts, we'll do a linear scan
# I think the size of this is bounded by size of alphabet**2

# pretokens, can be any number of these really
# think we want a sorted list of these for quick lookups

ex = bytes("cats", "utf-8")
ex1 = bytes("dogs", "utf-8")

import functools
def flatten(x:tuple[bytes]) -> bytes:
    return functools.reduce(lambda a,b: a+b,x)


example = bytes("cats are dogs","utf-8")
poop = [example[i:i+1] for i in range(len(example))]

class Pretoken:
    """
    Class for a single pretoken

    Attributes
    - count:int number of times its in the corpus
    - alphabet_list:list[bytes] is a list of bytes representing words in our alphabet
    """
    def __init__(self, pretoken:str):
        self.count = 0
        pretoken_bytes = bytes(pretoken, "utf-8")
        self.alphabet_list = [pretoken_bytes[i:i+1] for i in range(len(pretoken_bytes))] # initialized assuming bytes are alphabet
        return


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
            return flatten(self.pair) <  flatten(otherpair.pair)
        else:
            return False
    def __gt__(self, otherpair):
        if otherpair is None:
            return True
        return otherpair < self

# 1. split inputs into list of pretokens
# 2. for each pretoken in list, initialize Pretoken and maintain count. maybe store hash for easy counting?
# 3. for each unique pretoken in our pretoken hash, construct new hash with the alphabet pair counts and list of pretokens
# 4. loop over alphabet pairs, with max alphabet pair
#   a. add max pair to alphabet as bytes object
#   b. for each Pretoken in the max pair pretoken_list, modify the alphabet_list and pair counts for that max pair (first occurrence)
#   c. remove max pair from the pairs hash
# 5. Loop 4 until we reach alphabet size


def bpe_less_naive(
    input_path: str | os.PathLike,
    # input: str,
    vocab_size: int,
    special_tokens: list[str],
    **kwargs
):
    # Initialize Vocabulary
    vocab = [i.to_bytes() for i in range(256)]
    vocab += [bytes(st,"utf-8") for st in special_tokens]
    merges = []
    # Pretokenize 
    PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
    with open(input_path, "rb") as fi:
        input = fi.read().decode("utf-8")
    pretoken_re = re.finditer(PAT, input)
    # hash of pretokens
    pretoken_hash = {}
    for pretoken_match in pretoken_re:
        pretoken = pretoken_match.group()
        pretoken_obj = pretoken_hash.get(pretoken, Pretoken(pretoken))
        pretoken_obj.count += 1
        pretoken_hash[pretoken] = pretoken_obj

    # initialize our alphabet pair hash
    alphabet_pair_hash = {}
    for pretoken in pretoken_hash.values():
        for i in range(1, len(pretoken.alphabet_list)):
            pair = (pretoken.alphabet_list[i-1], pretoken.alphabet_list[i])
            # get alphabet pairs, add to alphabet pair hash
            update_alphabet_hash(alphabet_pair_hash, pair, pretoken)
    
    # While vocab is small enough
    while len(vocab) < vocab_size:
        # get max alphabet pair
        maxkey = None
        maxpair = None
        for (key, pair) in alphabet_pair_hash.items():
            if pair > maxpair:
                maxpair = pair
                maxkey = key
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
    input = """abababa cdcd"""
    with open("temp.txt","w") as fi:
        fi.write(input)
    (vocab, merges) = bpe_less_naive("temp.txt", 259, [])
    print(f"merges {merges}")

