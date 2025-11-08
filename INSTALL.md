# Installation Instructions for MCP Client

## Option 1: Install All Dependencies at Once (Recommended)

Install directly from the `pyproject.toml` file:

```bash
pip install -e .
```

Or if you're using `uv` (which is recommended based on your project structure):

```bash
uv pip install -e .
```

## Option 2: Install Individual Dependencies

Install each dependency separately:

```bash
# Ollama Python client (for free LLM)
pip install "ollama>=0.1.0"

# MCP SDK with CLI support
pip install "mcp[cli]>=1.18.0"

# Python dotenv for environment variables
pip install "python-dotenv>=1.1.1"
```

## Option 3: Install from requirements.txt (if you prefer)

If you want to create a requirements.txt file, you can extract dependencies:

```bash
pip install -e . > requirements.txt
```

Then install from requirements.txt:

```bash
pip install -r requirements.txt
```

## Complete Installation Command

Run this single command to install everything:

```bash
pip install "ollama>=0.1.0" "mcp[cli]>=1.18.0" "python-dotenv>=1.1.1"
```

## Verify Installation

After installation, verify all packages are installed:

```bash
pip list | findstr "ollama mcp python-dotenv"
```

Or check individually:

```bash
python -c "import ollama; print('ollama:', ollama.__version__)"
python -c "import mcp; print('mcp installed')"
python -c "import dotenv; print('python-dotenv installed')"
```

## Notes

- **Python version**: Requires Python >= 3.13
- **Ollama**: Make sure Ollama is also installed on your system (separate from Python package)
- **MCP**: The `[cli]` extra includes command-line tools for MCP



