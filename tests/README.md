# Tests

This directory contains unit and integration tests for the Decisions project.

## Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_argument_validator.py
│   ├── test_ml_scoring.py
│   └── test_llm_service.py
├── integration/             # Integration tests for full pipeline
│   └── test_analysis_pipeline.py
└── conftest.py             # Shared pytest fixtures
```

## Running Tests

### All Tests
```bash
# From project root
make test

# Or with pytest directly
pytest tests/ -v
```

### Unit Tests Only
```bash
pytest tests/unit/ -v
```

### Integration Tests Only
```bash
# Make sure backend is running first!
make back

# In another terminal
pytest tests/integration/ -v
```

### Specific Test File
```bash
pytest tests/unit/test_argument_validator.py -v
```

### With Coverage
```bash
pytest tests/ --cov=server --cov-report=html
```

## Test Categories

### Unit Tests
Test individual components in isolation:
- `test_argument_validator.py` - Validation logic, quality assessment
- `test_ml_scoring.py` - ML scoring, calibration, pairwise comparison

### Integration Tests
Test the complete pipeline:
- `test_analysis_pipeline.py` - End-to-end analysis flow, health checks, error handling

## Requirements

Install test dependencies:
```bash
pip install pytest pytest-cov requests
```

## CI/CD

Tests are automatically run in GitHub Actions on every push.

See `.github/workflows/test.yml` for CI configuration.
