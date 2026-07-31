---
name: Pull Request
about: Standard pull request template
title: ''
labels: ''
assignees: ''
---

## Description

Brief description of the changes in this pull request.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Related Issues

Closes #(issue number)
Related to #(issue number)

## Changes Made

### Core Changes
- [ ] Modified core functionality
- [ ] Added new features
- [ ] Fixed bugs
- [ ] Improved performance

### Documentation
- [ ] Updated README.md
- [ ] Updated CHANGELOG.md
- [ ] Updated API documentation
- [ ] Added code comments/docstrings

### Testing
- [ ] Added unit tests
- [ ] Added integration tests
- [ ] Updated existing tests
- [ ] All tests pass

## Testing

### Manual Testing
Describe the manual testing performed:

- [ ] Tested on [OS]
- [ ] Tested with Python version [X.X]
- [ ] Verified API endpoints
- [ ] Verified benchmarks

### Automated Testing
```bash
# Commands to run tests
pytest tests/
python test_lamb.py
```

### Test Results
- Unit tests: [ ] Pass / [ ] Fail
- Integration tests: [ ] Pass / [ ] Fail
- Smoke tests: [ ] Pass / [ ] Fail
- Benchmarks: [ ] Pass / [ ] Fail

## Performance Impact

- [ ] No performance impact
- [ ] Performance improved (describe below)
- [ ] Performance degraded (describe below)

**Performance Details:**
- Throughput: [before] → [after] RPS
- Latency: [before] → [after] ms
- Memory: [before] → [after] MB

## Breaking Changes

- [ ] No breaking changes
- [ ] Breaking changes (describe below)

**Migration Required:**
- [ ] No migration required
- [ ] Migration required (describe steps)

## Checklist

- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published in downstream modules

## Additional Notes

Add any additional information that reviewers should know:

## Screenshots (if applicable)

Add screenshots to help explain your changes:

## Deployment Notes

Any special instructions for deployment:

- [ ] Database migration required
- [ ] Configuration changes required
- [ ] Environment variables required
- [ ] Service restart required
