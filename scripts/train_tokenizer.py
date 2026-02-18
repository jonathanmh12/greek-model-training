from tokenizers import ByteLevelBPETokenizer

def train_tokenizer(sentences: list, vocab_size: int = 30000):
    tokenizer = ByteLevelBPETokenizer()

    # train_from_iterator accepts the list directly
    tokenizer.train_from_iterator(
        iterator=sentences, 
        vocab_size=vocab_size, 
        min_frequency=2, 
        show_progress=True,
        special_tokens=["<s>", "<pad>", "</s>", "<unk>", "<mask>"]
    )

    return tokenizer