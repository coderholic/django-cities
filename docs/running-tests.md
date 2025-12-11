# Running Tests

We provide a comprehensive Docker-based test environment that automatically sets up PostgreSQL with PostGIS and tests against multiple Python and Django versions.

## Prerequisites

Install [just](https://github.com/casey/just) command runner:

```bash
# macOS
brew install just

# Linux
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

# Cargo (all platforms)
cargo install just

# Or see https://github.com/casey/just#installation for more options
```

## Quick Start (Recommended)

Run tests with the latest Python and Django versions:

```bash
just test-quick
```

This will test with Python 3.14 and Django 6.0.

## Run All Test Combinations

Test against all supported Python (3.12, 3.13, 3.14) and Django (5.0, 5.1, 5.2, 6.0) combinations:

```bash
just test-all
```

Or use the shell script directly:

```bash
./run-tests.sh all
```

## Run Specific Python + Django Version

Test a specific combination:

```bash
# Using just (cleaner syntax)
just test 3.14 6.0
just test 3.13 5.2
just test 3.12 5.0

# Using the script directly
./run-tests.sh 3.14 6.0
./run-tests.sh 3.13 5.2
```

## Test Specific Python or Django Version

```bash
# Test all Django versions with Python 3.14
just test-py314

# Test all Python versions with Django 6.0
just test-django60

# Test all Python versions with Django 5.2
just test-django52
```

## Available Test Combinations

- **Python 3.12**: Django 5.0, 5.1, 5.2, 6.0
- **Python 3.13**: Django 5.1, 5.2, 6.0
- **Python 3.14**: Django 5.2, 6.0

## Using Docker Compose Directly

Run a specific test service:

```bash
# Build and run tests
docker compose up --build test-py314-django60

# Run in background
docker compose up -d test-py314-django60

# View logs
docker compose logs -f test-py314-django60

# Clean up
docker compose down -v
```

## Additional Commands

```bash
# See all available commands
just --list

# Open a shell in the test environment
just shell

# Access the PostgreSQL database
just db-shell

# Run linter
just lint

# Format code with black
just format

# Run specific test file
just test-file test_models

# Clean up containers and volumes
just clean

# Show environment info
just info
```

## Manual Testing (Without Docker)

If you prefer to test without Docker:

1. Install PostgreSQL with PostGIS:

```bash
# macOS
brew install postgresql postgis

# Ubuntu/Debian
sudo apt-get install postgresql postgis libgdal-dev
```

2. Create the test database:

```bash
createdb django_cities
psql django_cities -c "CREATE EXTENSION postgis;"
```

3. Install dependencies and run tests:

```bash
cd test_project
python manage.py migrate
python manage.py test test_app --noinput
```

4. Or use tox for multiple versions:

```bash
pip install tox
tox  # Run all environments
tox -e py313-django51  # Run specific environment
```

## Useful Environment Variables

* `POSTGRES_USER` - Database user (default: `postgres`)
* `POSTGRES_PASSWORD` - Database password (default: `postgres`)
* `TRAVIS_LOG_LEVEL` - Set to `DEBUG` for verbose import script logs (default: `INFO`)
* `CITIES_FILES` - Set to `file://` path to use local test data files
