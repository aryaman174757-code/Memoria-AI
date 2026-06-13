# MEMORIA AI - System Architecture Overview

## Version: 1.0
## Date: June 13, 2026
## Status: Final

---

## Executive Summary

MEMORIA AI follows a microservices-oriented architecture with clean architecture principles, domain-driven design, and event-driven patterns. The system is designed for scalability, maintainability, and extensibility, supporting millions of users with high availability and performance.

---

## Architectural Principles

### 1. Clean Architecture
- Separation of concerns between layers
- Dependency inversion
- Business logic independence from frameworks
- Testability at all layers

### 2. Domain-Driven Design (DDD)
- Bounded contexts for each domain
- Ubiquitous language
- Domain models as core
- Repository pattern for data access

### 3. Hexagonal Architecture
- Ports and adapters pattern
- Core business logic isolated
- External dependencies as adapters
- Testable core without infrastructure

### 4. CQRS (Command Query Responsibility Segregation)
- Separate read and write models
- Optimized for each operation
- Event sourcing for write model
- Materialized views for read model

### 5. Event-Driven Architecture
- Asynchronous communication
- Event sourcing for audit trail
- Eventual consistency
- Loose coupling between services

### 6. SOLID Principles
- Single Responsibility
- Open/Closed
- Liskov Substitution
- Interface Segregation
- Dependency Inversion

### 7. Microservice-Ready Design
- Service boundaries aligned with domains
- Independent deployment
- Horizontal scaling
- Fault isolation

---

## System Layers

### Presentation Layer
**Responsibilities:**
- User interface rendering
- API gateway functionality
- Request routing
- Authentication validation
- Response formatting

**Technologies:**
- Next.js (React)
- TypeScript
- Tailwind CSS
- Shadcn UI
- Framer Motion

### Application Layer
**Responsibilities:**
- Use case orchestration
- Business workflow coordination
- Transaction management
- Input validation
- Output transformation

**Technologies:**
- FastAPI
- Python
- Pydantic
- Service pattern

### Domain Layer
**Responsibilities:**
- Core business logic
- Domain models
- Business rules
- Domain events
- Value objects

**Technologies:**
- Python
- Domain models
- Business rules engine

### Infrastructure Layer
**Responsibilities:**
- Data persistence
- External service integration
- File storage
- Caching
- Messaging

**Technologies:**
- SQLAlchemy
- PostgreSQL
- Redis
- Celery
- S3-compatible storage

---

## Core Services

### 1. Authentication Service
**Purpose:** User identity and access management

**Responsibilities:**
- User registration and login
- JWT token generation and validation
- OAuth integration (Google, GitHub, Microsoft)
- Two-factor authentication
- Session management
- Password reset
- Role-based access control

**Key Endpoints:**
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- POST /api/v1/auth/logout
- POST /api/v1/auth/refresh
- POST /api/v1/auth/verify-2fa
- POST /api/v1/auth/oauth/{provider}
- POST /api/v1/auth/reset-password

### 2. User Management Service
**Purpose:** User profile and preferences management

**Responsibilities:**
- Profile CRUD operations
- Preference management
- Theme customization
- Notification settings
- API key management
- Workspace/team management

**Key Endpoints:**
- GET /api/v1/users/me
- PUT /api/v1/users/me
- GET /api/v1/users/{user_id}
- PUT /api/v1/users/{user_id}/preferences
- GET /api/v1/users/{user_id}/workspaces

### 3. Notes Service
**Purpose:** Rich text and markdown note management

**Responsibilities:**
- Note CRUD operations
- Version history
- Tag management
- Folder organization
- Collection management
- AI-generated titles and tags
- Note linking and backlinks
- Real-time collaboration

**Key Endpoints:**
- GET /api/v1/notes
- POST /api/v1/notes
- GET /api/v1/notes/{note_id}
- PUT /api/v1/notes/{note_id}
- DELETE /api/v1/notes/{note_id}
- GET /api/v1/notes/{note_id}/versions
- POST /api/v1/notes/{note_id}/ai-generate-title
- POST /api/v1/notes/{note_id}/ai-generate-tags

### 4. Documents Service
**Purpose:** Document upload, parsing, and management

**Responsibilities:**
- Document upload (PDF, DOCX, TXT, CSV, etc.)
- Document parsing and extraction
- OCR processing
- Document indexing
- Version management
- Document sharing
- Thumbnail generation

**Key Endpoints:**
- POST /api/v1/documents/upload
- GET /api/v1/documents
- GET /api/v1/documents/{document_id}
- DELETE /api/v1/documents/{document_id}
- GET /api/v1/documents/{document_id}/content
- POST /api/v1/documents/{document_id}/share

