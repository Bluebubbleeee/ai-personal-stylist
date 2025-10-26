# Contributing to AI-Powered Personal Stylist

Thank you for your interest in contributing to the AI-Powered Personal Stylist project! We welcome contributions from the community and appreciate your help in making this project better.

## 🤝 How to Contribute

### Reporting Issues
- Use the GitHub issue tracker to report bugs
- Provide detailed information about the issue
- Include steps to reproduce the problem
- Add screenshots if applicable

### Suggesting Features
- Open a new issue with the "enhancement" label
- Describe the feature in detail
- Explain why it would be beneficial
- Consider the impact on existing functionality

### Code Contributions
- Fork the repository
- Create a feature branch
- Make your changes
- Add tests for new functionality
- Submit a pull request

## 🛠️ Development Setup

### Prerequisites
- Python 3.11+
- Git
- Code editor (VS Code, PyCharm, etc.)

### Setup Steps
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/ai-personal-stylist.git
   cd ai-personal-stylist
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```
6. Run migrations:
   ```bash
   python manage.py migrate
   ```
7. Start the development server:
   ```bash
   python manage.py runserver
   ```

## 📝 Coding Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Use type hints where appropriate

### Django Best Practices
- Use class-based views when appropriate
- Follow Django's naming conventions
- Use Django's built-in security features
- Write comprehensive tests
- Use Django's ORM efficiently

### Frontend Guidelines
- Use semantic HTML
- Follow Bootstrap 5 conventions
- Write clean, readable CSS
- Use meaningful class names
- Ensure responsive design

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.wardrobe

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Writing Tests
- Write tests for new features
- Test edge cases and error conditions
- Use descriptive test names
- Keep tests independent and isolated
- Mock external API calls

### Test Structure
```python
class TestClothingItemModel(TestCase):
    def setUp(self):
        """Set up test data"""
        pass
    
    def test_model_creation(self):
        """Test model creation"""
        pass
    
    def test_model_validation(self):
        """Test model validation"""
        pass
```

## 📋 Pull Request Process

### Before Submitting
1. Ensure your code follows the coding standards
2. Write or update tests for your changes
3. Update documentation if needed
4. Test your changes thoroughly
5. Check that all tests pass

### Pull Request Template
When creating a pull request, please include:

- **Description**: What changes were made and why
- **Type**: Bug fix, feature, documentation, etc.
- **Testing**: How the changes were tested
- **Screenshots**: If applicable, include screenshots
- **Breaking Changes**: Any breaking changes should be noted

### Review Process
1. Automated tests must pass
2. Code review by maintainers
3. Address any feedback
4. Merge after approval

## 🏗️ Project Architecture

### Django Apps
- **authentication**: User management and profiles
- **common**: Static pages and utilities
- **recommendations**: AI outfit recommendations
- **wardrobe**: Wardrobe management

### Key Components
- **Models**: Database models and relationships
- **Views**: Business logic and request handling
- **Templates**: HTML templates and UI
- **Static Files**: CSS, JavaScript, and images
- **API Integration**: OpenAI and WeatherAPI

### File Organization
```
apps/
├── app_name/
│   ├── models.py      # Database models
│   ├── views.py       # View functions/classes
│   ├── urls.py        # URL patterns
│   ├── forms.py       # Django forms
│   ├── serializers.py # API serializers
│   └── tests.py       # Test cases
```

## 🐛 Bug Reports

### Before Reporting
1. Check if the issue already exists
2. Try to reproduce the issue
3. Check the latest version
4. Gather relevant information

### Bug Report Template
```markdown
**Bug Description**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: [e.g. Windows 10]
- Python Version: [e.g. 3.13]
- Django Version: [e.g. 5.2.6]

**Additional Context**
Any other context about the problem.
```

## ✨ Feature Requests

### Before Requesting
1. Check if the feature already exists
2. Consider if it fits the project's scope
3. Think about implementation complexity
4. Consider user impact

### Feature Request Template
```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Problem Statement**
What problem does this feature solve?

**Proposed Solution**
How would you like this feature to work?

**Alternatives Considered**
What other solutions have you considered?

**Additional Context**
Any other context or screenshots about the feature request.
```

## 📚 Documentation

### Code Documentation
- Add docstrings to functions and classes
- Use clear, descriptive comments
- Document complex algorithms
- Include examples where helpful

### User Documentation
- Update README.md for significant changes
- Add setup instructions for new features
- Document configuration options
- Include troubleshooting guides

## 🔒 Security

### Security Considerations
- Never commit API keys or secrets
- Use environment variables for sensitive data
- Validate all user inputs
- Use Django's built-in security features
- Report security vulnerabilities privately

### Reporting Security Issues
If you discover a security vulnerability, please:
1. Do not open a public issue
2. Email security@aistylist.com
3. Include detailed information
4. Allow time for response before disclosure

## 🎯 Areas for Contribution

### High Priority
- Mobile app development
- Performance optimization
- Additional AI features
- Enhanced user interface
- Comprehensive test coverage

### Medium Priority
- Documentation improvements
- Code refactoring
- Additional API integrations
- Advanced analytics
- Social features

### Low Priority
- Additional themes
- Localization support
- Advanced customization
- Integration with fashion retailers

## 📞 Getting Help

### Community Support
- GitHub Discussions for questions
- GitHub Issues for bug reports
- Email: aistylist@support.com

### Development Resources
- Django Documentation: https://docs.djangoproject.com/
- Bootstrap Documentation: https://getbootstrap.com/docs/
- OpenAI API Documentation: https://platform.openai.com/docs/

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation
- Annual contributor appreciation

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AI-Powered Personal Stylist! Your contributions help make this project better for everyone. 🎉
