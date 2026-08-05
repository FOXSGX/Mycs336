import regex as re
import json
import itertools
PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""

def counting(pretokens):
    ans = dict()
    for pretoken in pretokens:
        bts = pretoken.encode("utf-8")
        tokens = tuple(bytes([b]) for b in bts)
        if tokens in ans:
            ans[tokens] += 1
        else:
            ans[tokens] = 1
    return ans
# counting(["hi", "hi", "牛"])
# → {
#     (b"h", b"i"): 2,
#     (b"\xe7", b"\x89", b"\x9b"): 1,
# }


def pair_counting(counts):
    ans = dict()
    for tokens in counts:
        cnt = counts[tokens]
        for i in range(len(tokens)-1):
            new_tokens = (tokens[i],tokens[i+1])
            if new_tokens in ans:
                ans[new_tokens] += cnt
            else:
                ans[new_tokens] = cnt
    return ans
# pair_counting({
#     (b"h", b"i"): 2,
#     (b"a", b"b", b"a"): 3,
# })
# → {
#     (b"h", b"i"): 2,
#     (b"a", b"b"): 3,
#     (b"b", b"a"): 3,
# }


def find_best_pair(pair_counts):
    return max(pair_counts,key = lambda pair:(pair_counts[pair],pair))
# find_best_pair({
#     (b"a", b"b"): 3,
#     (b"b", b"a"): 3,
#     (b"h", b"i"): 2,
# })
# → (b"b", b"a")


def merge(best_pair,counts):
    new_counts = dict()
    for tokens in counts:
        if any(pair == best_pair for pair in itertools.pairwise(tokens)):
            new_tokens = []
            i = 0
            l = len(tokens)
            while i < l - 1:
                if (tokens[i],tokens[i+1]) == best_pair:
                    new_tokens.append(best_pair[0]+best_pair[1])
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            if i == l - 1:
                new_tokens.append(tokens[i])
            tu = tuple(new_tokens)
            if tu in new_counts:
                new_counts[tu] += counts[tokens]
            else:
                new_counts[tu] = counts[tokens]
        else:
            if tokens in new_counts:
                new_counts[tokens] += counts[tokens]
            else:
                new_counts[tokens] = counts[tokens]
    return new_counts
# merge(
#     (b"a", b"b"),
#     {
#         (b"a", b"b", b"a", b"b"): 2,
#         (b"a", b"b", b"c"): 3,
#         (b"b", b"a"): 4,
#         (b"a",): 5,
#     },
# )
# → {
#     (b"ab", b"ab"): 2,
#     (b"ab", b"c"): 3,
#     (b"b", b"a"): 4,
#     (b"a",): 5,
# }


def toy_train_bpe(pretokens, vocab_size):
    sequence_counts = counting(pretokens)
    vocab = {i : bytes([i]) for i in range(256)}
    merges = []

    while len(vocab) < vocab_size:
        pair_counts = pair_counting(sequence_counts)
        if not pair_counts:
            break
        best_pair = find_best_pair(pair_counts)
        merges.append(best_pair)
        vocab[len(vocab)] = best_pair[0]+best_pair[1]
        sequence_counts = merge(best_pair,sequence_counts)

    return vocab, merges
# toy_train_bpe(["abab", "abab", "aba"], 258)
# → vocab[256] == b"ab"
# → vocab[257] == b"abab"
# → merges == [(b"a", b"b"), (b"ab", b"ab")]


def break_up(text,special_tokens):
    if special_tokens:
        ordered_special_tokens = sorted(special_tokens,key = len,reverse=True)
        escaped_tokens = [re.escape(token) for token in ordered_special_tokens]
        pattern = "|".join(escaped_tokens)
        return list(filter(lambda x:x != "",re.split(pattern, text)))
    return [] if text =="" else [text]
# break_up(
#     "hello<|endoftext|>world<|endoftext|>!",
#     ["<|endoftext|>"],
# )
# → ["hello", "world", "!"]


def get_pretokens(text, special_tokens):
    segments = break_up(text, special_tokens)
    result = []

    for segment in segments:
        for item in  re.finditer(PAT, segment):
            result.append(item.group())
    return result
# get_pretokens(
#     "Hello<|endoftext|> world!",
#     ["<|endoftext|>"],
# )
# → ["Hello", " world", "!"]


def train_bpe(input_path,vocab_size,special_tokens):
    with open(input_path, "r", encoding="utf-8") as file:
        text = file.read()
    pretokens = get_pretokens(text,special_tokens)
    sequence_counts = counting(pretokens)
    vocab = {i : bytes([i]) for i in range(256)}
    for special_token in special_tokens:
        vocab[len(vocab)] = special_token.encode("utf-8")
    merges = []

    while len(vocab) < vocab_size:
        pair_counts = pair_counting(sequence_counts)
        if not pair_counts:
            break
        best_pair = find_best_pair(pair_counts)
        merges.append(best_pair)
        vocab[len(vocab)] = best_pair[0]+best_pair[1]
        sequence_counts = merge(best_pair,sequence_counts)

    return vocab, merges


def save_tokenizer(vocab,merges,vocab_filepath,merges_filepath):
    json_vocab = {
    str(token_id): token_bytes.hex()
    for token_id, token_bytes in vocab.items()
    }
    json_merges = [
    [left.hex(), right.hex()]
    for left, right in merges
    ]
    with open(vocab_filepath, "w", encoding="utf-8") as file:
        json.dump(json_vocab, file, indent=2)
    with open(merges_filepath,"w",encoding="utf-8") as file:
        json.dump(json_merges,file,indent=2)