# Contributing to StadiumAI

Thank you for your interest in contributing to StadiumAI! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites
- Python 3.12+
- Node.js 20+
- Git

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

## Development Workflow

### Code Style
- **Python**: Follow PEP 8, use Ruff for linting
- **JavaScript/TypeScript**: Follow ESLint rules
- **Commits**: Use conventional commits format

### Running Tests
```bash
# Backend
cd backend
pytest tests/ -v --cov=app

# Frontend
cd frontend
npm run test
npm run lint
```

### Code Quality
- All code must pass Ruff linting (backend)
- All code must pass ESLint (frontend)
- Maintain minimum 75% test coverage
- Add tests for new features

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Add/update tests
4. Ensure all tests pass
5. Update documentation if needed
6. Submit a pull request

## Reporting Issues

- Use GitHub Issues
- Include steps to reproduce
- Include expected vs actual behavior
- Include environment details

## Code of Conduct

Please follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Questions?

Feel free to open an issue for questions about contributing.
