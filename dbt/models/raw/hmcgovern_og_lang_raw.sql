-- models/my_bible_model.sql
SELECT * FROM read_parquet('https://huggingface.co/datasets/hmcgovern/original-language-bibles-greek/resolve/main/data/train-00000-of-00001.parquet')