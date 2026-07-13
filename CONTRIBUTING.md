# Contributing to DPR Agentic AI

Terima kasih sudah mau berkontribusi! 🎉

## Git Workflow

1. Checkout dari `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/nama-fitur
   ```

2. Commit dengan format konvensional:
   ```bash
   # Format: <type>(<scope>): <subject>
   git commit -m "feat(agents): implement Gemini zero-shot AKD classifier"
   git commit -m "fix(database): add unique constraint to content_items"
   git commit -m "test(agents): add unit tests for sentiment analysis"
   ```

   **Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
   **Scopes**: `agents`, `database`, `api`, `dashboard`, `tests`

3. Push dan buat Pull Request ke `develop`:
   ```bash
   git push origin feature/nama-fitur
   ```

## Development

```bash
# Install semua dependency (termasuk dev tools)
uv sync

# Run tests
uv run pytest tests/ -v

# Run linting
uv run ruff check src/

# Run type checking
uv run mypy src/
```

## Code Style

- Line length: 100 characters
- Python 3.11+ syntax
- Linting: `ruff`
- Type checking: `mypy`
- Docstrings on all public functions/classes

## Pull Request Checklist

- [ ] Tests pass (`uv run pytest`)
- [ ] Linting pass (`uv run ruff check src/`)
- [ ] New code has docstrings
- [ ] PR description explains the changes
