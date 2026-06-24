# rag — retrieval-augmented generation from scratch

> Ground answers in your own documents: index a knowledge base, retrieve the
> passages most relevant to a question, and answer **only** from what was
> retrieved — with a citation, and an honest "I don't know" when nothing
> relevant turns up.

The dominant production-AI pattern, built end to end with **no dependencies**: a
TF-IDF index from first principles, top-k retrieval, an extractive grounded
answer, and abstention below a relevance threshold (the anti-hallucination
guarantee). Deterministic; a real model synthesizes the answer when
`ANTHROPIC_API_KEY` is set, offline it's extractive.

## Quick start

```sh
python -m labs.rag.demo
python -m labs.rag.cli ask "How do plants make energy from light?"
python -m labs.rag.cli ask "What is the capital of France?"      # abstains
python -m labs.rag.cli retrieve "reliable ordered delivery"
python -m labs.rag.cli stats
```

```
Q: Which protocol guarantees reliable, ordered delivery?
A: TCP is a connection-oriented protocol that guarantees reliable, ordered
   delivery of a stream of bytes between applications.  [source: TCP/IP networking]
   confidence 0.67 · cited: TCP/IP networking

Q: What is the capital of France?
A: I couldn't find that in the knowledge base.  (abstained)
```

## The pipeline

1. **Index** (`index.py`). Split each document into sentence chunks. Build a
   **TF-IDF** vector per chunk: each term weighted by `tf · idf` — frequent in
   this chunk but rare across the corpus scores highest — then L2-normalized so
   cosine similarity is a dot product. (IDF is computed from scratch: `log((N+1)/
   (df+1)) + 1`.)
2. **Retrieve.** Vectorize the question the same way and return the top-k chunks
   by cosine similarity.
3. **Answer** (`rag.py`). If the top score clears a relevance **threshold**,
   return the most relevant retrieved sentence with its source citation;
   otherwise **abstain**. No source above threshold → no answer.

## Why grounding matters

The abstention is the point. A bare model will happily invent a plausible answer
to "What is the capital of France?" even if that's outside its remit; RAG answers
*only* from retrieved evidence and says so when there's none — which is exactly
how you make an assistant you can trust over your own corpus. Swap the
`KNOWLEDGE_BASE` for your documents and the same machinery grounds answers in
them.

## Tests

```sh
python -m unittest labs.rag.tests.test_rag -v
```
