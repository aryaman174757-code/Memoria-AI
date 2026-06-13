# MEMORIA AI - Project Folder Structure

## Version: 1.0
## Date: June 13, 2026
## Status: Final

---

## Executive Summary

This document defines the complete project folder structure for MEMORIA AI, following best practices for monorepo organization, separation of concerns, and scalability. The structure supports both development and production environments.

---

## Root Structure

```
memoria-ai/
├── README.md
├── LICENSE
├── .gitignore
├── .dockerignore
├── .env.example
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── Makefile
├── pyproject.toml
├── package.json
├── turbo.json
├── .github/
│   └── workflows/
├── docs/
├── apps/
│   ├── frontend/
│   ├── backend/
│   ├── mobile/
│   └── desktop/
├── packages/
│   ├── shared/
│   ├── ui/
│   ├── types/
│   └── config/
├── scripts/
├── tests/
└── deployments/
```

---

## Detailed Structure

### Root Configuration Files

```
memoria-ai/
├── README.md                    # Project documentation
├── LICENSE                      # MIT License
├── .gitignore                   # Git ignore rules
├── .dockerignore                # Docker ignore rules
├── .env.example                 # Environment variables template
├── docker-compose.yml           # Production Docker Compose
├── docker-compose.dev.yml       # Development Docker Compose
├── docker-compose.prod.yml      # Production Docker Compose override
├── Makefile                     # Common commands
├── pyproject.toml               # Python project configuration
├── package.json                 # Root package.json for monorepo
├── turbo.json                   # Turborepo configuration
├── .prettierrc                  # Prettier configuration
├── .eslintrc.js                 # ESLint configuration
├── .pre-commit-config.yaml      # Pre-commit hooks
└── .editorconfig                # Editor configuration
```

### GitHub Workflows

```
.github/
└── workflows/
    ├── ci.yml                   # Continuous Integration
    ├── cd.yml                   # Continuous Deployment
    ├── security.yml             # Security scanning
    ├── test.yml                 # Test automation
    ├── lint.yml                 # Linting checks
    └── dependency-review.yml    # Dependency review
```

### Documentation

```
docs/
├── architecture/               # Architecture documents
│   ├── 01-PRD.md
│   ├── 02-System-Architecture-Overview.md
│   ├── 03-High-Level-Architecture.md
│   ├── 04-Low-Level-Architecture.md
│   ├── 05-Database-Schema.md
│   ├── 06-Project-Folder-Structure.md
│   ├── 07-REST-API-Specification.md
│   ├── 08-Event-Driven-Architecture.md
│   ├── 09-AI-Agent-Architecture.md
│   ├── 10-RAG-System-Architecture.md
│   ├── 11-Security-Architecture.md
│   ├── 12-DevOps-CI-CD-Architecture.md
│   ├── 13-Deployment-Architecture.md
│   ├── 14-Development-Roadmap.md
│   └── 15-Sprint-Planning.md
├── api/                        # API documentation
│   ├── openapi.yaml
│   └── postman_collection.json
├── user-guides/                # User guides
│   ├── getting-started.md
│   ├── notes.md
│   ├── documents.md
│   ├── search.md
│   ├── learning.md
│   ├── career.md
│   └── projects.md
├── developer-guides/           # Developer guides
│   ├── setup.md
│   ├── contributing.md
│   ├── testing.md
│   ├── deployment.md
│   └── troubleshooting.md
└── diagrams/                   # Architecture diagrams
    ├── system-architecture.drawio
    ├── data-flow.drawio
    └── deployment.drawio
```

### Frontend Application (Next.js)

