import multiprocessing as mp
import regex as re
from cs336_basics.pretokenization_example import find_chunk_boundaries
import functools

class Pretoken:
    """
    Class for a single pretoken

    Attributes
    - count:int number of times its in the corpus
    - alphabet_list:list[bytes] is a list of bytes representing words in our alphabet
    """
    def __init__(self, pretoken:str):
        self.count = 0
        self.pretoken = pretoken
        pretoken_bytes = bytes(pretoken, "utf-8")
        self.alphabet_list = [pretoken_bytes[i:i+1] for i in range(len(pretoken_bytes))] # initialized assuming bytes are alphabet
        return


# okay so we're going to maintain sorted lists of pretokens we find for each chunk, return these
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


def child_process(args):
    bounds, input_path, special_tokens = args
    return get_chunk_pretoken_counts(input_path, bounds, special_tokens)

def get_chunk_pretoken_counts(input_path:str, bounds:list[int], special_tokens:list[str]):
    pretokens = []
    pretoken_counts = []
    for i in range(1, len(bounds)):
        lowbound = bounds[i-1]
        upbound = bounds[i]
        with open(input_path,"rb") as f:
            f.seek(lowbound)
            chunk = f.read(upbound - lowbound).decode("utf-8", errors="ignore")
        input_splits = split_on_special_tokens(chunk, special_tokens)
        PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
        for input_split in input_splits:
            pretoken_re = re.finditer(PAT, input_split)
            for pretoken_match in pretoken_re:
                pretoken = pretoken_match.group()
                # find index in our pretoken list 
                ind = find_index(pretoken, pretokens)
                if len(pretokens) == 0 or ind >= len(pretokens):
                    pretokens.insert(ind, pretoken)
                    pretoken_counts.insert(ind, 0)
                elif pretokens[ind] != pretoken:
                    pretokens.insert(ind, pretoken)
                    pretoken_counts.insert(ind, 0)
                pretoken_counts[ind] += 1
    return (pretokens, pretoken_counts)

def merge_results(pretoken_list:list[Pretoken], child_process_results):
    """
    Takes results from the child processes and makes one list
    Linear scan through each
    """
    result_ind = 0
    p_ind = 0
    pretokens, pretoken_counts = child_process_results
    while result_ind < len(pretokens):
        result_pretoken = pretokens[result_ind]
        result_count = pretoken_counts[result_ind]
        if p_ind >= len(pretoken_list):
            # case where we reached the end of the list
            pretoken_list.append(Pretoken(result_pretoken))
            pretoken_list[-1].count += result_count
            p_ind += 1
            result_ind += 1
        elif pretoken_list[p_ind].pretoken < result_pretoken:
            # go to next element of pretoken list
            p_ind += 1
        elif pretoken_list[p_ind].pretoken == result_pretoken:
            # increment count
            pretoken_list[p_ind].count += result_count
            p_ind += 1
            result_ind += 1            
        elif pretoken_list[p_ind].pretoken > result_pretoken:
            # insert new element
            new_pretoke = Pretoken(result_pretoken)
            new_pretoke.count += result_count
            pretoken_list.insert(p_ind, new_pretoke)
            p_ind += 1
            result_ind += 1
    return pretoken_list    

# w1 = ["bats","cats","dogs"]
# c1 = [1,3,2]
# w2 = ["africa","cats","dogs","rain"]
# c2 = [1,1,7,5]

# results = [(w1,c1), (w2,c2)]
# test = 
# for t in test:
#     print(f"{t.pretoken} {t.count}")

def get_pretoken_list(input_path, special_tokens, num_processes:int, num_corpus_splits:int):
    # get's the boundaries
    with open(input_path, "rb") as f:
        boundaries = find_chunk_boundaries(f, num_corpus_splits, b"<|endoftext|>")
    bounds_groups = split_bounds(boundaries, num_processes)
    # given boundaries, spawn children 
    args_list = [(bound_group, input_path, special_tokens) for bound_group in bounds_groups]
    with mp.Pool(min(4,num_processes)) as p:
        results = p.map(child_process, args_list)
    # cool now for each of our results, add to a final list
    return functools.reduce(merge_results,results, [])



# split_bounds(x, 4)


# x = list(range(17))
# processes = 4

# with mp.Pool(3) as p:
#     print(p.map(f, [(1,2), (2,2), (3,4)]))

# num_corpus_splits = 16
# with open("data/TinyStoriesV2-GPT4-valid.txt", "rb") as f:
#     boundaries = find_chunk_boundaries(f, num_corpus_splits, b"<|endoftext|>")

def split_bounds(bounds, num_processes):
    bound_splits = []
    size = (len(bounds)-1) // num_processes
    i = 1
    while (i-1) * size < len(bounds)-1:
        bound_splits.append(bounds[(i-1)*size:(i*size+1)])
        i+=1
    return bound_splits

# split_bounds(boundaries, 1)


    # # The following is a serial implementation, but you can parallelize this
    # # by sending each start/end pair to a set of processes.