### 5. Knowledge Service
**Purpose:** Knowledge graph construction and management

**Responsibilities:**
- Entity extraction
- Relationship mapping
- Knowledge graph construction
- Graph visualization
- Graph queries
- Relationship strength scoring
- Temporal tracking

**Key Endpoints:**
- GET /api/v1/knowledge/graph
- POST /api/v1/knowledge/entities
- GET /api/v1/knowledge/relationships
- POST /api/v1/knowledge/query
- GET /api/v1/knowledge/visualize

### 6. AI Service
**Purpose:** AI model integration and orchestration

**Responsibilities:**
- Multi-LLM provider management
- Model routing and selection
- Fallback handling
- Cost optimization
- Rate limiting
- Response caching
- Prompt template management
- Fine-tuning support

**Key Endpoints:**
- POST /api/v1/ai/chat
- POST /api/v1/ai/completions
- POST /api/v1/ai/embeddings
- GET /api/v1/ai/models
- POST /api/v1/ai/prompts

### 7. Memory Service
**Purpose:** Multi-type memory storage and retrieval

**Responsibilities:**
- Short-term memory
- Long-term memory
- Semantic memory
- Episodic memory
- Procedural memory
- Conversation memory
- Memory consolidation
- Memory retrieval

**Key Endpoints:**
- POST /api/v1/memory/store
- GET /api/v1/memory/retrieve
- POST /api/v1/memory/consolidate
- GET /api/v1/memory/{type}
- DELETE /api/v1/memory/{memory_id}

### 8. Search Service
**Purpose:** Unified search across all content

**Responsibilities:**
- Global search
- Semantic search
- Hybrid search (keyword + vector)
- Natural language queries
- Cross-document search
- Search filters and faceting
- Search analytics

**Key Endpoints:**
- GET /api/v1/search
- POST /api/v1/search/semantic
- POST /api/v1/search/hybrid
- GET /api/v1/search/suggestions
- POST /api/v1/search/save

### 9. Analytics Service
**Purpose:** User activity and performance analytics

**Responsibilities:**
- Knowledge growth tracking
- Learning progress
- Skill development
- Activity trends
- Study analytics
- Productivity metrics
- Custom dashboards

**Key Endpoints:**
- GET /api/v1/analytics/overview
- GET /api/v1/analytics/knowledge-growth
- GET /api/v1/analytics/learning-progress
- GET /api/v1/analytics/productivity
- POST /api/v1/analytics/custom-query

### 10. Learning Service
**Purpose:** Learning tracking and management

**Responsibilities:**
- Topic tracking
- Learning session logging
- Progress tracking
- Weakness detection
- Revision planning
- Spaced repetition
- Quiz generation
- Flashcard management

**Key Endpoints:**
- POST /api/v1/learning/sessions
- GET /api/v1/learning/topics
- POST /api/v1/learning/revision-plan
- POST /api/v1/learning/quiz
- GET /api/v1/learning/weaknesses

### 11. Study Assistant
**Purpose:** Exam and study preparation

**Responsibilities:**
- Exam preparation tracking
- Mock test generation
- Performance analysis
- Study schedule generation
- Resource recommendations
- Achievement tracking

**Key Endpoints:**
- POST /api/v1/study/exam-prep
- POST /api/v1/study/mock-test
- GET /api/v1/study/performance
- POST /api/v1/study/schedule

### 12. Career Assistant
**Purpose:** Career development and job search

**Responsibilities:**
- Resume analysis
- ATS optimization
- Skill gap detection
- Roadmap generation
- Mock interviews
- Job application tracking
- Cover letter generation

**Key Endpoints:**
- POST /api/v1/career/resume-analysis
- POST /api/v1/career/ats-optimize
- GET /api/v1/career/skill-gaps
- POST /api/v1/career/roadmap
- POST /api/v1/career/mock-interview

### 13. Project Assistant
**Purpose:** Project management and tracking

**Responsibilities:**
- Project creation and management
- Milestone tracking
- Task generation
- AI suggestions
- Risk analysis
- Progress tracking
- GitHub integration

**Key Endpoints:**
- POST /api/v1/projects
- GET /api/v1/projects
- GET /api/v1/projects/{project_id}
- POST /api/v1/projects/{project_id}/tasks
- POST /api/v1/projects/{project_id}/analyze

### 14. Task Manager
**Purpose:** Task and todo management

**Responsibilities:**
- Task CRUD operations
- Prioritization
- Due dates and reminders
- Dependencies
- Subtasks
- Labels and assignments
- Recurring tasks