```
apps/frontend/
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
├── postcss.config.js
├── .eslintrc.json
├── .prettierrc
├── public/
│   ├── favicon.ico
│   ├── logo.svg
│   ├── robots.txt
│   └── sitemap.xml
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   ├── register/
│   │   │   │   └── page.tsx
│   │   │   └── forgot-password/
│   │   │       └── page.tsx
│   │   ├── dashboard/
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── notes/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── documents/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── search/
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── learning/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── topics/
│   │   │   │   └── page.tsx
│   │   │   ├── flashcards/
│   │   │   │   └── page.tsx
│   │   │   └── quizzes/
│   │   │       └── page.tsx
│   │   ├── career/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── resume/
│   │   │   │   └── page.tsx
│   │   │   ├── jobs/
│   │   │   │   └── page.tsx
│   │   │   └── interviews/
│   │   │       └── page.tsx
│   │   ├── projects/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── tasks/
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── calendar/
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── agents/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── analytics/
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   └── settings/
│   │       ├── layout.tsx
│   │       ├── profile/
│   │       │   └── page.tsx
│   │       ├── preferences/
│   │       │   └── page.tsx
│   │       ├── security/
│   │       │   └── page.tsx
│   │       └── billing/
│   │           └── page.tsx
│   ├── components/              # React components
│   │   ├── ui/                  # Shadcn UI components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── select.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── table.tsx
│   │   │   ├── toast.tsx
│   │   │   └── ...
│   │   ├── layout/              # Layout components
│   │   │   ├── header.tsx
│   │   │   ├── sidebar.tsx
│   │   │   ├── footer.tsx
│   │   │   └── navigation.tsx
│   │   ├── notes/              # Note components
│   │   │   ├── note-editor.tsx
│   │   │   ├── note-card.tsx
│   │   │   ├── note-list.tsx
│   │   │   └── folder-tree.tsx
│   │   ├── documents/          # Document components
│   │   │   ├── document-uploader.tsx
│   │   │   ├── document-card.tsx
│   │   │   └── document-viewer.tsx
│   │   ├── search/             # Search components
│   │   │   ├── search-bar.tsx
│   │   │   ├── search-results.tsx
│   │   │   └── search-filters.tsx
│   │   ├── learning/           # Learning components
│   │   │   ├── topic-card.tsx
│   │   │   ├── flashcard.tsx
│   │   │   └── quiz.tsx
│   │   ├── career/             # Career components
│   │   │   ├── resume-uploader.tsx
│   │   │   ├── job-card.tsx
│   │   │   └── skill-badge.tsx
│   │   ├── projects/           # Project components
│   │   │   ├── project-card.tsx
│   │   │   ├── milestone-list.tsx
│   │   │   └── task-board.tsx
│   │   ├── tasks/              # Task components
│   │   │   ├── task-item.tsx
│   │   │   ├── task-form.tsx
│   │   │   └── task-calendar.tsx
│   │   ├── calendar/           # Calendar components
│   │   │   ├── calendar-view.tsx
│   │   │   ├── event-form.tsx
│   │   │   └── event-card.tsx
│   │   ├── agents/             # Agent components
│   │   │   ├── agent-card.tsx
│   │   │   ├── agent-chat.tsx
│   │   │   └── agent-config.tsx
│   │   └── analytics/          # Analytics components
│   │       ├── charts/
│   │       │   ├── knowledge-growth.tsx
│   │       │   ├── learning-progress.tsx
│   │       │   └── activity-trends.tsx
│   │       └── dashboard.tsx
│   ├── lib/                    # Utility functions
│   │   ├── api.ts              # API client
│   │   ├── auth.ts             # Authentication utilities
│   │   ├── utils.ts            # General utilities
│   │   └── constants.ts       # Constants
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useNotes.ts
│   │   ├── useDocuments.ts
│   │   ├── useSearch.ts
│   │   ├── useLearning.ts
│   │   ├── useCareer.ts
│   │   ├── useProjects.ts
│   │   ├── useTasks.ts
│   │   ├── useCalendar.ts
│   │   ├── useAgents.ts
│   │   └── useAnalytics.ts
│   ├── store/                  # State management (Zustand)
│   │   ├── authStore.ts
│   │   ├── uiStore.ts
│   │   ├── notesStore.ts
│   │   ├── documentsStore.ts
│   │   └── userStore.ts
│   ├── types/                  # TypeScript types
│   │   ├── auth.ts
│   │   ├── notes.ts
│   │   ├── documents.ts
│   │   ├── learning.ts
│   │   ├── career.ts
│   │   ├── projects.ts
│   │   ├── tasks.ts
│   │   ├── calendar.ts
│   │   ├── agents.ts
│   │   └── analytics.ts
│   └── styles/                 # Global styles
│       └── globals.css
└── tests/                      # Frontend tests
    ├── unit/
    ├── integration/
    └── e2e/
```

