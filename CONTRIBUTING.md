# Contributing to LAMB Cognitive Operating System

Thank you for your interest in contributing to LAMB! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming and inclusive community.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- A GitHub account
- Familiarity with Python, FastAPI, and cognitive computing concepts

### Setting Up Development Environment

1. **Fork the Repository**
   ```bash
   # Fork the repository on GitHub
   # Clone your fork
   git clone https://github.com/YOUR_USERNAME/LAMB-Core.git
   cd LAMB-Core
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run Tests**
   ```bash
   pytest tests/
   ```

6. **Run Smoke Tests**
   ```bash
   python test_lamb.py
   ```

## Development Workflow

### Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/***: New features
- **bugfix/***: Bug fixes
- **hotfix/***: Critical production fixes
- **docs/***: Documentation updates

### Creating a Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### Making Changes

1. Write clean, well-documented code
2. Follow coding standards (see below)
3. Add tests for new functionality
4. Update documentation
5. Commit changes with descriptive messages

### Commit Message Format

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks

**Example:**
```
feat(classification): add LLM-based classifier

Implemented a new classifier that uses Claude API for
more accurate memory classification. This improves
precision from 15% to 25% on the benchmark suite.

Closes #123
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines
- Use [Black](https://github.com/psf/black) for formatting
- Use [isort](https://github.com/PyCQA/isort) for import sorting
- Maximum line length: 100 characters

### Type Hints

- Use type hints for all function signatures
- Use `typing` module for complex types
- Return types should always be specified

```python
from typing import Dict, List, Optional

def classify_memory(
    content: str,
    session_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> ClassificationResult:
    """Classify memory content into memory types."""
    ...
```

### Documentation

- Use docstrings for all modules, classes, and public functions
- Follow Google docstring format
- Include parameter descriptions and return types

```python
def compute_salience(
    text: str,
    query_embedding: np.ndarray,
    store: MemoryStore,
    session_id: str
) -> float:
    """Compute salience score for a given text.
    
    Args:
        text: The input text to evaluate.
        query_embedding: The embedding vector for the text.
        store: The memory store instance.
        session_id: The session identifier.
        
    Returns:
        A salience score between 0.0 and 1.0.
        
    Raises:
        ValueError: If text is empty or None.
    """
    ...
```

### Error Handling

- Use specific exception types
- Provide meaningful error messages
- Log errors appropriately
- Never silently catch exceptions

```python
try:
    result = await classify_memory(input_data)
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    raise
except ClassificationError as e:
    logger.warning(f"Classification failed: {e}")
    # Handle gracefully
```

## Testing

### Unit Tests

- Write unit tests for all new functions
- Use pytest framework
- Aim for >80% code coverage
- Mock external dependencies

```python
import pytest
from memory_classification.core.engine import ClassificationEngine

def test_classify_memory():
    """Test memory classification."""
    engine = ClassificationEngine()
    result = engine.classify(test_input)
    assert result.memory_types == ["identity_memory"]
```

### Integration Tests

- Test component interactions
- Test API endpoints
- Test database operations

### Benchmark Tests

- Run benchmarks before submitting PR
- Ensure performance doesn't degrade
- Document any performance changes

```bash
python benchmarks/classification_bench/run_benchmarks.py
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=memory_classification --cov=attention --cov-report=html

# Run specific test file
pytest tests/unit/memory_classification/test_engine.py

# Run with verbose output
pytest tests/ -v
```

## Documentation

### Code Documentation

- Keep docstrings up to date
- Document complex algorithms
- Add inline comments for non-obvious logic

### README Updates

- Update README.md for user-facing changes
- Update CHANGELOG.md for version changes
- Add architecture diagrams for major changes

### API Documentation

- Update API reference for endpoint changes
- Add examples for new endpoints
- Document request/response schemas

## Pull Request Process

### Before Submitting

1. **Update Documentation**
   - Update relevant documentation
   - Add changelog entry
   - Update README if needed

2. **Run Tests**
   ```bash
   pytest tests/
   python test_lamb.py
   ```

3. **Run Linters**
   ```bash
   black .
   isort .
   mypy memory_classification/
   ```

4. **Check Formatting**
   ```bash
   black --check .
   ```

### Submitting PR

1. Push your branch
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create Pull Request on GitHub
   - Use descriptive title
   - Reference related issues
   - Add description of changes
   - Include screenshots for UI changes

3. PR Template
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests added/updated
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] Changelog updated
   - [ ] No new warnings generated
   ```

### Review Process

1. Automated checks must pass
2. At least one maintainer approval required
3. Address all review comments
4. Update PR based on feedback

### Merging

- Squash commits for clean history
- Use semantic commit messages for PR titles
- Delete branch after merge

## Release Process

### Version Bumping

Follow semantic versioning (MAJOR.MINOR.PATCH)

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Release Checklist

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Update README.md if needed
4. Run full test suite
5. Run benchmarks
6. Create release branch
7. Tag release
8. Push to GitHub
9. Create GitHub release
10. Update documentation

### Release Notes Template

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature 1
- New feature 2

### Changed
- Performance improvement
- API update

### Fixed
- Bug fix 1
- Bug fix 2

### Removed
- Deprecated feature

### Security
- Security fix
```

## Getting Help

- **Documentation**: Check existing docs first
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our Discord community (link in README)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to LAMB! 🚀
