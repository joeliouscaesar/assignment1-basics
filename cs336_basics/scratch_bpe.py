import regex as re
import os
import functools

def flatten(x:tuple[bytes]) -> bytes:
    return functools.reduce(lambda a,b: a+b,x)

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
            return self.pair < otherpair.pair
            # return flatten(self.pair) <  flatten(otherpair.pair)
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
    with open(input_path, "r") as fi:
        input = fi.read()
    # replace special tokens
    for st in special_tokens:
        input.replace(st, "")
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

def split_on_special_tokens(str_value, special_tokens:list[str]):
    str_list = []
    while True:
        locs = [str_value.find(st) for st in special_tokens]
        actual_locs = [loc for loc in locs if loc >= 0]
        actual_loc_sts = [st for (st,loc) in zip(special_tokens, locs) if loc >= 0]
        if actual_locs == []:
            str_list.append(str_value)
            break
        else:
            first_match = min(actual_locs)
            first_match_st = actual_loc_sts[actual_locs.index(first_match)]
            splits = str_value.split(first_match_st, 1)
            str_list.append(splits[0])
            str_value = splits[1]
    return str_list


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


# from common import FIXTURES_PATH, gpt2_bytes_to_unicode
# # Compare the learned merges to the expected output merges
# gpt2_byte_decoder = {v: k for k, v in gpt2_bytes_to_unicode().items()}

# reference_merges_path = "./fixtures/train-bpe-reference-merges.txt"
# with open(reference_merges_path, encoding="utf-8") as f:
#     gpt2_reference_merges = [tuple(line.rstrip().split(" ")) for line in f]
#     reference_merges = [
#         (
#             bytes([gpt2_byte_decoder[token] for token in merge_token_1]),
#             bytes([gpt2_byte_decoder[token] for token in merge_token_2]),
#         )
#         for merge_token_1, merge_token_2 in gpt2_reference_merges
#     ]

# with open("../ref_merges.txt","w") as fi:
#     for rm in reference_merges:
#         fi.write(f"{rm}\n")


# # seems like pretokenization is fine 
# PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
# with open("./tests/fixtures/corpus.en","rb") as fi:
#     x = fi.read()
# words = re.findall(PAT, x.decode())


# with open("./tests/fixtures/corpus.en","r") as fi:
#     x1 = fi.read()

# words1 = re.findall(PAT, x1)
# words == words1

# pretoken_re = re.finditer(PAT, x1)
# # words2 = [i.group() for i in pretoken_re]


# # hash of pretokens
# pretoken_hash = {}
# for pretoken_match in pretoken_re:
#     pretoken = pretoken_match.group()
#     pretoken_obj = pretoken_hash.get(pretoken, Pretoken(pretoken))
#     pretoken_obj.count += 1
#     pretoken_hash[pretoken] = pretoken_obj

# len(pretoken_hash)
# # looks like we counted properly
# functools.reduce(lambda a,b: a + b.count, pretoken_hash.values(), 0) == len(words)
# # assert that alphabet list is good
# for (pt, al) in pretoken_hash.items():
#     print(f"pt {pt}")
#     assert pt == flatten(al.alphabet_list).decode("utf-8")
# # this looks good too
# for pt in pretoken_hash.values():
#     al = pt.alphabet_list
#     for a in al:
#         assert len(a) == 1


# # initialize our alphabet pair hash
# alphabet_pair_hash = {}
# for pretoken in pretoken_hash.values():
#     for i in range(1, len(pretoken.alphabet_list)):
#         pair = (pretoken.alphabet_list[i-1], pretoken.alphabet_list[i])
#         # get alphabet pairs, add to alphabet pair hash
#         update_alphabet_hash(alphabet_pair_hash, pair, pretoken)



# # (ap, ap_obj) = alphabet_pair_hash.items().__iter__().__next__()
# # len(ap_obj.pretoken_list)

# # so far looks good

# # cool 
# for (ap, ap_obj) in alphabet_pair_hash.items():
#     for pretoke in ap_obj.pretoken_list:
#         assert flatten(ap) in flatten(pretoke.alphabet_list)


# counts = [pair.count for pair in alphabet_pair_hash.values()]
# counts.sort()

# for pretoke in maxpair.pretoken_list:
#     print(flatten(pretoke.alphabet_list))
    
# maxpair = max(alphabet_pair_hash.values())

# # functools.reduce(lambda a,b: a+b.count, maxpair.pretoken_list, 0)
# old_al_lengths = [len(pretoke.alphabet_list) for pretoke in maxpair.pretoken_list]
# old_flat_lens = [len(flatten(pretoke.alphabet_list)) for pretoke in maxpair.pretoken_list]
# assert old_al_lengths == old_flat_lens


# # add to vocab/merges 
# flatmaxpair = flatten(maxpair.pair)
# vocab.append(flatmaxpair)
# merges.append(maxpair.pair)
# # iterate over pretokens this pair is in
# for pretoken in maxpair.pretoken_list:
#     # get current indices and decrement old surrounding pair counts
#     inds = get_pair_indices(pretoken, maxpair.pair)
#     decrement_old_pairs(alphabet_pair_hash, pretoken, inds)
#     # update this pretoken's alphabet list
#     inds = update_alphabet_list(pretoken, maxpair.pair)
#     # get updated alphabet pairs from this change
#     new_pairs = get_new_pairs(pretoken, inds)
#     for pair in new_pairs:
#         # update alphabet_pair_hash
#         update_alphabet_hash(alphabet_pair_hash, pair, pretoken)
# # remove old pair
# alphabet_pair_hash.pop(maxpair.pair)

# new_al_lengths = [len(pretoke.alphabet_list) for pretoke in maxpair.pretoken_list]
# old_al_lengths == new_al_lengths


# whelp = {}
# for (k, v) in alphabet_pair_hash.items():
#     if len(flatten(k)) > 2:
#         whelp[k] = v

# for (k,v) in alphabet_pair_hash.items():

#     assert 

# pretoke = maxpair.pretoken_list[0]