### Backend Application (FastAPI)

```
apps/backend/
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── alembic.ini
├── Dockerfile
├── .dockerignore
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── dependencies.py         # Dependency injection
│   ├── middleware.py           # Custom middleware
│   ├── exceptions.py           # Exception handlers
│   ├── security.py             # Security utilities
│   ├── database.py             # Database connection
│   ├── cache.py                # Cache connection
│   ├── queue.py                # Queue connection
│   ├── storage.py              # Storage connection
│   ├── auth/                  # Authentication service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── users/                 # User management service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── notes/                 # Notes service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── documents/             # Documents service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── parsers/
│   │   │   ├── __init__.py
│   │   │   ├── pdf.py
│   │   │   ├── docx.py
│   │   │   ├── txt.py
│   │   │   ├── csv.py
│   │   │   ├── xlsx.py
│   │   │   └── image.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── search/                # Search service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── learning/              # Learning service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── career/                # Career service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── projects/              # Projects service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── integrations/
│   │   │   ├── __init__.py
│   │   │   └── github.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── tasks/                 # Tasks service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── calendar/              # Calendar service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── integrations/
│   │   │   ├── __init__.py
│   │   │   ├── google.py
│   │   │   └── outlook.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── agents/                # Agents service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── agent_types/
│   │   │   ├── __init__.py
│   │   │   ├── study_agent.py
│   │   │   ├── research_agent.py
│   │   │   ├── career_agent.py
│   │   │   ├── coding_agent.py
│   │   │   ├── document_agent.py
│   │   │   ├── planning_agent.py
│   │   │   ├── project_agent.py
│   │   │   └── task_agent.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── analytics/             # Analytics service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── knowledge/             # Knowledge service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── notifications/         # Notifications service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── channels/
│   │   │   ├── __init__.py
│   │   │   ├── email.py
│   │   │   ├── push.py
│   │   │   └── sms.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── ai/                    # AI service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── services.py
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── openai.py
│   │   │   ├── anthropic.py
│   │   │   └── google.py
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── retriever.py
│   │   │   ├── reranker.py
│   │   │   └── context_compressor.py
│   │   ├── embeddings/
│   │   │   ├── __init__.py
│   │   │   └── generator.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── vector_db/             # Vector database layer
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── chroma.py
│   │   ├── pinecone.py
│   │   ├── weaviate.py
│   │   └── qdrant.py
│   ├── memory/                # Memory service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── memory_types/
│   │   │   ├── __init__.py
│   │   │   ├── short_term.py
│   │   │   ├── long_term.py
│   │   │   ├── semantic.py
│   │   │   ├── episodic.py
│   │   │   └── procedural.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── recommendations/       # Recommendations service
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── schemas.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── publisher.py
│   │       └── subscriber.py
│   ├── core/                  # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── cache.py
│   │   ├── queue.py
│   │   ├── storage.py
│   │   ├── security.py
│   │   ├── exceptions.py
│   │   └── constants.py
│   ├── models/                # Shared models
│   │   ├── __init__.py
│   │   └── base.py
│   ├── repositories/          # Base repository
│   │   ├── __init__.py
│   │   └── base.py
│   ├── schemas/               # Shared schemas
│   │   ├── __init__.py
│   │   └── common.py
│   ├── tasks/                 # Celery tasks
│   │   ├── __init__.py
│   │   ├── document_tasks.py
│   │   ├── embedding_tasks.py
│   │   ├── notification_tasks.py
│   │   ├── analytics_tasks.py
│   │   └── agent_tasks.py
│   └── websocket/             # WebSocket handlers
│       ├── __init__.py
│       ├── manager.py
│       └── handlers.py
├── alembic/                   # Database migrations
│   ├── versions/
│   │   ├── 001_initial.py
│   │   ├── 002_auth_tables.py
│   │   ├── 003_content_tables.py
│   │   ├── 004_learning_tables.py
│   │   ├── 005_career_tables.py
│   │   ├── 006_projects_tables.py
│   │   ├── 007_tasks_tables.py
│   │   ├── 008_calendar_tables.py
│   │   ├── 009_agents_tables.py
│   │   ├── 010_analytics_tables.py
│   │   └── ...
│   ├── env.py
│   └── script.py.mako
└── tests/                     # Backend tests
    ├── unit/
    ├── integration/
    └── e2e/
```

