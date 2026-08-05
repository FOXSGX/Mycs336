import regex as re
import json
PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""

def merge_one_pair(tokens, pair):
    new_tokens = []
    i = 0
    while i < len(tokens) - 1:
        if (tokens[i],tokens[i+1]) == pair:
            new_tokens.append(pair[0]+pair[1])
            i += 2
        else:
            new_tokens.append(tokens[i])
            i += 1
    if i == len(tokens) - 1:
        new_tokens.append(tokens[i])
    return new_tokens
#辅助函数：merge单个token序列
def apply_bpe_merges(tokens, merges):
    for pair in merges:
        tokens = merge_one_pair(tokens,pair)
    return tokens
#辅助函数：遍历tokens并merge
def special_token_suffix(text, special_tokens):
    complete_matches = [
        st
        for st in special_tokens
        if text.endswith(st)
    ]
    if complete_matches:
        longest_complete = max(complete_matches, key=len)
        can_grow = any(
            st.startswith(longest_complete) and st != longest_complete
            for st in special_tokens
        )
        if can_grow:
            cut = len(text) - len(longest_complete)
            return text[:cut], text[cut:]
        return (text, "")
    for i in range(len(text)):
        suffix = text[i:]
        for st in special_tokens:
            if st.startswith(suffix) and st != suffix and suffix:
                return (text[:i],suffix)
    return (text,"")
#辅助函数：检查并切除最长special_token真前缀
def split_last_pretoken(text):
    last_start = None
    for match in re.finditer(PAT,text):
        last_start = match.start()
    if last_start is not None:
        return (text[:last_start],text[last_start:])
    return ("",text)
#辅助函数：检查并切除普通文本的最后一个match




class Tokenizer:
    def __init__(self,vocab,merges,special_tokens):
        self.vocab = vocab
        self.merges = merges
        self.special_tokens = special_tokens or []
        self.bytes_to_id = dict()
        for key in vocab:
            self.bytes_to_id[vocab[key]] = key

    def decode(self,ids):
        return b"".join(self.vocab[id] for id in ids).decode("utf-8",errors="replace")

    def encode(self,text):
        ids = []
        if self.special_tokens:
            ordered_special_tokens = sorted(self.special_tokens,key=len,reverse=True,)
            escaped_tokens = [re.escape(token) for token in ordered_special_tokens]
            pattern = "|".join(escaped_tokens)
            chunks = re.split(f"({pattern})", text)
        else:
            chunks = [text]
        for chunk in chunks:
            if not chunk:
                continue
            if chunk in self.special_tokens:
                ids.append(self.bytes_to_id[chunk.encode("utf-8")])
            else:
                for item in re.finditer(PAT, chunk):
                    pretoken = item.group()
                    tokens = [bytes([b]) for b in pretoken.encode("utf-8")]
                    tokens = apply_bpe_merges(tokens, self.merges)
                    ids.extend(self.bytes_to_id[token] for token in tokens)
        return ids

    def encode_iterable(self, iterable):
        buffer = ""
        for chunk in iterable:
            candidate = buffer + chunk
            candidate,suffix = special_token_suffix(candidate,self.special_tokens)
            if self.special_tokens:
                ordered_special_tokens = sorted(self.special_tokens,key=len,reverse=True,)
                escaped_tokens = [re.escape(token) for token in ordered_special_tokens]
                pattern = "|".join(escaped_tokens)
                parts = re.split(f"({pattern})", candidate)
                ordinary_tail = parts[-1]
                candidate = "".join(parts[:-1])
            else:
                ordinary_tail = candidate
                candidate = ""
            safe_tail,buffer = split_last_pretoken(ordinary_tail)
            candidate += safe_tail
            buffer += suffix
            ids = self.encode(candidate)
            yield from ids
        ids = self.encode(buffer)
        yield from ids

    @classmethod
    def from_files(cls, vocab_filepath, merges_filepath, special_tokens=None):
        with open(vocab_filepath,"r",encoding="utf-8") as file:
            json_vocab = json.load(file)
        with open(merges_filepath,"r",encoding="utf-8") as file:
                    json_merges = json.load(file)
        vocab = {
            int(token_id):bytes.fromhex(token_bytes)
            for token_id,token_bytes in json_vocab.items()
        }
        merges = [
            (bytes.fromhex(left),bytes.fromhex(right))
            for left,right in json_merges
        ]
        return cls(vocab,merges,special_tokens)
