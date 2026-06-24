"""A small, multi-topic knowledge base (distinct topics so grounding is testable)."""

KNOWLEDGE_BASE = [
    {
        "id": "photosynthesis",
        "title": "Photosynthesis",
        "text": (
            "Photosynthesis is the process by which green plants convert light "
            "energy into chemical energy. It takes place mainly in the chloroplasts, "
            "using the pigment chlorophyll. Plants take in carbon dioxide and water "
            "and produce glucose and oxygen. The oxygen is released into the air as a "
            "by-product."
        ),
    },
    {
        "id": "tcp",
        "title": "TCP/IP networking",
        "text": (
            "TCP is a connection-oriented protocol that guarantees reliable, ordered "
            "delivery of a stream of bytes between applications. It establishes a "
            "connection with a three-way handshake before any data is sent. UDP, by "
            "contrast, is connectionless and does not guarantee delivery, which makes "
            "it faster for streaming and games."
        ),
    },
    {
        "id": "espresso",
        "title": "Espresso",
        "text": (
            "Espresso is a concentrated coffee brewed by forcing hot water under high "
            "pressure through finely ground coffee. A typical shot uses about nine bars "
            "of pressure and extracts in roughly twenty-five seconds. The layer of "
            "golden foam on top is called crema."
        ),
    },
    {
        "id": "moon",
        "title": "The Moon",
        "text": (
            "The Moon is Earth's only natural satellite and the fifth largest in the "
            "solar system. Its gravitational pull is the main cause of the ocean tides. "
            "The same side of the Moon always faces Earth because its rotation is "
            "tidally locked to its orbit."
        ),
    },
    {
        "id": "transformers",
        "title": "Transformers",
        "text": (
            "A transformer is a neural network architecture built around the attention "
            "mechanism, which lets the model weigh the relevance of different parts of "
            "the input. Transformers process all tokens in parallel rather than one at "
            "a time, which made them far more scalable than recurrent networks. They "
            "are the foundation of modern large language models."
        ),
    },
]
