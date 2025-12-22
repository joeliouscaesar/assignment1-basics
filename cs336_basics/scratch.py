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



