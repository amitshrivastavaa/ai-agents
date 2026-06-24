# bpe — a byte-level tokenizer from scratch

> The first thing every LLM does to your text: chop it into tokens. This builds
> the GPT-style **Byte-Pair Encoding** tokenizer from first principles — start
> from raw bytes, repeatedly merge the most frequent adjacent pair into a new
> token, and watch common chunks (`' the'`, `'ing'`, `' agent'`) become single
> tokens so text compresses.

Because it works on **bytes**, `decode(encode(x)) == x` for *any* input — emoji
included. Fully offline, deterministic, no dependencies. (Homage to Karpathy's
minbpe; pairs with [`micrograd`](../micrograd/) as the "LLM from scratch"
foundations.)

## Quick start

```sh
python -m labs.bpe.demo
python -m labs.bpe.cli encode "An agent plans ahead and learns."
python -m labs.bpe.cli merges --vocab 400
python -m labs.bpe.cli compare
```

```
Tokenizing: 'An intelligent agent plans ahead and learns from memory.'
  A|n| |int|e|l|li|g|ent| agent| p|lan|s| a|h|e|a|d| and| le|ar|n|s| from| m|emor|y|.
  56 bytes → 28 tokens (2.00× compression)
```

## How it works

**Train.** Encode the corpus as UTF-8 bytes — 256 base tokens. Then repeatedly:
count every adjacent pair, mint a new token id for the **most frequent** one,
and replace it everywhere. Each merge is recorded. The vocabulary grows from 256
toward your target, one learned subword at a time.

**Encode.** Re-bytes the text, then replays the merges in the order they were
learned (earliest merge first) until none apply.

**Decode.** Concatenate each token's bytes and UTF-8-decode. Since every token
is ultimately a byte string, decoding is exact for any input.

## What it learns

The first merges on an English corpus are exactly the chunks you'd guess —
`'s '`, `' t'`, `'e '`, `'in'`, `'en'`, `' a'`, `' th'`, `'ent'` — and longer
ones (`' agent'`, `' and'`, `'tion'`) appear as the vocabulary grows. More
merges means more text collapses into single tokens:

| vocab | merges | compression (corpus) |
| ---: | ---: | ---: |
| 256 | 0 | 1.00× (raw bytes) |
| 300 | 44 | 1.54× |
| 400 | 144 | 2.17× |
| 512 | 256 | 2.35× |

## Round-trips, guaranteed

```python
from labs.bpe import BPETokenizer, CORPUS
tok = BPETokenizer().train(CORPUS, vocab_size=400)
tok.decode(tok.encode("café — déjà vu 🤖")) == "café — déjà vu 🤖"   # True
```

## Tests

```sh
python -m unittest labs.bpe.tests.test_bpe -v
```
