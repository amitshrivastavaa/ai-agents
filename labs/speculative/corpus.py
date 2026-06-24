"""Training text for the draft and target n-gram models."""

CORPUS = """
The agent observes the world, decides on an action, and acts. It observes the
result, learns from the reward, and tries again. A good agent plans before it
acts, remembers what worked, and avoids the mistakes it made before. The best
agents are simple inside but careful about the world outside.

A language model predicts the next token from the tokens that came before. It
learns the patterns of language by counting what follows what, and it generates
text one token at a time. A small model is fast but often wrong; a large model
is accurate but slow. Speculative decoding uses the small model to guess and the
large model to check, so the system is both fast and accurate at the same time.

To plan is to imagine the consequences of actions before taking them. To learn
is to improve from experience over time. To reason is to search for the steps
that lead from what is known to what is wanted. These are the oldest ideas in
artificial intelligence, and they still matter today, because the patterns that
worked before tend to work again, again and again.
""".strip()