**Key Endpoints:**
- GET /api/v1/tasks
- POST /api/v1/tasks
- GET /api/v1/tasks/{task_id}
- PUT /api/v1/tasks/{task_id}
- DELETE /api/v1/tasks/{task_id}
- POST /api/v1/tasks/{task_id}/complete

### 15. Calendar Service
**Purpose:** Calendar and event management

**Responsibilities:**
- Event creation and management
- Calendar integration
- Recurring events
- Reminders
- Calendar views
- Event sharing

**Key Endpoints:**
- GET /api/v1/calendar/events
- POST /api/v1/calendar/events
- GET /api/v1/calendar/events/{event_id}
- PUT /api/v1/calendar/events/{event_id}
- DELETE /api/v1/calendar/events/{event_id}

### 16. Notification Service
**Purpose**: Multi-channel notification delivery

**Responsibilities:**
- In-app notifications
- Email notifications
- Push notifications
- SMS notifications
- Notification preferences
- Scheduling
- History

**Key Endpoints:**
- GET /api/v1/notifications
- POST /api/v1/notifications/mark-read
- PUT /api/v1/notifications/preferences
- POST /api/v1/notifications/send

### 17. Agent Service
**Purpose**: AI agent creation and management

**Responsibilities:**
- Agent creation and configuration
- Agent execution
- Agent collaboration
- Agent monitoring
- Agent logging
- Custom agent behaviors

**Key Endpoints:**
- POST /api/v1/agents
- GET /api/v1/agents
- POST /api/v1/agents/{agent_id}/execute
- GET /api/v1/agents/{agent_id}/logs

### 18. Recommendation Service
**Purpose**: Personalized recommendations

**Responsibilities:**
- Content recommendations
- Learning path recommendations
- Resource recommendations
- Task recommendations
- Goal recommendations
- Feedback collection

**Key Endpoints:**
- GET /api/v1/recommendations
- POST /api/v1/recommendations/feedback
- GET /api/v1/recommendations/{type}

---

## Data Architecture

### Primary Database: PostgreSQL
**Purpose:** Relational data storage

**Data Types:**
- User data
- Notes and documents
- Tasks and projects
- Calendar events
- Learning sessions
- Analytics data
- Audit logs

### Vector Database: ChromaDB
**Purpose:** Semantic search and embeddings

**Data Types:**
- Document embeddings
- Note embeddings
- Query embeddings
- Memory embeddings

### Cache: Redis
**Purpose:** High-speed caching

**Cached Data:**
- Session data
- API responses
- User preferences
- Frequently accessed notes
- Search results

### Message Queue: Celery + RabbitMQ
**Purpose:** Asynchronous task processing

**Task Types:**
- Document indexing
- AI processing
- Email sending
- Notification delivery
- Analytics aggregation
- Background jobs

### Object Storage: S3-compatible
**Purpose:** File storage

**Stored Files:**
- Uploaded documents
- Generated thumbnails
- Export files
- User avatars
- Attachments

---

## Integration Architecture

### External Integrations

**AI Providers:**
- OpenAI API
- Anthropic API
- Google Gemini API

**OAuth Providers:**
- Google OAuth
- GitHub OAuth
- Microsoft OAuth

**Calendar:**
- Google Calendar API
- Microsoft Outlook API

**Version Control:**
- GitHub API
- GitLab API (future)

**Email:**
- SendGrid
- AWS SES

**Storage:**
- AWS S3
- Google Cloud Storage
- Azure Blob Storage

---

## Security Architecture

### Authentication Flow
1. User submits credentials
2. Authentication service validates
3. JWT access token generated
4. Refresh token stored securely
5. Tokens returned to client
6. Client includes access token in requests
7. API gateway validates token
8. Request forwarded to service

### Authorization Flow
1. Request authenticated
2. User roles extracted from token
3. Service checks permissions
4. Resource access granted/denied
5. Audit log updated

### Data Encryption
- TLS 1.3 for all connections
- AES-256 for data at rest
- Encrypted fields in database
- Secure key management

### Rate Limiting
- Per-user rate limits
- Per-endpoint rate limits
- IP-based rate limiting
- Distributed rate limiting with Redis

---

## Scalability Strategy

### Horizontal Scaling
- Stateless services
- Load balancing
- Auto-scaling groups
- Container orchestration

### Database Scaling
- Read replicas
- Connection pooling
- Query optimization
- Indexing strategy
- Future sharding

### Caching Strategy
- Multi-level caching
- Cache invalidation
- Cache warming
- CDN for static assets

### Async Processing
- Message queues
- Background workers
- Batch processing
- Event-driven updates

