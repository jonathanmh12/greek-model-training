# MLFlow Integration Guide

This project uses MLFlow for experiment tracking, model versioning, and reproducibility.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -e .
```

The MLFlow dependency is included in `pyproject.toml`.

### 2. Run Training with MLFlow
Simply execute the training notebook as usual. MLFlow tracking is automatically enabled in [updated_training_notebook.ipynb](updated_training_notebook.ipynb).

### 3. View Experiment Results
After training, launch the MLFlow UI:
```bash
uv run mlflow server
```

Then navigate to http://localhost:5000 in your browser.

## 📊 What's Being Tracked

### Parameters
- Model architecture (vocab_size, hidden_layers, attention_heads, etc.)
- Training hyperparameters (epochs, batch_size, mlm_probability)
- Hardware configuration (GPU availability, fp16 mode)
- Model version

### Metrics
- Training loss over time
- Automatically logged by the Hugging Face Trainer

### Artifacts
- Trained BERT model
- Tokenizer
- Model configuration
- Consolidated local checkpoints under `models/local_checkpoints/`

## 📁 Data Storage

All MLFlow data is stored in:
```
mlruns/
├── 0/               # Default experiment
├── <experiment_id>/ # GreekBERT_Training experiment
└── .trash/          # Deleted runs
```

## 🔍 Comparing Experiments

The MLFlow UI allows you to:
- Compare multiple training runs side-by-side
- Filter and search experiments
- Visualize metric curves
- Download models and artifacts
- Track model lineage

## 💡 Tips

### Run Multiple Experiments
Each time you run the training notebook, a new experiment run is created. Compare different configurations by modifying hyperparameters between runs.

### Custom Run Names
The notebook creates a timestamped run name (for example, `GreekBERT_20260220_154500`) to avoid collisions. Customize it in the notebook:
```python
run_name = "my_custom_run_name"
with mlflow.start_run(run_name=run_name):
    ...
```

### Remote Tracking Server
For team collaboration, configure a remote MLFlow tracking server:
```python
mlflow.set_tracking_uri("http://your-mlflow-server:5000")
```

## 🛠️ Advanced Usage

### Load a Previous Model
```python
import mlflow

# Load model from a specific run
model_uri = "runs:/<run_id>/model"
model = mlflow.transformers.load_model(model_uri)
```

### Register Models
```python
mlflow.register_model(
    model_uri=f"runs:/{run.info.run_id}/model",
    name="GreekBERT"
)
```

## 📖 Resources
- [MLFlow Documentation](https://mlflow.org/docs/latest/index.html)
- [MLFlow Transformers Integration](https://mlflow.org/docs/latest/python_api/mlflow.transformers.html)
