# Changelog

All notable changes to StadiumAI will be documented in this file.

## [1.0.0] - 2024-01-15

### Added
- Real-time crowd monitoring with density heatmap
- AI-powered navigation with step-by-step voice guidance
- Live match commentary and statistics
- Multi-language translation (10 languages)
- Incident reporting with photo/GPS attachment
- Staff assignment and status tracking
- Transport integration (routes, schedules, live tracking)
- Sustainability dashboard with waste management
- Accessibility services (hearing, visual, mobility, cognitive)
- Push notifications for match events and incidents
- Anonymous session-based user system
- Staff dashboard with real-time management
- Comprehensive REST API with 27 endpoints

### Security
- CORS configuration with environment-based origins
- Rate limiting per endpoint (20-100 requests/minute)
- Security headers middleware (CSP, X-Frame-Options, etc.)
- Input validation via Pydantic models
- No hardcoded secrets

### Testing
- 163 backend tests with 95.82% code coverage
- 15 frontend tests with Vitest
- Unit, integration, and edge case coverage

### Infrastructure
- GitHub Actions CI/CD pipeline
- Backend: Python 3.12 + FastAPI
- Frontend: React 19 + TypeScript + Vite
- Database: SQLite with SQLAlchemy ORM
- AI: Google Gemini integration