---

## High-Level Data Flow

### Note Creation Flow
1. User creates note via UI
2. Frontend sends POST request
3. API gateway validates auth
4. Notes service processes request
5. Note stored in PostgreSQL
6. Event published to message queue
7. AI service generates embeddings
8. Embeddings stored in ChromaDB
9. Knowledge service extracts entities
10. Entities stored in knowledge graph
11. Response returned to client

### Document Upload Flow
1. User uploads document
2. File stored in S3
3. Document service creates record
4. Document parsing job queued
5. Worker extracts text/content
6. OCR if needed
7. Text chunked for embeddings
8. Embeddings generated and stored
9. Document indexed for search
10. User notified of completion

### Search Flow
1. User submits search query
2. Query embedding generated
3. Hybrid search executed:
   - Keyword search in PostgreSQL
   - Vector search in ChromaDB
4. Results reranked
5. Context compressed
6. Results returned to client
7. Search analytics logged

### AI Chat Flow
1. User sends message
2. Conversation context retrieved
3. Relevant documents retrieved via RAG
4. Context assembled
5. Prompt constructed
6. LLM provider selected
7. Request sent to LLM
8. Response processed
9. Citations generated
10. Response returned to client
11. Conversation memory updated

---

## Monitoring & Observability

### Metrics Collection
- Application metrics (Prometheus)
- Business metrics (custom)
- Infrastructure metrics (CloudWatch)
- User behavior metrics (analytics)

### Logging
- Structured logging (JSON)
- Log aggregation (ELK stack)
- Log levels (DEBUG, INFO, WARN, ERROR)
- Sensitive data redaction

### Tracing
- Distributed tracing (OpenTelemetry)
- Request tracing across services
- Performance monitoring
- Error tracking (Sentry)

### Alerting
- Metric-based alerts
- Log-based alerts
- Error rate alerts
- Performance degradation alerts

---

## Disaster Recovery

### Backup Strategy
- Database backups every 6 hours
- Incremental backups every hour
- Backups stored in multiple regions
- 30-day retention
- Point-in-time recovery

### High Availability
- Multi-region deployment
- Load balancing
- Auto-failover
- Health checks
- Circuit breakers

### Incident Response
- Runbooks for common incidents
- On-call rotation
- Incident communication
- Post-incident reviews

---

## Technology Stack Summary

### Frontend
- **Framework:** Next.js 14 (React 18)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Components:** Shadcn UI
- **Animations:** Framer Motion
- **State:** Zustand
- **Data Fetching:** React Query
- **Forms:** React Hook Form + Zod

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.11+
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **Async:** asyncio
- **Tasks:** Celery

### Database
- **Primary:** PostgreSQL 15+
- **Vector:** ChromaDB
- **Cache:** Redis 7+
- **Queue:** RabbitMQ

### AI/ML
- **Frameworks:** LangChain, LangGraph, LlamaIndex
- **Providers:** OpenAI, Anthropic, Google
- **Embeddings:** OpenAI, Cohere

### DevOps
- **Containers:** Docker
- **Orchestration:** Kubernetes (future)
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus + Grafana
- **Logging:** ELK Stack
- **Tracing:** OpenTelemetry

### Deployment
- **Frontend:** Vercel
- **Backend:** Render
- **Database:** Render PostgreSQL
- **Storage:** AWS S3
- **CDN:** Cloudflare

---

## Architecture Decision Records (ADRs)

### ADR-001: Microservices vs Monolith
**Decision:** Start with modular monolith, design for microservices

**Rationale:**
- Faster initial development
- Lower operational complexity
- Easier testing
- Can split into microservices later

### ADR-002: PostgreSQL vs MongoDB
**Decision:** PostgreSQL as primary database

**Rationale:**
- ACID compliance
- Strong relational capabilities
- JSON support for flexibility
- Mature tooling
- Better for complex queries

### ADR-003: ChromaDB vs Pinecone
**Decision:** ChromaDB initially with abstraction for others

**Rationale:**
- Open source and self-hosted
- No vendor lock-in
- Good performance for initial scale
- Can migrate to Pinecone/Weaviate later

### ADR-004: FastAPI vs Django
**Decision:** FastAPI for backend

**Rationale:**
- Native async support
- Better performance
- Automatic API documentation
- Modern Python patterns
- Type safety

### ADR-005: Next.js vs React SPA
**Decision:** Next.js for frontend

**Rationale:**
- Server-side rendering
- Better SEO
- API routes for BFF
- Built-in optimization
- Great developer experience

---

**Document Status:** Approved
**Next Review:** Q4 2026
**Owner:** Architecture Team
