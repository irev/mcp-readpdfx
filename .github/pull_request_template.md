# Pull Request Template

## 📋 Description

Brief description of what this PR does and why it's needed.

Fixes #(issue_number)

## 🔄 Type of Change

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🧪 Test update
- [ ] 🔧 Maintenance/refactoring

## 🧪 Testing

- [ ] Tests pass locally with my changes
- [ ] I have added/updated tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have tested this with multiple MCP clients (if applicable)

### Test Environment
- **OS**: 
- **Python Version**: 
- **MCP Client(s) Tested**: 

## 📝 Changes Made

### Core Changes
- [ ] Modified MCP server core (`src/mcp_server.py`)
- [ ] Updated MCP tools (`src/mcp_tools.py`)
- [ ] Changed MCP types (`src/mcp_types.py`)
- [ ] Updated server runner (`src/mcp_server_runner.py`)

### Configuration Changes
- [ ] Updated configuration files
- [ ] Modified client integration configs
- [ ] Changed environment variables

### Documentation Changes
- [ ] Updated README
- [ ] Updated client integration guides
- [ ] Added/updated code comments
- [ ] Updated API documentation

## 🔧 Configuration Changes

If this PR includes configuration changes, please describe them:

```yaml
# Example configuration changes
```

## 📊 Performance Impact

- [ ] No performance impact
- [ ] Improves performance
- [ ] May impact performance (please describe)

**Performance Test Results** (if applicable):
- Memory usage: 
- Startup time: 
- Processing speed: 

## 🔒 Security Considerations

- [ ] No security implications
- [ ] Security implications have been considered and addressed
- [ ] Security review recommended

**Security Changes** (if applicable):
- Input validation changes
- Authentication/authorization changes
- Data handling changes

## 📱 Client Compatibility

Tested with the following MCP clients:
- [ ] Claude Desktop
- [ ] LM Studio
- [ ] Continue.dev
- [ ] Cursor
- [ ] Custom HTTP client
- [ ] Not applicable

## 🐛 Bug Fix Details

If this is a bug fix, please describe:
- **Root Cause**: 
- **Solution**: 
- **Impact**: 

## ✨ New Feature Details

If this is a new feature, please describe:
- **Feature**: 
- **Use Case**: 
- **API Changes**: 

## 💥 Breaking Changes

If this introduces breaking changes, please describe:
- **What breaks**: 
- **Migration path**: 
- **Deprecation timeline**: 

## 📋 Checklist

### Code Quality
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings

### Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have tested the integration with at least one MCP client

### Documentation
- [ ] I have updated relevant documentation
- [ ] I have updated the CHANGELOG (if applicable)
- [ ] I have updated client integration guides (if applicable)

### Backwards Compatibility
- [ ] This change maintains backwards compatibility
- [ ] Breaking changes are documented and justified
- [ ] Migration guide provided (if needed)

## 📸 Screenshots/Examples

If applicable, add screenshots or examples to help explain your changes:

```python
# Code examples
```

## 🔗 Related Issues/PRs

- Closes #
- Related to #
- Depends on #

## 📝 Additional Notes

Any additional notes, concerns, or context for reviewers:

---

## For Reviewers

### Review Focus Areas
- [ ] Code quality and style
- [ ] Test coverage
- [ ] Documentation completeness
- [ ] Performance impact
- [ ] Security implications
- [ ] Breaking changes
- [ ] Client compatibility

### Testing Checklist
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance testing (if applicable)
- [ ] Security testing (if applicable)