import regex as re
import os

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
