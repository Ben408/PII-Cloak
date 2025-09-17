# Contributing to Cloak & Style

Thank you for your interest in contributing to Cloak & Style! This document provides guidelines and information for contributors.

## 🎯 Project Overview

Cloak & Style is a professional PII (Personally Identifiable Information) data scrubbing tool designed for content professionals. Our mission is to make data privacy elegant and accessible while maintaining the highest standards of security and usability.

## 🤝 How to Contribute

### Types of Contributions

We welcome contributions in the following areas:

- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Submit pull requests for improvements
- **Documentation**: Improve guides, README, and code comments
- **Testing**: Help ensure quality and reliability
- **Translation**: Help localize the application

### Before You Start

1. **Check Existing Issues**: Search for existing issues or pull requests
2. **Read Documentation**: Familiarize yourself with the project structure
3. **Set Up Development Environment**: Follow the setup instructions below

## 🛠️ Development Setup

### Prerequisites

- Python 3.11+
- Git
- Windows 10/11 (for testing)
- 8-16 GB RAM recommended

### Local Development Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/cloak-and-style.git
   cd cloak-and-style
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\Activate.ps1
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Development Dependencies**
   ```bash
   pip install pytest pytest-cov black flake8 mypy
   ```

5. **Run Tests**
   ```bash
   python -m pytest test/ -v
   ```

### Project Structure

```
cloak-and-style/
├── core/                    # Core functionality
│   ├── detection_engine.py  # PII detection logic
│   ├── file_processor.py    # File processing
│   ├── document_modifier.py # Document modification
│   ├── report_generator.py  # Report generation
│   ├── performance_optimizer.py # Performance optimization
│   └── cli.py              # Command-line interface
├── pii-mask/               # ML model integration
├── test/                   # Test files and test data
├── cloak_and_style_ui.py   # Main GUI application
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
└── CONTRIBUTING.md        # This file
```

## 📝 Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line Length**: 88 characters (Black formatter default)
- **Docstrings**: Google style docstrings
- **Type Hints**: Required for all public functions
- **Imports**: Organized with isort

### Code Formatting

We use automated tools for code formatting:

```bash
# Format code
black .

# Sort imports
isort .

# Check code style
flake8 .

# Type checking
mypy core/ cloak_and_style_ui.py
```

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(ui): add dark mode support`
- `fix(detection): resolve false positive in email detection`
- `docs(readme): update installation instructions`
- `test(core): add unit tests for file processor`

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest test/ -v

# Run specific test file
python -m pytest test/test_detection.py -v

# Run with coverage
python -m pytest test/ --cov=core --cov-report=html

# Run performance tests
python -m pytest test/ -k "performance" -v
```

### Writing Tests

- **Test Structure**: Follow the existing test patterns
- **Test Data**: Use the test files in the `test/` directory
- **Coverage**: Aim for 90%+ code coverage
- **Performance**: Include performance benchmarks for critical paths

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Test memory usage and processing speed
- **Security Tests**: Test privacy and data handling

## 🔒 Security Guidelines

### Data Privacy

- **No PII in Code**: Never commit files containing real PII
- **Test Data**: Use synthetic data for testing
- **Local Processing**: Ensure all processing remains local
- **Memory Management**: Properly clean up sensitive data

### Code Review Security Checklist

- [ ] No hardcoded credentials
- [ ] No PII in logs or error messages
- [ ] Proper input validation
- [ ] Secure file handling
- [ ] Memory cleanup for sensitive data

## 📋 Pull Request Process

### Before Submitting

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

3. **Test Your Changes**
   ```bash
   # Run all tests
   python -m pytest test/ -v
   
   # Check code quality
   black . --check
   flake8 .
   mypy core/ cloak_and_style_ui.py
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat(scope): description of changes"
   ```

### Pull Request Guidelines

1. **Title**: Clear, descriptive title
2. **Description**: Detailed description of changes
3. **Related Issues**: Link to related issues
4. **Testing**: Describe how you tested the changes
5. **Breaking Changes**: Note any breaking changes

### Review Process

1. **Automated Checks**: All CI checks must pass
2. **Code Review**: At least one maintainer must approve
3. **Testing**: Changes must be tested on Windows
4. **Documentation**: Documentation must be updated

## 🐛 Bug Reports

### Before Reporting

1. **Search Issues**: Check if the bug has already been reported
2. **Reproduce**: Ensure you can reproduce the issue
3. **Gather Information**: Collect relevant system information

### Bug Report Template

```markdown
**Bug Description**
Brief description of the issue

**Steps to Reproduce**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**
What you expected to happen

**Actual Behavior**
What actually happened

**System Information**
- OS: Windows 10/11
- Python Version: 3.11.x
- Cloak & Style Version: 1.0.0
- RAM: 8-16 GB

**Additional Information**
Any other relevant information
```

## 💡 Feature Requests

### Before Requesting

1. **Search Issues**: Check if the feature has been requested
2. **Think Through**: Consider implementation complexity
3. **Check Roadmap**: See if it's already planned

### Feature Request Template

```markdown
**Feature Description**
Brief description of the feature

**Use Case**
Why this feature would be useful

**Proposed Implementation**
How you think it could be implemented

**Alternatives Considered**
Other approaches you considered

**Additional Information**
Any other relevant information
```

## 🏷️ Issue Labels

We use the following labels to categorize issues:

- **bug**: Something isn't working
- **enhancement**: New feature or request
- **documentation**: Improvements or additions to documentation
- **good first issue**: Good for newcomers
- **help wanted**: Extra attention is needed
- **priority: high**: High priority issues
- **priority: low**: Low priority issues
- **security**: Security-related issues

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code contributions

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) for details.

## 🙏 Recognition

### Contributors

All contributors will be recognized in:

- **README.md**: Contributors section
- **Release Notes**: Credit for significant contributions
- **Documentation**: Attribution for documentation contributions

### Hall of Fame

Contributors who make significant contributions will be added to our Hall of Fame in the project documentation.

## 📄 License

By contributing to Cloak & Style, you agree that your contributions will be licensed under the MIT License.

## 🎉 Thank You

Thank you for contributing to Cloak & Style! Your contributions help make data privacy more accessible and secure for everyone.

---

**Questions?** Feel free to open an issue or start a discussion on GitHub!
