from cs336_basics.scratch_bpe import bpe_less_naive

data_path = "data/TinyStoriesV2-GPT4-valid.txt"
vocab, merges = bpe_less_naive(data_path, 1000, ["<|endoftext|>"], num_processes=4)

# with open(data_path,"rb") as f:
#     boundaries = find_chunk_boundaries(f,2,b"<|endoftext|>")

# with open(data_path,"rb") as f:
#     input = f.read()

# input = input[:100000]
# input_splits = split_on_special_tokens(input, special_tokens)




# def binary_search(x,xs:list) -> int:
#     if len(xs) == 0:
#         return 0
#     low = 0
#     high = len(xs)
#     if xs[low] >= x:
#         return low
#     elif xs[high-1] <= x:
#         return high
#     # so we know that strictly xs[low] < x < xs[high]
#     mid = (high - low) // 2
#     while (high - low) > 1:
#         if xs[mid] == x:
#             return mid
#         elif x < xs[mid]:
#             high = mid
#         elif x > xs[mid]:
#             low = mid
#         mid = (high - low) // 2
#     return high

# # # Pretokenize 
# PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
# with open(data_path, "r") as fi:
#     input = fi.read()



# # just keeping track of pretoken counts
# def get_pretoken_counts()

# xs = [1,2,3,4,5]
# binary_search(6,xs)
# xs = [1,3,4,5]
# binary_search(2,xs)
# xs = [1,3,4,5]
# binary_search(-1,xs)
# xs = [1,3,4,5]
# binary_search(4,xs)
# xs = [1,3,4,5]
# binary_search(5,xs)
# xs = []
# binary_search(5,xs)



# import pstats
# p = pstats.Stats("valic_cprof_mp")
# stats = p.strip_dirs().sort_stats("cumulative")

# old_p = pstats.Stats("valid_cprof")
# old_p.strip_dirs().sort_stats("cumulative").print_stats(10)


