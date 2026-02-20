from datasets import Dataset, DatasetDict, load_dataset
from transformers import PreTrainedTokenizerFast

def load_datasets(raw_tokenizer, corpus_path: str | None = None, sentences: list[str] | None = None):
    # 1. Setup the wrapper for later use (Trainer needs it)
    fast_tokenizer = PreTrainedTokenizerFast(tokenizer_object=raw_tokenizer)
    fast_tokenizer.pad_token = "<pad>"
    fast_tokenizer.mask_token = "<mask>"

    # 2. Load the dataset
    if sentences is not None:
        raw_dataset = DatasetDict({"train": Dataset.from_dict({"text": sentences})})
    elif corpus_path is not None:
        raw_dataset = load_dataset("text", data_files={"train": corpus_path})
    else:
        raise ValueError("Provide either `corpus_path` or `sentences`.")

    # 3. Use the raw_tokenizer's .encode_batch method
    # This bypasses the buggy 'direction' argument entirely
    def tokenize_function(examples):
        # We manually truncate and pad here
        raw_tokenizer.enable_truncation(max_length=128)
        raw_tokenizer.enable_padding(length=128)
        
        # Encode the batch
        encodings = raw_tokenizer.encode_batch(examples["text"])
        
        # Return a dictionary of lists (what Datasets expects)
        return {
            "input_ids": [e.ids for e in encodings],
            "attention_mask": [e.attention_mask for e in encodings]
        }

    tokenized_datasets = raw_dataset.map(
        tokenize_function, 
        batched=True, 
        remove_columns=["text"],
        load_from_cache_file=False
    )

    return tokenized_datasets["train"]