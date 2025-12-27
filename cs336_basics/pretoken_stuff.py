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


# def split_on_special_tokens(str_value, special_tokens:list[str]) -> list[str]:
#     str_list = []
#     while True:
#         locs = [str_value.find(st) for st in special_tokens]
#         actual_locs = [loc for loc in locs if loc >= 0]
#         actual_loc_sts = [st for (st,loc) in zip(special_tokens, locs) if loc >= 0]
#         if actual_locs == []:
#             str_list.append(str_value)
#             break
#         else:
#             first_match = min(actual_locs)
#             first_match_st = actual_loc_sts[actual_locs.index(first_match)]
#             splits = str_value.split(first_match_st, 1)
#             str_list.append(splits[0])
#             str_value = splits[1]
#     return str_list

def split_on_special_tokens(str_value, special_tokens:list[str]) -> list[str]:
    split_pattern = "|".join(re.escape(token) for token in special_tokens)
    return re.split(split_pattern, str_value)

def child_process(args):
    """
    A little unncessary but basically a caller for get_chunk_pretoken_counts 
    for each of the child processes
    """
    bounds, input_path, special_tokens = args
    return get_chunk_pretoken_counts(input_path, bounds, special_tokens)

def get_chunk_pretoken_counts(input_path:str, bounds:list[int], special_tokens:list[str]) -> tuple[list[str], list[int]]:
    """
    Returns a tuple of lists, the first is pretokens (sorted alphabetically) the second is the counts corresponding to
    those pretokens
    """
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


def get_chunk_pretoken_counts(input_path:str, bounds:list[int], special_tokens:list[str]) -> dict[str,int]:
    """
    Returns a tuple of lists, the first is pretokens (sorted alphabetically) the second is the counts corresponding to
    those pretokens
    """
    pretoken_counts = {}
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
                if pretoken in pretoken_counts:
                    pretoken_counts[pretoken] += 1
                else:
                    pretoken_counts[pretoken] = 1
    return pretoken_counts

# def get_chunk_pretoken_counts(input_path:str, bounds:list[int], special_tokens:list[str]) -> tuple[list[str], list[int]]:
#     """
#     Returns a tuple of lists, the first is pretokens (sorted alphabetically) the second is the counts corresponding to
#     those pretokens
#     """
#     pretokens = []
#     pretoken_counts = []
#     for i in range(1, len(bounds)):
#         lowbound = bounds[i-1]
#         upbound = bounds[i]
#         with open(input_path,"rb") as f:
#             f.seek(lowbound)
#             chunk = f.read(upbound - lowbound).decode("utf-8", errors="ignore")
#         input_splits = split_on_special_tokens(chunk, special_tokens)
#         PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
#         for input_split in input_splits:
#             pretoken_re = re.finditer(PAT, input_split)
#             for pretoken_match in pretoken_re:
#                 pretoken = pretoken_match.group()
#                 # find index in our pretoken list 
#                 ind = find_index(pretoken, pretokens)
#                 if len(pretokens) == 0 or ind >= len(pretokens):
#                     pretokens.insert(ind, pretoken)
#                     pretoken_counts.insert(ind, 0)
#                 elif pretokens[ind] != pretoken:
#                     pretokens.insert(ind, pretoken)
#                     pretoken_counts.insert(ind, 0)
#                 pretoken_counts[ind] += 1
#     return (pretokens, pretoken_counts)

def merge_results(pretoken_list:list[Pretoken], child_process_results) -> list[Pretoken]:
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

def split_bounds(bounds, num_processes) -> list[list[int]]:
    """
    Splits up bounds so we don't have to read in whole subsets of the file at once
    """
    bound_splits = []
    size = (len(bounds)-1) // num_processes
    i = 1
    while (i-1) * size < len(bounds)-1:
        bound_splits.append(bounds[(i-1)*size:(i*size+1)])
        i+=1
    return bound_splits


def get_pretoken_list(input_path, special_tokens, num_processes:int, num_corpus_splits:int) -> list[Pretoken]:    
    # get's the boundaries
    with open(input_path, "rb") as f:
        boundaries = find_chunk_boundaries(f, num_corpus_splits, b"<|endoftext|>")
    bounds_groups = split_bounds(boundaries, num_processes)
    # given boundaries, spawn children 
    args_list = [(bound_group, input_path, special_tokens) for bound_group in bounds_groups]
    with mp.Pool(min(4,num_processes)) as p:
        results = p.map(child_process, args_list)
    
    pretoken_dict = {}
    for res in results:
        for (k,v) in res.items():
            pretoke = pretoken_dict.get(k, Pretoken(k))
            pretoke.count += v
            pretoken_dict[k] = pretoke
    return pretoken_dict

    # # cool now for each of our results, add to a final list
    # return functools.reduce(merge_results,results, [])




