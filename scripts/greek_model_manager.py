import torch
import os
from pathlib import Path
import tempfile
from transformers import (
    RobertaConfig, RobertaForMaskedLM, RobertaTokenizerFast, 
    DataCollatorForLanguageModeling, Trainer, TrainingArguments
)
from datasets import load_dataset
from clean_data import build_greek_corpus_from_dbt

class GreekModelPipeline:
    def __init__(self, model_name, vocab_size=30000):
        self.model_name = model_name
        self.vocab_size = vocab_size
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None

    def load_tokenizer(self, path="."):
        # Assumes vocab.json and merges.txt are in the path
        self.tokenizer = RobertaTokenizerFast.from_pretrained(
            path, max_len=512, bos_token="<s>", eos_token="</s>", 
            sep_token="</s>", cls_token="<s>", unk_token="<unk>", 
            pad_token="<pad>", mask_token="<mask"
        )

    def init_new_model(self, layers=6, heads=12):
        config = RobertaConfig(
            vocab_size=self.vocab_size,
            max_position_embeddings=514,
            num_attention_heads=heads,
            num_hidden_layers=layers,
            type_vocab_size=1,
        )
        self.model = RobertaForMaskedLM(config=config).to(self.device)

    def train(self, corpus_path, epochs=10, batch_size=32):
        # 1. Dataset setup
        raw_ds = load_dataset("text", data_files={"train": corpus_path})
        tokenized_ds = raw_ds.map(
            lambda x: self.tokenizer(x["text"], truncation=True, max_length=128, padding="max_length"),
            batched=True, remove_columns=["text"], load_from_cache_file=False
        )

        # 2. Collator
        collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer, mlm=True, mlm_probability=0.15
        )

        # 3. Training Args
        checkpoints_dir = Path("models/local_checkpoints") / self.model_name
        checkpoints_dir.mkdir(parents=True, exist_ok=True)

        args = TrainingArguments(
            output_dir=str(checkpoints_dir),
            overwrite_output_dir=True,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            save_total_limit=2,
            fp16=True if self.device == "cuda" else False,
            logging_steps=100, # See loss more frequently
            prediction_loss_only=True,
        )

        trainer = Trainer(
            model=self.model, args=args, data_collator=collator,
            train_dataset=tokenized_ds["train"]
        )
        
        trainer.train()
        final_dir = Path("models/local_exports") / self.model_name
        final_dir.mkdir(parents=True, exist_ok=True)
        self.model.save_pretrained(str(final_dir))
        self.tokenizer.save_pretrained(str(final_dir))

    def train_from_dbt(self, whitelist=None, epochs=10, batch_size=32, run_dbt=True):
        sentences = build_greek_corpus_from_dbt(whitelist=whitelist, run_dbt=run_dbt)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
            tmp.write("\n".join(sentences))
            temp_path = tmp.name

        try:
            self.train(corpus_path=temp_path, epochs=epochs, batch_size=batch_size)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def get_similarity(self, word1, word2):
        # Helper for semantic domain testing
        def get_vec(text):
            inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
            with torch.no_grad():
                out = self.model.roberta(**inputs)
            return out.last_hidden_state.mean(dim=1).squeeze()
        
        v1, v2 = get_vec(word1), get_vec(word2)
        return torch.nn.functional.cosine_similarity(v1, v2, dim=0).item()