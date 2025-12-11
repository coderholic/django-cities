# Development

If you're contributing to django-cities, we provide code quality tools and pre-commit hooks to ensure consistent code style and catch common issues.

## Code Quality Tools

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting. Ruff is a fast Python linter and formatter written in Rust that replaces multiple tools (flake8, black, isort, etc.).

### Install Development Tools

```bash
# Install ruff
pip install ruff

# Install pre-commit
pip install pre-commit
```

### Linting

```bash
# Check code for issues
just lint

# Check and automatically fix issues
just lint-fix

# Check formatting without making changes
just format-check
```

### Formatting

```bash
# Format code with ruff
just format
```

Ruff is configured in `pyproject.toml` to match the existing code style (ignoring line length and binary operator line breaks).

## Pre-commit Hooks

Pre-commit hooks automatically run checks before each commit to catch issues early. We use hooks for:

- **Ruff linting and formatting** - Ensures code quality and consistent style
- **Django system checks** - Runs `manage.py check` to catch Django-specific issues
- **Migration checks** - Ensures no migrations are missing with `makemigrations --check`
- **Basic file checks** - Trailing whitespace, end-of-file, YAML syntax, etc.

### Install Pre-commit Hooks

```bash
# Install the hooks
just pre-commit-install

# Or manually
pre-commit install
```

### Run Pre-commit Hooks

```bash
# Run on all files (useful before creating PR)
just pre-commit

# Or manually
pre-commit run --all-files

# Update hooks to latest versions
just pre-commit-update
```

Once installed, the hooks will run automatically on `git commit`. If any hook fails:
1. Review the errors
2. Fix the issues (some hooks auto-fix)
3. Stage the fixes with `git add`
4. Commit again

### Available Just Commands

```bash
just lint              # Run ruff linter
just lint-fix          # Run ruff linter with auto-fix
just format            # Format code with ruff
just format-check      # Check formatting without changes
just pre-commit-install    # Install pre-commit hooks
just pre-commit            # Run pre-commit on all files
just pre-commit-update     # Update pre-commit hooks
```
