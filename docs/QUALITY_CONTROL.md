# Quality Control Guide
## Agentic AI Classification & Sentiment Analysis System
### DPR RI

**Version:** 1.0  
**Status:** Draft  
**Project:** Agentic AI Klasifikasi AKD & Analisis Sentimen  
**Last Updated:** August 2026

---

# Table of Contents

1. Purpose
2. Scope
3. Quality Standards
4. Quality Objectives
5. Quality Roles
6. Development Workflow
7. Quality Gates
8. Code Quality Standards
9. Functional Quality Control
10. AI Model Quality Control
11. Software Quality Characteristics
12. Security Quality Control
13. Testing Strategy
14. Risk Management
15. Documentation Quality
16. CI/CD Quality Checks
17. Release Checklist
18. Acceptance Criteria
19. Continuous Improvement

---

# 1. Purpose

This document defines the Quality Control (QC) process for the Agentic AI Classification & Sentiment Analysis System.

The objective is to ensure every component of the project satisfies the functional, technical, AI, security, and usability requirements defined in:

- Project Charter
- Product Requirements Document (PRD)
- Software Requirements Specification (SRS)
- Stakeholder Proposal

Quality Control is performed continuously throughout the Software Development Life Cycle (SDLC), not only during final testing.

---

# 2. Scope

This QC Guide applies to every component of the system.

## Backend

- FastAPI
- REST API
- Database Layer

## AI Components

- Analysis Agent
- Trend Agent
- Insight Agent
- Recommendation Agent
- Supervisor Agent

## Infrastructure

- PostgreSQL
- Redis
- Docker
- DigitalOcean

## Dashboard

- Streamlit

## Reports

- Executive Summary PDF

---

# 3. Quality Standards

| Standard | Purpose |
|------------|----------|
| ISO/IEC 25010 | Software Product Quality |
| ISO/IEC 25059 | AI System Quality |
| ISO 19011 | Audit Guidelines |
| ISO/IEC 27001 | Information Security |
| ISO/IEC 27005 | Risk Management |
| PRD | Product Requirements |
| SRS | Functional Requirements |
| Project Charter | Project Governance |

---

# 4. Quality Objectives

The project should achieve the following objectives.

| Objective | Target |
|------------|----------|
| Sentiment Accuracy | ≥ 75% |
| AKD Classification Accuracy | ≥ 70% |
| API Availability | ≥ 95% |
| Dashboard SUS Score | ≥ 68 |
| PDF Generation | < 5 minutes |
| Critical Bugs | 0 before release |

---

# 5. Quality Roles

## Project Lead

Responsible for

- Sprint approval
- Architecture review
- Final release approval

---

## Backend Developer

Responsible for

- API implementation
- Unit testing
- Docker configuration
- Database integration

---

## AI Engineer

Responsible for

- Prompt Engineering
- Model evaluation
- AI accuracy validation

---

## Database Engineer

Responsible for

- Schema validation
- Migration
- Data integrity

---

## System Analyst

Responsible for

- Requirement traceability
- UML consistency
- Documentation
- Test case preparation

---

# 6. Development Workflow

```text
Requirements
    │
    ▼
Architecture Review
    │
    ▼
Development
    │
    ▼
Pull Request
    │
    ▼
Code Review
    │
    ▼
Testing
    │
    ▼
QA Review
    │
    ▼
Deployment
```

Every stage must pass before the next stage begins.

---

# 7. Quality Gates

## Gate 1 — Requirement Review

Checklist

- [ ] PRD completed
- [ ] SRS completed
- [ ] User stories approved
- [ ] Acceptance criteria defined

---

## Gate 2 — Architecture Review

Checklist

- [ ] Database approved
- [ ] Docker architecture approved
- [ ] API design approved
- [ ] Security reviewed
- [ ] Agent workflow reviewed

---

## Gate 3 — Code Review

Checklist

- [ ] Coding standard followed
- [ ] Documentation updated
- [ ] Error handling implemented
- [ ] Logging implemented
- [ ] Unit tests added

---

## Gate 4 — Testing

Checklist

- [ ] Unit Test
- [ ] Integration Test
- [ ] API Test
- [ ] AI Evaluation
- [ ] Database Test

---

## Gate 5 — Deployment

Checklist

- [ ] Docker build successful
- [ ] Database migration completed
- [ ] Environment variables configured
- [ ] Backup completed

---

# 8. Code Quality Standards

## Formatting

Use

- Black
- isort
- Ruff

---

## Naming

Variables

```python
article_title
```

Functions

```python
collect_news()
```

Classes

```python
AnalysisAgent
```

Constants

```python
MAX_RETRY
```

---

## Rules

- No duplicated code
- No hardcoded secrets
- Type hints required
- Modular design
- Small functions
- Proper exception handling

---

# 9. Functional Quality Control

Every Functional Requirement (FR) in the SRS must have a corresponding test case.

