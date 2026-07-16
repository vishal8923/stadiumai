# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability within StadiumAI, please send an email to the StadiumAI team. All security vulnerabilities will be promptly addressed.

**Please do NOT report security vulnerabilities through public GitHub issues.**

## Security Measures

### Authentication & Authorization
- Anonymous session-based user system (no PII required)
- Staff authentication via session tokens
- No sensitive data stored in client-side storage

### Data Protection
- All API inputs validated via Pydantic models
- SQL injection prevention via SQLAlchemy ORM
- No hardcoded secrets or API keys
- Environment variables for all configuration

### Network Security
- CORS configuration with environment-based origins
- Security headers middleware (CSP, X-Frame-Options, etc.)
- Rate limiting per endpoint (20-100 requests/minute)
- HTTPS enforcement in production

### AI Security
- API keys stored server-side only
- Input sanitization for AI prompts
- No sensitive data in AI requests

## Dependency Management

- Regular dependency updates
- Automated vulnerability scanning
- Lock files for reproducible builds

## Development Practices

- Code review required for all changes
- Automated testing in CI/CD
- Linting and static analysis
- Minimum 75% test coverage

## Contact

For security inquiries, please contact the project maintainers.