### Mobile Application (React Native)

```
apps/mobile/
├── package.json
├── tsconfig.json
├── babel.config.js
├── metro.config.js
├── app.json
├── .eslintrc.js
├── .prettierrc
├── ios/
│   ├── Podfile
│   ├── MemoriaAI/
│   │   ├── AppDelegate.swift
│   │   ├── Info.plist
│   │   └── ...
│   └── MemoriaAITests/
├── android/
│   ├── app/
│   │   ├── build.gradle
│   │   └── src/
│   │       └── main/
│   │           ├── AndroidManifest.xml
│   │           ├── java/
│   │           └── res/
│   ├── build.gradle
│   ├── gradle.properties
│   └── settings.gradle
└── src/
    ├── __init__.py
    ├── App.tsx
    ├── assets/
    │   ├── images/
    │   └── fonts/
    ├── components/
    │   ├── ui/
    │   ├── notes/
    │   ├── documents/
    │   └── ...
    ├── navigation/
    │   ├── AppNavigator.tsx
    │   ├── AuthNavigator.tsx
    │   └── MainNavigator.tsx
    ├── screens/
    │   ├── auth/
    │   │   ├── LoginScreen.tsx
    │   │   └── RegisterScreen.tsx
    │   ├── notes/
    │   │   ├── NotesListScreen.tsx
    │   │   └── NoteDetailScreen.tsx
    │   └── ...
    ├── services/
    │   ├── api.ts
    │   ├── auth.ts
    │   └── storage.ts
    ├── hooks/
    │   ├── useAuth.ts
    │   └── ...
    ├── store/
    │   └── ...
    ├── types/
    │   └── ...
    └── utils/
        └── ...
```

### Desktop Application (Electron)

```
apps/desktop/
├── package.json
├── tsconfig.json
├── electron-builder.yml
├── .eslintrc.js
├── .prettierrc
├── src/
│   ├── main/
│   │   ├── main.ts
│   │   ├── menu.ts
│   │   ├── window.ts
│   │   └── ipc/
│   │       ├── handlers.ts
│   │       └── channels.ts
│   ├── renderer/
│   │   ├── App.tsx
│   │   ├── components/
│   │   ├── screens/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── store/
│   │   ├── types/
│   │   └── utils/
│   └── shared/
│       └── types.ts
└── resources/
    ├── icons/
    └── images/
```

### Shared Packages

```
packages/
├── shared/                    # Shared utilities
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── constants.ts
│   │   ├── utils.ts
│   │   ├── validators.ts
│   │   └── formatters.ts
│   └── tests/
├── ui/                        # Shared UI components
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── components/
│   │   │   ├── Button/
│   │   │   ├── Input/
│   │   │   ├── Card/
│   │   │   └── ...
│   │   ├── hooks/
│   │   └── utils/
│   └── tests/
├── types/                     # Shared TypeScript types
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── auth.ts
│   │   ├── notes.ts
│   │   ├── documents.ts
│   │   ├── learning.ts
│   │   ├── career.ts
│   │   ├── projects.ts
│   │   ├── tasks.ts
│   │   ├── calendar.ts
│   │   ├── agents.ts
│   │   └── analytics.ts
│   └── tests/
└── config/                    # Shared configuration
    ├── package.json
    ├── tsconfig.json
    ├── eslint.config.js
    ├── prettier.config.js
    └── tailwind.config.js
```

### Scripts