| FR | Component | Test |
|------|------------|---------|
| FR-01 | RSS Collection | Verify articles collected |
| FR-02 | Twitter Collection | Verify tweets collected |
| FR-03 | Database | No duplicate entries |
| FR-04 | Sentiment | Positive / Neutral / Negative |
| FR-05 | AKD Classification | Maximum 3 AKDs |
| FR-07 | Trend Detection | Correct Z-score |
| FR-11 | PDF Report | PDF generated successfully |

---

# 10. AI Model Quality Control

## Sentiment Model

Metrics

- Accuracy
- Precision
- Recall
- F1 Score

Target

```
Accuracy ≥ 75%
```

Ground Truth

Manual DPR reports

---

## AKD Classification

Metrics

- Top-1 Accuracy
- Top-3 Accuracy
- Precision
- Recall

Target

```
Top-1 ≥ 70%
```

---

## Recommendation Evaluation

Reviewer evaluates

- Relevance
- Consistency
- Hallucination
- Readability

Scale

1–5

---

# 11. Software Quality Characteristics

## Functional Suitability

Checklist

- All FR implemented
- Output correct
- Business rules followed

---

## Performance

Target

| Component | Target |
|------------|---------|
| API | <2 sec |
| Dashboard | <3 sec |
| PDF | <5 min |

---

## Reliability

Target

```
95% uptime
```

Verify

- Recovery after restart
- Queue recovery
- Retry mechanism

---

## Security

Verify

- Authentication
- Authorization
- HTTPS
- Secret Management
- Audit Logs

---

## Maintainability

Verify

- Modular agents
- Configurable AKD dictionary
- Independent testing

---

## Portability

System must run on

- Docker Desktop
- Ubuntu
- DigitalOcean

---

# 12. Security Quality Control

Checklist

- [ ] API Keys encrypted
- [ ] .env ignored
- [ ] HTTPS enabled
- [ ] Database password protected
- [ ] User roles enforced
- [ ] Audit logs enabled
- [ ] Regular backup

---

# 13. Testing Strategy

## Unit Test

Coverage target

```
≥ 80%
```

---

## Integration Test

Verify

- Database
- Redis
- FastAPI
- AI Agents

---

## API Test

Verify

- Status code
- Response schema
- Error handling

---

## AI Evaluation

Evaluate

- Sentiment accuracy
- AKD accuracy
- Recommendation quality

---

## User Acceptance Testing

Performed by

- Reviewer
- Internship Supervisor
- Analyst

---

# 14. Risk Management

| Risk | Impact | Mitigation |
|--------|----------|------------|
| Gemini unavailable | High | Retry |
| RSS unavailable | Medium | Multiple sources |
| Twitter unavailable | High | RSS fallback |
| Hallucination | Medium | Human Review |
| PostgreSQL failure | High | Daily backup |

---

# 15. Documentation Quality

Every sprint must update

- README
- PRD
- SRS
- API Documentation
- Database Diagram
- UML
- Changelog

---

# 16. CI/CD Quality Checks

GitHub Actions pipeline

```text
Push

↓

Black

↓

isort

↓

Ruff

↓

Pytest

↓

Docker Build

↓

Success
```

Pipeline must pass before merging.

---

# 17. Release Checklist

Before release

- [ ] All stories completed
- [ ] All tests passed
- [ ] Documentation updated
- [ ] Docker image built
- [ ] Database migrated
- [ ] Backup verified
- [ ] Product Owner approval

---

# 18. Acceptance Criteria

The project is accepted if

- Sentiment Accuracy ≥75%
- AKD Accuracy ≥70%
- Dashboard operational
- Executive Summary PDF generated
- No Critical Bugs
- UAT approved
- Documentation complete

---

# 19. Continuous Improvement

After each sprint

Conduct

- Sprint Review
- Retrospective
- Bug Analysis
- AI Performance Review
- Documentation Review

Improvements identified during retrospectives shall be added to the project backlog and prioritized in the next sprint.

---

# Appendix A — Pull Request Checklist

```text
- [ ] Code compiles
- [ ] Unit tests added
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] Logging implemented
- [ ] Error handling complete
- [ ] Docker builds successfully
- [ ] Reviewer approved
```

---

# Appendix B — Sprint Exit Criteria

A sprint is complete only if

- All planned issues are completed
- No Critical defects remain
- CI pipeline passes
- Documentation updated
- Product Owner approves
- Sprint Review completed

---

# Appendix C — Recommended Tools

| Purpose | Tool |
|----------|------|
| Version Control | GitHub |
| Project Management | GitHub Projects |
| CI/CD | GitHub Actions |
| Containerization | Docker |
| Database | PostgreSQL |
| Cache | Redis |
| Dashboard | Streamlit |
| API | FastAPI |
| AI Orchestration | LangGraph |
| LLM | Gemini 2.5 Flash |
| Sentiment Model | IndoBERT |
| Testing | Pytest |
| Documentation | MkDocs / Markdown |