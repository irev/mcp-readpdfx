# Contributing to OCR PDF MCP Server

Thank you for your interest in contributing to the OCR PDF MCP Server! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Documentation](#documentation)

## Code of Conduct

This project follows a simple code of conduct:
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a professional environment

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Tesseract OCR installed on your system
- Basic knowledge of PDF processing and OCR

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ocr-pdf-mcp.git
   cd ocr-pdf-mcp
   ```

## Development Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.template .env
   # Edit .env with your Tesseract path and preferences
   ```

4. **Run the automated installer to verify setup:**
   ```bash
   python install.py
   ```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-language-support`
- `bugfix/fix-pdf-parsing-error`
- `docs/update-installation-guide`
- `refactor/improve-ocr-performance`

### Development Workflow

1. **Create a new branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write code following the established patterns
   - Add tests for new functionality
   - Update documentation as needed
   - Test thoroughly

3. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add support for new OCR language"
   ```

### Commit Message Convention

We use conventional commits:
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `style:` formatting changes
- `refactor:` code refactoring
- `test:` adding tests
- `chore:` maintenance tasks

## Testing

### Running Tests

1. **Basic functionality test:**
   ```bash
   python server.py --test
   ```

2. **Test with sample PDFs:**
   - Place test PDFs in `pdf-test/` directory
   - Run comprehensive tests with various PDF types

3. **Test client configurations:**
   ```bash
   python install.py --test-config
   ```

### Test Coverage

Ensure your changes include appropriate tests:
- Unit tests for new functions
- Integration tests for MCP tools
- Edge case testing for error handling
- Cross-platform compatibility testing

### Test Guidelines

- Test both success and failure scenarios
- Include tests for different PDF types (text, scanned, mixed)
- Test with various OCR languages
- Verify error handling and logging
- Test memory usage with large files

## Submitting Changes

### Pull Request Process

1. **Update your branch:**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Push your changes:**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request:**
   - Provide a clear title and description
   - Reference any related issues
   - Include screenshots for UI changes
   - List any breaking changes

### Pull Request Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed
- [ ] Cross-platform testing (if applicable)

## Documentation
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] README.md updated (if needed)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] No unnecessary debug code left
```

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length:** 100 characters (not 79)
- **Imports:** Group imports logically
- **Type hints:** Use type hints for function parameters and returns
- **Docstrings:** Use Google-style docstrings
- **Error handling:** Comprehensive error handling with logging

### Code Examples

**Function with proper style:**
```python
def process_pdf_page(
    pdf_path: str, 
    page_num: int, 
    ocr_language: str = "eng"
) -> Dict[str, Any]:
    """Process a single PDF page with OCR.
    
    Args:
        pdf_path: Path to the PDF file
        page_num: Page number to process (0-indexed)
        ocr_language: OCR language code(s)
        
    Returns:
        Dictionary containing extracted text and metadata
        
    Raises:
        OCRProcessingError: If OCR processing fails
        FileNotFoundError: If PDF file not found
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Failed to process page {page_num}: {e}")
        raise
```

### Configuration Management

- Use environment variables for configuration
- Provide sensible defaults
- Validate configuration on startup
- Document all configuration options

## Documentation

### Types of Documentation

1. **Code Documentation:**
   - Inline comments for complex logic
   - Docstrings for all public functions
   - Type hints for better code understanding

2. **User Documentation:**
   - Update README.md for user-facing changes
   - Update installation instructions
   - Update configuration examples

3. **Developer Documentation:**
   - Update this CONTRIBUTING.md
   - Update technical documentation
   - Update API documentation

### Documentation Standards

- Use clear, concise language
- Include practical examples
- Keep documentation up-to-date
- Test all documented procedures

## Areas for Contribution

### High Priority

- **Performance optimization** for large PDF processing
- **Additional OCR languages** and language packs
- **Advanced preprocessing** options for better OCR accuracy
- **Batch processing** capabilities
- **Error recovery** mechanisms

### Medium Priority

- **REST API mode** for HTTP access
- **Custom OCR models** integration
- **Advanced configuration** options
- **Monitoring and metrics** collection
- **Plugin system** for extensibility

### Low Priority

- **GUI interface** for desktop use
- **Cloud deployment** templates
- **Advanced PDF analysis** features
- **Machine learning** preprocessing
- **Performance dashboard**

## Getting Help

### Resources

- Check existing issues and pull requests
- Review the README.md and documentation
- Test with the provided sample PDFs
- Review the code for examples

### Communication

- **Issues:** Use GitHub issues for bug reports and feature requests
- **Discussions:** Use GitHub discussions for general questions
- **Code Review:** Be constructive and helpful in reviews

### Issue Templates

When creating issues, use these templates:

**Bug Report:**
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 11, macOS 12, Ubuntu 22.04]
- Python Version: [e.g., 3.12.0]
- Tesseract Version: [e.g., 5.4.0]
- MCP Client: [e.g., Claude Desktop]

## Additional Context
Any additional information
```

## Recognition

Contributors will be recognized in:
- CHANGELOG.md for significant contributions
- README.md contributors section
- Release notes for major features

Thank you for contributing to making OCR PDF MCP Server better for everyone!