"""
WHAT THIS FILE DOES: Defines one consistent way to send an instruction and
input text to a language model and get text back, so the rest of the
pipeline never has to know which provider is actually answering.
"""


class LLMProvider:
    """Every adapter (real or fake) implements this shape and nothing more."""

    def call(self, instruction: str, input_text: str) -> str:
        raise NotImplementedError
