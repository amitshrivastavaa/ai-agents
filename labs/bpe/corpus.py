"""A small built-in training corpus (public-domain-style prose about agents)."""

CORPUS = """
An agent is a system that perceives its environment and acts upon it to achieve
goals. The simplest agents react directly to what they sense; more capable ones
maintain memory, form models of the world, and plan ahead before they act.
Planning means imagining the consequences of actions and choosing the sequence
that leads to the best expected outcome. Memory lets an agent improve over time,
recalling what worked and what did not, so that the same mistake is not repeated.

When several agents share an environment, intelligence can emerge from their
interaction. Ants find short paths by laying and following trails. Markets find
prices through countless local trades. Populations of strategies evolve toward
cooperation when reciprocity is rewarded and toward defection when it is not.
None of these systems has a central controller; the global behaviour is the sum
of many simple local rules, repeated again and again until a pattern settles.

Learning ties it together. A network of simple units, trained by gradient
descent, can approximate almost any function, turning raw experience into useful
prediction. Attention lets a model focus on the parts of its input that matter,
and memory lets it carry what it has learned from one moment to the next. The
same few ideas, composed in different ways, underlie reasoning, perception, and
language. Build them from first principles and the magic turns into mechanism.
""".strip()
