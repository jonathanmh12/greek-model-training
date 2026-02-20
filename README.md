# Greek Model Training

Training pipeline for building Greek semantic embedding models.

## Overview

This repository contains the code for training transformer-based models on Biblical Greek text. It supports:
- Tokenizer training
- Model fine-tuning with various configurations
- Experiment tracking with MLflow
- Data cleaning and preprocessing

## Project Structure

```
├── notebooks/          # Jupyter notebooks for experimentation
│   ├── pipeline_train.ipynb
│   ├── tokenizing_embedding.ipynb
│   ├── transform_the_data.ipynb
│   └── ...
├── scripts/           # Standalone training scripts
│   ├── train_tokenizer.py
│   ├── clean_data.py
│   └── load_datasets.py
├── data/              # Training data (Greek corpus)
├── models/            # Trained model checkpoints
└── pyproject.toml
```

## Setup

```bash
uv sync
```

## dbt Persistence (DuckDB)

A minimal dbt project is available in `dbt/` for persisting cleaned corpus text into a local DuckDB warehouse.

### Run dbt

```bash
cd dbt
DBT_PROFILES_DIR=. uv run dbt debug
DBT_PROFILES_DIR=. uv run dbt run
DBT_PROFILES_DIR=. uv run dbt test
```

### Output

- DuckDB file: `data/greek_training.duckdb`
- Raw model: `analytics.raw_corpus`
- Staging model: `analytics.stg_corpus`

### dbt XML pipeline (share-first)

The dbt flow now mirrors this sequence:
1. `raw_corpus`: ingest **all XML files** from the mounted share (no whitelist yet), plus supplementary text
2. `stg_corpus_cleaned`: normalize XML body content and whitespace
3. `stg_corpus`: split into sentence-like rows and apply whitelist filtering downstream

#### Configure mounted share inputs

```bash
export CORPUS_XML_GLOB="/mnt/proxmox_greek/First1KGreek/data/**/*.xml"
export ADDITIONAL_TEXT_PATH="/mnt/proxmox_greek/corpus/combined_text_NT.txt"
```

Optional: override whitelist at runtime to limit the authors to a certain time or place:

```bash
DBT_PROFILES_DIR=. uv run dbt run --vars '{author_whitelist: [tlg0543, tlg0527, tlg0007]}'
```

Run the pipeline:

```bash
cd dbt
DBT_PROFILES_DIR=. uv run dbt run
DBT_PROFILES_DIR=. uv run dbt test
```

## Training

See notebooks for detailed training procedures. Key workflows:
- `tokenizing_embedding.ipynb` - Build tokenizer and initial embeddings
- `pipeline_train.ipynb` - Main training pipeline
- `transform_the_data.ipynb` - Data preparation

## Model Output

Trained models are saved to `models/` and can be used by the UI repo.

## Tracking

Experiments are tracked with MLflow. See `MLFLOW.md` for details.
