# Development Guidelines

## Code Style

### Language
- All code comments, docstrings, and documentation must be written in English
- Variable names, function names, and class names should be in English
- Log messages and error messages should be in English

### Python Code Style
- Follow PEP 8 style guide
- Maximum line length is 100 characters
- Use Google style docstrings
- Use type hints for function parameters and return values

### Example
```python
def calculate_total(first_number: int, second_number: int) -> int:
    """Calculate the sum of two numbers.

    Args:
        first_number: The first number to add.
        second_number: The second number to add.

    Returns:
        The sum of the two numbers.

    Raises:
        ValueError: If either number is negative.
    """
    if first_number < 0 or second_number < 0:
        raise ValueError("Numbers must be non-negative")
    return first_number + second_number
```

### Documentation
- All public functions and classes must have docstrings
- Docstrings should follow Google style
- Include type hints for parameters and return values
- Document exceptions that may be raised
- Keep docstrings concise but informative

### Testing
- Write unit tests for all new functionality
- Test names should be descriptive and in English
- Follow the `test_<function_name>_<scenario>` naming pattern
- Include docstrings in test functions explaining what is being tested

### Git Commits
- Write commit messages in English
- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Reference issue numbers when applicable

### Code Review
- All code changes must be reviewed
- Reviewers should check for:
  - Code style compliance
  - Proper documentation
  - Test coverage
  - Performance implications
  - Security considerations

### Tools
We use the following tools for code quality:
- Black for code formatting
- isort for import sorting
- pylint for code analysis
- mypy for type checking
- pytest for testing

### Pre-commit Checks
Before submitting a PR, ensure:
1. All tests pass
2. Code is formatted with Black
3. Imports are sorted with isort
4. No pylint warnings
5. No mypy errors
6. Test coverage meets requirements

# 如何贡献代码
1. Fork 本仓库。
2. Clone 到本地：`git clone <你的fork地址>`
3. 创建新分支：`git checkout -b feature/你的功能名`
4. 提交更改：`git commit -m "描述你的更改"`
5. 推送到你的 fork：`git push origin feature/你的功能名`
6. 在 GitHub 上创建 Pull Request。

