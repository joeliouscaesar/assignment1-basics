from cs336_basics.scratch_bpe import bpe_less_naive
import pickle

suffix = "run1x1"
data_path = "data/TinyStoriesV2-GPT4-valid.txt"
vocab, merges = bpe_less_naive(data_path, 1000, ["<|endoftext|>"], num_processes=1, num_corpus_splits = 1)

with open(f"merges_{suffix}","wb") as fi:
    pickle.dump(merges, fi)



# import pickle
# import pstats
# p = pstats.Stats("valid_cprof_run1x1")
# stats = p.strip_dirs().sort_stats("cumulative")
# stats.print_stats(10)

# p = pstats.Stats("valid_cprof_run4x4")
# stats = p.strip_dirs().sort_stats("cumulative")
# stats.print_stats(10)

# p = pstats.Stats("valid_cprof_run4x16")
# stats = p.strip_dirs().sort_stats("cumulative")
# stats.print_stats(10)

# with open("merges_run1x1", "rb") as fi:
#     merges_1x1 = pickle.load(fi)

# with open("merges_run4x4", "rb") as fi:
#     merges_4x4 = pickle.load(fi)

# with open("merges_run4x16", "rb") as fi:
#     merges_4x16 = pickle.load(fi)

# len(merges_4x4)
# len(merges_4x16)
# assert merges_4x4 == merges_4x16

# p1 = pstats.Stats("valid_cprof_mp2")
# stats1 = p1.strip_dirs().sort_stats("cumulative")

# old_p = pstats.Stats("valid_cprof")
# old_p.strip_dirs().sort_stats("cumulative").print_stats(10)

