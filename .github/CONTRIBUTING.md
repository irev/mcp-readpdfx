# Contributing to ReadPDFx

Thank you for your interest in contributing to ReadPDFx! We welcome contributions from the community and are pleased to have you join us.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please be respectful and inclusive in all interactions.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Tesseract OCR
- Basic understanding of MCP Protocol

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/readpdfx.git
   cd readpdfx
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Install Tesseract OCR**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr tesseract-ocr-eng

   # macOS
   brew install tesseract

   # Windows
   choco install tesseract
   ```

4. **Verify installation**
   ```bash
   python run.py --help
   python -m pytest tests/
   ```

## 🔧 Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-ocr-tool` - New features
- `fix/resolve-import-error` - Bug fixes
- `docs/update-readme` - Documentation updates
- `refactor/reorganize-structure` - Code refactoring

### Commit Message Format

Follow conventional commit format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `chore`: Maintenance tasks

**Examples:**
```
feat(ocr): add multi-language support for OCR processing

fix(server): resolve import path issues after restructure

docs(client): update Claude Desktop integration guide
```

### Development Workflow

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run tests
   python -m pytest tests/ -v

   # Run code quality checks
   flake8 src/ tests/ scripts/
   black --check src/ tests/ scripts/
   mypy src/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

## 📤 Submitting Changes

### Pull Request Process

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Go to GitHub and create a PR from your branch
   - Fill out the PR template completely
   - Link related issues
   - Describe your changes clearly

3. **PR Review Process**
   - Automated tests will run
   - Maintainers will review your code
   - Address any feedback promptly
   - Make requested changes

4. **Merge**
   - Once approved, your PR will be merged
   - Your branch will be deleted
   - Thank you for contributing! 🎉

### PR Requirements

- [ ] All tests pass
- [ ] Code style checks pass
- [ ] Documentation updated
- [ ] CHANGELOG updated (for significant changes)
- [ ] No breaking changes (or properly documented)

## 🎨 Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 127 characters
- Use meaningful variable names
- Add docstrings to all public functions

```python
def process_pdf_smart(
    pdf_path: str, 
    language: str = "eng",
    output_format: str = "text"
) -> MCPToolResult:
    """
    Intelligently process PDF with automatic OCR detection.
    
    Args:
        pdf_path: Absolute path to the PDF file
        language: OCR language code (default: "eng")
        output_format: Output format (default: "text")
        
    Returns:
        MCPToolResult with extracted text and metadata
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If invalid parameters provided
    """
    # Implementation here
    pass
```

### File Organization

- `src/` - Core MCP server code
- `scripts/` - Utility scripts
- `tests/` - Test files
- `client-configs/` - Client integration guides
- `ocr_pdf_mcp/` - Original OCR utilities

### Import Organization

```python
# Standard library imports
import sys
import os
from typing import Dict, List, Optional

# Third-party imports
from fastapi import FastAPI
import pytest

# Local imports
from .mcp_types import MCPTool
from .mcp_server import MCPServer
```

## 🧪 Testing Guidelines

### Test Structure

- Write tests for all new functionality
- Maintain or improve test coverage
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

```python
def test_process_pdf_smart_with_digital_pdf():
    """Test smart PDF processing with digital PDF content."""
    # Arrange
    pdf_path = "tests/fixtures/digital_sample.pdf"
    expected_text = "Sample digital text"
    
    # Act
    result = process_pdf_smart(pdf_path, language="eng")
    
    # Assert
    assert result.is_error is False
    assert expected_text in result.content[0].text
```

### Test Categories

- **Unit Tests**: Test individual functions
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Test performance requirements

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_mcp_server.py -v

# Run tests matching pattern
python -m pytest tests/ -k "test_ocr"
```

## 📚 Documentation Guidelines

### Documentation Types

1. **Code Documentation**
   - Docstrings for all public functions
   - Inline comments for complex logic
   - Type hints for all functions

2. **User Documentation**
   - README updates
   - Client integration guides
   - Installation instructions

3. **Developer Documentation**
   - API documentation
   - Architecture decisions
   - Contributing guidelines

### Writing Style

- Use clear, concise language
- Provide examples
- Include troubleshooting tips
- Keep documentation up to date

## 🐛 Bug Reports

When reporting bugs, please include:

- ReadPDFx version
- Operating system and Python version
- MCP client being used
- Steps to reproduce
- Expected vs actual behavior
- Error logs and stack traces
- Sample files (if applicable)

## 💡 Feature Requests

For feature requests, please provide:

- Clear description of the feature
- Use case and benefits
- Proposed implementation approach
- Examples of how it would work
- Willingness to contribute

## 🔍 Code Review Guidelines

### For Contributors

- Keep PRs focused and small
- Write clear commit messages
- Respond to feedback promptly
- Be open to suggestions

### For Reviewers

- Be constructive and helpful
- Focus on code quality and maintainability
- Check for test coverage
- Verify documentation updates

## 📋 Release Process

### Version Numbering

We follow Semantic Versioning (SemVer):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes (backward compatible)

### Release Checklist

- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release notes
- [ ] Tag release in Git

## 🏷️ Labels and Tags

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed

### Priority Labels

- `priority: critical` - Critical issues
- `priority: high` - High priority
- `priority: medium` - Medium priority
- `priority: low` - Low priority

## 🎯 Areas for Contribution

We especially welcome contributions in these areas:

### 🔧 Core Features
- New OCR processing capabilities
- Performance optimizations
- Additional file format support
- Enhanced error handling

### 📱 Client Integration
- New MCP client support
- Improved integration guides
- Client-specific optimizations
- Connection reliability improvements

### 📚 Documentation
- Tutorial improvements
- API documentation
- Troubleshooting guides
- Translation to other languages

### 🧪 Testing
- Additional test cases
- Performance benchmarks
- Integration tests
- Test automation improvements

### 🛠️ DevOps
- CI/CD improvements
- Docker optimizations
- Deployment automation
- Monitoring and logging

## 💬 Getting Help

If you need help with contributing:

- Check existing issues and discussions
- Create a new issue with the `question` label
- Join our community discussions
- Reach out to maintainers

## 🙏 Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub contributor graph
- Special thanks in major releases

Thank you for contributing to ReadPDFx! 🚀