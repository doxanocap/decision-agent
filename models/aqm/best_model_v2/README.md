# ML Model: best_model_v2

This directory contains the Cross-Encoder model for argument quality scoring.

## Model Details

- **Model**: Fine-tuned MiniLM-L-12-v2
- **Task**: Pairwise argument comparison
- **Size**: ~130MB
- **Format**: SafeTensors

## Download Model Weights

The model weights (`model.safetensors`) are **not included in the repository** due to size constraints.

### Option 1: Download from HuggingFace (Recommended)

If you have the model hosted on HuggingFace:
```bash
# From project root
cd models/aqm/best_model_v2
wget https://huggingface.co/YOUR_USERNAME/best_model_v2/resolve/main/model.safetensors
```

### Option 2: Use Default Model

The system will automatically fall back to the default `cross-encoder/ms-marco-MiniLM-L-12-v2` from HuggingFace if local weights are not found.

```python
# In server/services/ml_scoring.py
# Fallback logic is already implemented
```

### Option 3: Train Your Own

See `model.ipynb` for training code.

## Files

- `config.json` - Model configuration
- `tokenizer.json` - Tokenizer configuration
- `vocab.txt` - Vocabulary
- `model.safetensors` - **Model weights (not in repo, download separately)**

## Usage

The model is automatically loaded by `server/services/ml_scoring.py`:

```python
from server.services.ml_scoring import get_ml_scoring

ml_scoring = get_ml_scoring()
scores = ml_scoring.score_arguments(arguments, context)
```

## License

Same as parent project (MIT).