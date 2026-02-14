from transformers import AutoTokenizer
from dataclasses import dataclass

"""Actually, class was only made because of return token count. Autotokenizer already has the remaining functions. 
   If it is not needed to output how many tokens the creation of the model has required, this can actually be deleted 
   here."""


@dataclass
class Tokenizer:
    model_name: str
    tokenizer: AutoTokenizer = None

    def __post_init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def encode_plain_text(self, text: str) -> list:
        return self.tokenizer.encode(text)

    def decode_tokenized_text(self, token_l: list[int]) -> str:
        return self.tokenizer.decode(token_l)

    def return_token_count(self, text: str) -> int:
        return len(self.encode_plain_text(text=text))

    def return_vocab(self):
        return self.tokenizer.vocab

    def return_vocab_size(self):
        return self.tokenizer.vocab_size

    def return_special_tokens_and_ids(self):
        return self.tokenizer.added_tokens_encoder


def main() -> None:
    from src.utility.model_name_storage_HF import SAUERKRAUT_MODEL

    vago_tokenizer = Tokenizer(model_name=SAUERKRAUT_MODEL)
    enc = vago_tokenizer.encode_plain_text("Produkt:")
    dec = vago_tokenizer.decode_tokenized_text(enc)
    count = vago_tokenizer.return_token_count("Produkt:")
    print(enc, dec, count)


if __name__ == "__main__":
    main()