```
scripts/
├── setup.sh                  # Initial setup script
├── dev.sh                     # Development startup
├── build.sh                   # Build script
├── test.sh                    # Test script
├── deploy.sh                  # Deployment script
├── migrate.sh                # Database migration
├── seed.sh                   # Database seeding
└── clean.sh                   # Cleanup script
```

### Tests

```
tests/
├── e2e/                       # End-to-end tests
│   ├── auth.spec.ts
│   ├── notes.spec.ts
│   ├── documents.spec.ts
│   └── ...
├── performance/               # Performance tests
│   ├── load-test.js
│   └── stress-test.js
└── fixtures/                  # Test fixtures
    ├── users.json
    ├── notes.json
    └── documents.json
```

### Deployments

```
deployments/
├── kubernetes/                # Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmaps/
│   ├── secrets/
│   ├── deployments/
│   ├── services/
│   ├── ingress/
│   └── hpa/
├── terraform/                 # Terraform configurations
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── modules/
│   │   ├── vpc/
│   │   ├── rds/
│   │   ├── ecs/
│   │   └── s3/
│   └── environments/
│       ├── dev/
│       ├── staging/
│       └── prod/
├── docker/                    # Docker configurations
│   ├── frontend.Dockerfile
│   ├── backend.Dockerfile
│   ├── nginx.conf
│   └── entrypoint.sh
└── helm/                      # Helm charts
    ├── memoria-ai/
    │   ├── Chart.yaml
    │   ├── values.yaml
    │   ├── values-dev.yaml
    │   ├── values-staging.yaml
    │   └── values-prod.yaml
    └── templates/
```

---

## File Naming Conventions

### Python Files
- Use `snake_case` for module names
- Use `PascalCase` for class names
- Use `snake_case` for function and variable names
- Example: `note_service.py`, `NoteService`, `get_note_by_id`

### TypeScript/JavaScript Files
- Use `kebab-case` for component files
- Use `PascalCase` for component names
- Use `camelCase` for functions and variables
- Example: `note-card.tsx`, `NoteCard`, `getNoteById`

### Configuration Files
- Use `kebab-case` or `snake_case`
- Example: `docker-compose.yml`, `tsconfig.json`

### Documentation Files
- Use `kebab-case` with `.md` extension
- Use numbers for ordering
- Example: `01-prd.md`, `getting-started.md`

---

## Import Conventions

### Python Imports
```python
# Standard library imports
import os
from datetime import datetime

# Third-party imports
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# Local imports
from app.core.config import settings
from app.auth.models import User
from app.auth.repositories import UserRepository
```

### TypeScript Imports
```typescript
// External imports
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';

// Local imports
import { useAuth } from '@/hooks/useAuth';
import { Note } from '@/types/notes';
import { getNotes } from '@/lib/api';
```

---

## Environment Variables

### Development (.env.development)
```env
# Application
APP_NAME=MEMORIA AI
APP_ENV=development
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/memoria_ai_dev

# Redis
REDIS_URL=redis://localhost:6379

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Storage
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET=memoria-ai-dev

# OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...

# Email
SENDGRID_API_KEY=...
EMAIL_FROM=noreply@memoria.ai
```

### Production (.env.production)
```env
# Application
APP_NAME=MEMORIA AI
APP_ENV=production
DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@prod-host:5432/memoria_ai

# Redis
REDIS_URL=redis://prod-host:6379

# RabbitMQ
RABBITMQ_HOST=prod-host
RABBITMQ_PORT=5672
RABBITMQ_USER=prod_user
RABBITMQ_PASSWORD=prod_password

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Storage
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET=memoria-ai-prod

# OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...

# Email
SENDGRID_API_KEY=...
EMAIL_FROM=noreply@memoria.ai
```

---

## Git Workflow

### Branch Naming
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Production hotfixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test updates

### Commit Messages
```
feat(auth): add OAuth login support
fix(notes): resolve markdown rendering issue
docs(readme): update installation instructions
test(api): add integration tests for notes endpoint
refactor(database): optimize query performance
```

---

**Document Status:** Approved
**Next Review:** Q4 2026
**Owner:** Development Team
