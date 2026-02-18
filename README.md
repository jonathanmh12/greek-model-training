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

## Training

See notebooks for detailed training procedures. Key workflows:
- `tokenizing_embedding.ipynb` - Build tokenizer and initial embeddings
- `pipeline_train.ipynb` - Main training pipeline
- `transform_the_data.ipynb` - Data preparation

## Model Output

Trained models are saved to `models/` and can be used by the UI repo.

## Tracking

Experiments are tracked with MLflow. See `MLFLOW.md` for details.
