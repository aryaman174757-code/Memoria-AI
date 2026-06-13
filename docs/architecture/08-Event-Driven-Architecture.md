# MEMORIA AI - Event-Driven Architecture

## Version: 1.0
## Date: June 13, 2026
## Status: Final

---

## Executive Summary

This document describes the event-driven architecture of MEMORIA AI, including event design, message brokers, event patterns, and event handling strategies. The system uses an event-driven approach for loose coupling, scalability, and asynchronous processing.

---

## Architecture Overview

### Event-Driven Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Event Producers                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Auth Svc    │  │  Notes Svc   │  │  Docs Svc    │  │  Learning Svc│   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Message Broker (RabbitMQ)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Exchanges   │  │   Queues     │  │  Bindings    │  │  Dead Letter  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Event Consumers                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  AI Svc      │  │  Search Svc  │  │  Analytics   │  │  Notify Svc  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Knowledge   │  │  Vector DB   │  │  Webhooks    │  │  Cache       │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Event Design Principles

### 1. Event Naming Convention
- Use past tense for events that have occurred
- Use domain-specific terminology
- Format: `[Aggregate].[Action]` or `[Domain].[Entity].[Action]`

**Examples:**
- `UserRegistered`
- `NoteCreated`
- `NoteUpdated`
- `DocumentUploaded`
- `DocumentProcessed`
- `LearningSessionCompleted`

### 2. Event Structure
All events follow this structure:

```json
{
  "event_id": "uuid",
  "event_type": "string",
  "event_version": "string",
  "occurred_at": "ISO8601 timestamp",
  "correlation_id": "uuid",
  "causation_id": "uuid",
  "producer": "service_name",
  "data": {},
  "metadata": {}
}
```

### 3. Event Versioning
- Include version in event type
- Maintain backward compatibility
- Use semantic versioning
- Document breaking changes

---

## Event Catalog

### Authentication Events

#### UserRegistered
Emitted when a new user registers.

```json
{
  "event_type": "auth.user.registered",
  "event_version": "1.0.0",
  "data": {
    "user_id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "registration_source": "email"
  }
}
```

**Consumers:**
- Analytics Service (track registrations)
- Notification Service (send welcome email)
- Recommendation Service (initialize recommendations)

#### UserVerified
Emitted when user verifies email.

```json
{
  "event_type": "auth.user.verified",
  "event_version": "1.0.0",
  "data": {
    "user_id": "uuid",
    "email": "user@example.com",
    "verified_at": "2024-01-01T00:00:00Z"
  }
}
```

#### UserLoggedIn
Emitted when user logs in.

```json
{
  "event_type": "auth.user.logged_in",
  "event_version": "1.0.0",
  "data": {
    "user_id": "uuid",
    "email": "user@example.com",
    "login_method": "password",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
  }
}
```

#### PasswordChanged
Emitted when user changes password.

```json
{
  "event_type": "auth.password.changed",
  "event_version": "1.0.0",
  "data": {
    "user_id": "uuid",
    "changed_at": "2024-01-01T00:00:00Z",
    "ip_address": "192.168.1.1"
  }
}
```

---

### Notes Events

#### NoteCreated
Emitted when a note is created.

```json
{
  "event_type": "content.note.created",
  "event_version": "1.0.0",
  "data": {
    "note_id": "uuid",
    "user_id": "uuid",
    "title": "Note Title",
    "note_type": "rich_text",
    "folder_id": "uuid",
    "tags": ["tag1", "tag2"],
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Consumers:**
- AI Service (generate embeddings)
- Knowledge Service (extract entities)
- Search Service (index for search)
- Analytics Service (track note creation)

#### NoteUpdated
Emitted when a note is updated.

```json
{
  "event_type": "content.note.updated",
  "event_version": "1.0.0",
  "data": {
    "note_id": "uuid",
    "user_id": "uuid",
    "title": "Updated Title",
    "content_changed": true,
    "tags_changed": true,
    "updated_at": "2024-01-01T01:00:00Z"
  }
}
```

**Consumers:**
- AI Service (regenerate embeddings if content changed)
- Knowledge Service (update entities if content changed)
- Search Service (update index)
- Analytics Service (track note updates)

#### NoteDeleted
Emitted when a note is deleted.

```json
{
  "event_type": "content.note.deleted",
  "event_version": "1.0.0",
  "data": {
    "note_id": "uuid",
    "user_id": "uuid",
    "deleted_at": "2024-01-01T00:00:00Z"
  }
}
```

**Consumers:**
- Vector Database (remove embeddings)
- Knowledge Service (remove entities)
- Search Service (remove from index)
- Analytics Service (track deletion)

#### NotePinned
Emitted when a note is pinned.

```json
{
  "event_type": "content.note.pinned",
  "event_version": "1.0.0",
  "data": {
    "note_id": "uuid",
    "user_id": "uuid",
    "pinned_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### Documents Events

#### DocumentUploaded
Emitted when a document is uploaded.

```json
{
  "event_type": "content.document.uploaded",
  "event_version": "1.0.0",
  "data": {
    "document_id": "uuid",
    "user_id": "uuid",
    "title": "Document Title",
    "file_name": "document.pdf",
    "file_type": "pdf",
    "file_size": 1024000,
    "uploaded_at": "2024-01-01T00:00:00Z"
  }
}
```

**Consumers:**
- Document Service (trigger processing)
- Analytics Service (track upload)

#### DocumentProcessingStarted
Emitted when document processing starts.

```json
{
  "event_type": "content.document.processing.started",
  "event_version": "1.0.0",
  "data": {
    "document_id": "uuid",
    "user_id": "uuid",
    "processing_type": "extraction",
    "started_at": "2024-01-01T00:00:00Z"
  }
}
```

#### DocumentProcessed
Emitted when document processing completes.

```json
{
  "event_type": "content.document.processed",
  "event_version": "1.0.0",
  "data": {
    "document_id": "uuid",
    "user_id": "uuid",
    "status": "success",
    "extracted_text_length": 5000,
    "chunk_count": 10,
    "ocr_performed": false,
    "processed_at": "2024-01-01T00:05:00Z"
  }
}
```

**Consumers:**
- AI Service (generate embeddings for chunks)
- Search Service (index chunks)
- Knowledge Service (extract entities)
- Notification Service (notify user)

#### DocumentProcessingFailed
Emitted when document processing fails.

```json
{
  "event_type": "content.document.processing.failed",
  "event_version": "1.0.0",
  "data": {
    "document_id": "uuid",
    "user_id": "uuid",
    "error_type": "parsing_error",
    "error_message": "Unable to parse PDF",
    "failed_at": "2024-01-01T00:05:00Z"
  }
}
```

**Consumers:**
- Notification Service (notify user of failure)
- Analytics Service (track failures)

---

### Learning Events

#### LearningSessionStarted
Emitted when a learning session starts.

```json
{
  "event_type": "learning.session.started",
  "event_version": "1.0.0",
  "data": {
    "session_id": "uuid",
    "user_id": "uuid",
    "topic_id": "uuid",
    "started_at": "2024-01-01T00:00:00Z"
  }
}
```

#### LearningSessionCompleted
Emitted when a learning session completes.

```json
{
  "event_type": "learning.session.completed",
  "event_version": "1.0.0",
  "data": {
    "session_id": "uuid",
    "user_id": "uuid",
    "topic_id": "uuid",
    "duration_minutes": 30,
    "notes": "Session notes...",
    "completed_at": "2024-01-01T00:30:00Z"
  }
}
```

**Consumers:**
- Analytics Service (update learning progress)
- Recommendation Service (update recommendations)
- Learning Service (update topic progress)

#### TopicProgressUpdated
Emitted when topic progress changes.

```json
{
  "event_type": "learning.topic.progress.updated",
  "event_version": "1.0.0",
  "data": {
    "user_id": "uuid",
    "topic_id": "uuid",
    "mastery_level": 65.5,
    "total_minutes": 120,
    "session_count": 10,
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Consumers:**
- Analytics Service (track progress)
- Recommendation Service (suggest next topics)
- Study Assistant (update revision plans)

#### FlashcardReviewed
Emitted when a flashcard is reviewed.

```json
{
  "event_type": "learning.flashcard.reviewed",
  "event_version": "1.0.0",
  "data": {
    "flashcard_id": "uuid",
    "user_id": "uuid",
    "quality": 4,
    "next_review_date": "2024-01-02T00:00:00Z",
    "reviewed_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### Career Events

#### ResumeUploaded
Emitted when a resume is uploaded.

```json
{
  "event_type": "career.resume.uploaded",
  "event_version": "1.0.0",
  "data": {
    "resume_id": "uuid",
    "user_id": "uuid",
    "title": "My Resume",
    "uploaded_at": "2024-01-01T00:00:00Z"
  }
}
```

**Consumers:**
- Career Service (trigger analysis)
- Analytics Service (track uploads)

#### ResumeAnalyzed
Emitted when resume analysis completes.

```json
{
  "event_type": "career.resume.analyzed",
  "event_version": "1.0.0",
  "data": {
    "resume_id": "uuid",
    "user_id": "uuid",
    "ats_score": 85.5,
    "skills_extracted": ["Python", "JavaScript"],
    "analyzed_at": "2024-01-01T00:05:00Z"
  }
}
```

**Consumers:**
- Notification Service (notify user)
- Recommendation Service (suggest improvements)

#### JobApplicationCreated
Emitted when a job application is created.

```json
{
  "event_type": "career.job_application.created",
  "event_version": "1.0.0",
  "data": {
    "application_id": "uuid",
    "user_id": "uuid",
    "company_name": "Google",
    "job_title": "Software Engineer",
    "status": "applied",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Consumers:**
- Analytics Service (track applications)
- Career Service (suggest interview prep)

---

### Project Events

#### ProjectCreated
Emitted when a project is created.

```json
{
  "event_type": "project.created",
  "event_version": "1.0.0",
  "data": {
    "project_id": "uuid",
    "user_id": "uuid",
    "name": "Project Name",
    "github_url": "https://github.com/...",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### MilestoneCreated
Emitted when a milestone is created.

```json
{
  "event_type": "project.milestone.created",
  "event_version": "1.0.0",
  "data": {
    "milestone_id": "uuid",
    "project_id": "uuid",
    "user_id": "uuid",
    "name": "Milestone 1",
    "due_date": "2024-01-15",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### ProjectTaskCreated
Emitted when a project task is created.

```json
{
  "event_type": "project.task.created",
  "event_version": "1.0.0",
  "data": {
    "task_id": "uuid",
    "project_id": "uuid",
    "user_id": "uuid",
    "title": "Task Title",
    "priority": "high",
    "due_date": "2024-01-10",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### Task Events

#### TaskCreated
Emitted when a task is created.

```json
{
  "event_type": "task.created",
  "event_version": "1.0.0",
  "data": {
    "task_id": "uuid",
    "user_id": "uuid",
    "title": "Task Title",
    "priority": "medium",
    "due_date": "2024-01-10T10:00:00Z",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### TaskCompleted
Emitted when a task is completed.

```json
{
  "event_type": "task.completed",
  "event_version": "1.0.0",
  "data": {
    "task_id": "uuid",
    "user_id": "uuid",
    "completed_at": "2024-01-01T10:00:00Z"
  }
}
```

**Consumers:**
- Analytics Service (track completions)
- Notification Service (send reminder if recurring)

---

### Calendar Events

#### EventCreated
Emitted when a calendar event is created.

```json
{
  "event_type": "calendar.event.created",
  "event_version": "1.0.0",
  "data": {
    "event_id": "uuid",
    "user_id": "uuid",
    "calendar_id": "uuid",
    "title": "Meeting",
    "start_time": "2024-01-10T10:00:00Z",
    "end_time": "2024-01-10T11:00:00Z",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### EventReminderTriggered
Emitted when an event reminder is triggered.

```json
{
  "event_type": "calendar.event.reminder.triggered",
  "event_version": "1.0.0",
  "data": {
    "event_id": "uuid",
    "user_id": "uuid",
    "reminder_minutes_before": 15,
    "triggered_at": "2024-01-10T09:45:00Z"
  }
}
```

**Consumers:**
- Notification Service (send reminder)

---

### Agent Events

#### AgentCreated
Emitted when an agent is created.

```json
{
  "event_type": "agent.created",
  "event_version": "1.0.0",
  "data": {
    "agent_id": "uuid",
    "user_id": "uuid",
    "name": "My Agent",
    "agent_type": "study",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### AgentExecutionStarted
Emitted when agent execution starts.

```json
{
  "event_type": "agent.execution.started",
  "event_version": "1.0.0",
  "data": {
    "execution_id": "uuid",
    "agent_id": "uuid",
    "user_id": "uuid",
    "input": {},
    "started_at": "2024-01-01T00:00:00Z"
  }
}
```

#### AgentExecutionCompleted
Emitted when agent execution completes.

```json
{
  "event_type": "agent.execution.completed",
  "event_version": "1.0.0",
  "data": {
    "execution_id": "uuid",
    "agent_id": "uuid",
    "user_id": "uuid",
    "status": "success",
    "output": {},
    "duration_seconds": 5,
    "completed_at": "2024-01-01T00:00:05Z"
  }
}
```

---

### Analytics Events

#### DailyStatsGenerated
Emitted when daily statistics are generated.

```json
{
  "event_type": "analytics.daily_stats.generated",
  "event_version": "1.0.0",
  "data": {
    "user_id": "uuid",
    "stat_date": "2024-01-01",
    "notes_created": 5,
    "documents_uploaded": 2,
    "learning_minutes": 60,
    "tasks_completed": 3,
    "generated_at": "2024-01-02T00:00:00Z"
  }
}
```

---

## Message Broker Configuration

### RabbitMQ Setup

#### Exchanges

**Topic Exchanges (for routing):**
- `auth.events` - Authentication events
- `content.events` - Content events (notes, documents)
- `learning.events` - Learning events
- `career.events` - Career events
- `project.events` - Project events
- `task.events` - Task events
- `calendar.events` - Calendar events
- `agent.events` - Agent events
- `analytics.events` - Analytics events

**Fanout Exchanges (for broadcasting):**
- `broadcast.events` - Broadcast to all consumers

#### Queues

**Service-specific queues:**
- `auth.service.queue` - Authentication service
- `notes.service.queue` - Notes service
- `documents.service.queue` - Documents service
- `ai.service.queue` - AI service
- `search.service.queue` - Search service
- `knowledge.service.queue` - Knowledge service
- `analytics.service.queue` - Analytics service
- `notification.service.queue` - Notification service

**Task queues:**
- `document.processing.queue` - Document processing tasks
- `embedding.generation.queue` - Embedding generation tasks
- `entity.extraction.queue` - Entity extraction tasks
- `notification.delivery.queue` - Notification delivery tasks
- `analytics.aggregation.queue` - Analytics aggregation tasks

#### Bindings

**Example bindings:**
- `content.events` → `ai.service.queue` (routing key: `content.note.*`)
- `content.events` → `search.service.queue` (routing key: `content.*`)
- `learning.events` → `analytics.service.queue` (routing key: `learning.session.*`)

---

## Event Patterns

### 1. Event Notification Pattern
Producer publishes event, consumers receive notification.

**Use Case:**
- Note created → Notify analytics service

**Implementation:**
```python
# Producer
await event_publisher.publish(
    "content.note.created",
    NoteCreatedEvent(note_id="uuid", user_id="uuid", ...)
)

# Consumer
@event_subscriber.subscribe("content.note.created")
async def handle_note_created(event: NoteCreatedEvent):
    await analytics_service.track_note_creation(event)
```

### 2. Event-Carried State Transfer
Event contains all data needed by consumers.

**Use Case:**
- Document processed → AI service needs extracted text

**Implementation:**
```json
{
  "event_type": "content.document.processed",
  "data": {
    "document_id": "uuid",
    "extracted_text": "Full text content...",
    "chunks": [...]
  }
}
```

### 3. Event Sourcing
Store all events as immutable log, rebuild state by replaying.

**Use Case:**
- Note version history
- Audit trail

**Implementation:**
```python
# Store event
await event_store.append(
    stream_id=f"note_{note_id}",
    event=NoteUpdatedEvent(...)
)

# Rebuild state
events = await event_store.read_stream(f"note_{note_id}")
note = rebuild_note_from_events(events)
```

### 4. CQRS Pattern
Separate read and write models, events synchronize them.

**Use Case:**
- Note created → Update write model, publish event, update read model

**Implementation:**
```python
# Write side
note = await note_repository.create(...)
await event_publisher.publish("content.note.created", ...)

# Read side
@event_subscriber.subscribe("content.note.created")
async def update_read_model(event: NoteCreatedEvent):
    await read_model.note_search_index.add(event)
```

### 5. Saga Pattern
Coordinate distributed transactions using events.

**Use Case:**
- Document upload → Process → Generate embeddings → Index

**Implementation:**
```python
# Saga orchestrator
class DocumentUploadSaga:
    async def execute(self, document_id: str):
        # Step 1: Upload
        await document_service.upload(document_id)
        
        # Step 2: Process (triggered by event)
        await self.wait_for("content.document.processed")
        
        # Step 3: Generate embeddings (triggered by event)
        await self.wait_for("ai.embeddings.generated")
        
        # Step 4: Index (triggered by event)
        await self.wait_for("search.document.indexed")
```

### 6. Retry Pattern
Retry failed event processing with exponential backoff.

**Implementation:**
```python
@event_subscriber.subscribe("content.document.processed", retry_policy=RetryPolicy(
    max_retries=3,
    backoff=exponential_backoff
))
async def handle_document_processed(event: DocumentProcessedEvent):
    try:
        await generate_embeddings(event.document_id)
    except Exception as e:
        raise  # Trigger retry
```

### 7. Dead Letter Pattern
Failed events sent to dead letter queue for inspection.

**Implementation:**
```python
# Configure dead letter queue
queue = channel.queue_declare(
    queue="document.processing.queue",
    arguments={
        "x-dead-letter-exchange": "dlx",
        "x-dead-letter-routing-key": "document.processing.dlq"
    }
)
```

---

## Event Implementation

### Event Publisher

```python
# core/events/publisher.py
import pika
import json
from typing import Any
from datetime import datetime
import uuid

class EventPublisher:
    def __init__(self, config: Config):
        self.config = config
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=config.RABBITMQ_HOST,
                port=config.RABBITMQ_PORT,
                credentials=pika.PlainCredentials(
                    config.RABBITMQ_USER,
                    config.RABBITMQ_PASSWORD
                )
            )
        )
        self.channel = self.connection.channel()
        
        # Declare exchanges
        self._declare_exchanges()
    
    def _declare_exchanges(self):
        exchanges = [
            'auth.events',
            'content.events',
            'learning.events',
            'career.events',
            'project.events',
            'task.events',
            'calendar.events',
            'agent.events',
            'analytics.events'
        ]
        
        for exchange in exchanges:
            self.channel.exchange_declare(
                exchange=exchange,
                exchange_type='topic',
                durable=True
            )
    
    async def publish(
        self,
        event_type: str,
        event_data: Any,
        routing_key: str = None
    ) -> None:
        # Extract exchange from event type
        exchange = event_type.split('.')[0] + '.events'
        
        # Create event envelope
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "event_version": "1.0.0",
            "occurred_at": datetime.utcnow().isoformat(),
            "correlation_id": str(uuid.uuid4()),
            "producer": self.config.SERVICE_NAME,
            "data": event_data.dict() if hasattr(event_data, 'dict') else event_data,
            "metadata": {}
        }
        
        # Serialize event
        message = json.dumps(event)
        
        # Publish event
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key or event_type,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json',
                timestamp=int(datetime.utcnow().timestamp())
            )
        )
    
    def close(self):
        self.connection.close()
```

### Event Subscriber

```python
# core/events/subscriber.py
import pika
import json
from typing import Callable, Dict, Any
from datetime import datetime

class EventSubscriber:
    def __init__(self, config: Config):
        self.config = config
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=config.RABBITMQ_HOST,
                port=config.RABBITMQ_PORT,
                credentials=pika.PlainCredentials(
                    config.RABBITMQ_USER,
                    config.RABBITMQ_PASSWORD
                )
            )
        )
        self.channel = self.connection.channel()
        self.handlers: Dict[str, Callable] = {}
        
        # Declare exchanges and queues
        self._declare_infrastructure()
    
    def _declare_infrastructure(self):
        # Declare exchanges
        exchanges = [
            'auth.events',
            'content.events',
            'learning.events',
            'career.events',
            'project.events',
            'task.events',
            'calendar.events',
            'agent.events',
            'analytics.events'
        ]
        
        for exchange in exchanges:
            self.channel.exchange_declare(
                exchange=exchange,
                exchange_type='topic',
                durable=True
            )
        
        # Declare dead letter exchange
        self.channel.exchange_declare(
            exchange='dlx',
            exchange_type='direct',
            durable=True
        )
    
    def subscribe(
        self,
        event_type: str,
        handler: Callable,
        queue_name: str = None,
        routing_key: str = None
    ) -> None:
        self.handlers[event_type] = handler
        
        # Extract exchange from event type
        exchange = event_type.split('.')[0] + '.events'
        
        # Generate queue name if not provided
        if not queue_name:
            queue_name = f"{self.config.SERVICE_NAME}.{event_type}.queue"
        
        # Declare queue with dead letter exchange
        self.channel.queue_declare(
            queue=queue_name,
            durable=True,
            arguments={
                'x-dead-letter-exchange': 'dlx',
                'x-dead-letter-routing-key': f"{queue_name}.dlq"
            }
        )
        
        # Bind queue to exchange
        self.channel.queue_bind(
            exchange=exchange,
            queue=queue_name,
            routing_key=routing_key or event_type
        )
        
        # Set up consumer
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=lambda ch, method, properties, body: self._handle_message(
                event_type, handler, ch, method, properties, body
            ),
            auto_ack=False
        )
    
    def _handle_message(
        self,
        event_type: str,
        handler: Callable,
        channel: pika.channel.Channel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes
    ) -> None:
        try:
            # Parse event
            event = json.loads(body)
            
            # Call handler
            handler(event)
            
            # Acknowledge message
            channel.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            # Log error
            print(f"Error handling event {event_type}: {e}")
            
            # Reject message (send to dead letter queue)
            channel.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False
            )
    
    def start(self):
        self.channel.start_consuming()
    
    def close(self):
        self.connection.close()
```

### Event Models

```python
# core/events/models.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class BaseEvent(BaseModel):
    event_id: UUID
    event_type: str
    event_version: str
    occurred_at: datetime
    correlation_id: UUID
    causation_id: Optional[UUID]
    producer: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]

class NoteCreatedEvent(BaseModel):
    note_id: UUID
    user_id: UUID
    title: str
    note_type: str
    folder_id: Optional[UUID]
    tags: list[str]
    created_at: datetime

class DocumentUploadedEvent(BaseModel):
    document_id: UUID
    user_id: UUID
    title: str
    file_name: str
    file_type: str
    file_size: int
    uploaded_at: datetime

class DocumentProcessedEvent(BaseModel):
    document_id: UUID
    user_id: UUID
    status: str
    extracted_text_length: int
    chunk_count: int
    ocr_performed: bool
    processed_at: datetime

class LearningSessionCompletedEvent(BaseModel):
    session_id: UUID
    user_id: UUID
    topic_id: Optional[UUID]
    duration_minutes: int
    notes: Optional[str]
    completed_at: datetime
```

---

## Event Processing Strategies

### 1. At-Least-Once Delivery
Messages are guaranteed to be delivered but may be duplicated.

**Implementation:**
- Use persistent queues
- Manual acknowledgment
- Idempotent consumers

### 2. At-Most-Once Delivery
Messages may be lost but never duplicated.

**Implementation:**
- Auto-acknowledgment
- Non-persistent queues
- Faster processing

### 3. Exactly-Once Delivery
Messages are delivered exactly once (ideal but complex).

**Implementation:**
- Use message deduplication
- Idempotent operations
- Transactional outbox pattern

---

## Event Monitoring

### Metrics to Track

- **Event throughput**: Events per second
- **Event latency**: Time from publish to consume
- **Queue depth**: Number of messages in queue
- **Consumer lag**: Time behind producer
- **Error rate**: Failed message processing
- **Dead letter count**: Messages in DLQ

### Monitoring Implementation

```python
# core/events/monitoring.py
from prometheus_client import Counter, Histogram, Gauge

# Metrics
events_published = Counter(
    'events_published_total',
    'Total events published',
    ['event_type', 'exchange']
)

events_consumed = Counter(
    'events_consumed_total',
    'Total events consumed',
    ['event_type', 'queue']
)

event_processing_duration = Histogram(
    'event_processing_duration_seconds',
    'Event processing duration',
    ['event_type']
)

queue_depth = Gauge(
    'queue_depth',
    'Current queue depth',
    ['queue_name']
)

consumer_lag = Gauge(
    'consumer_lag_seconds',
    'Consumer lag in seconds',
    ['queue_name']
)
```

---

## Event Testing

### Unit Testing Events

```python
# tests/events/test_publisher.py
import pytest
from core.events.publisher import EventPublisher
from core.events.models import NoteCreatedEvent

def test_publish_note_created():
    publisher = EventPublisher(config)
    event = NoteCreatedEvent(
        note_id="uuid",
        user_id="uuid",
        title="Test Note",
        note_type="rich_text",
        folder_id=None,
        tags=[],
        created_at=datetime.utcnow()
    )
    
    publisher.publish("content.note.created", event)
    
    # Assert event was published
    # (mock RabbitMQ connection)
```

### Integration Testing Events

```python
# tests/events/test_integration.py
import pytest
from core.events.publisher import EventPublisher
from core.events.subscriber import EventSubscriber

def test_event_flow():
    # Setup publisher and subscriber
    publisher = EventPublisher(config)
    subscriber = EventSubscriber(config)
    
    # Subscribe to event
    received_events = []
    
    def handler(event):
        received_events.append(event)
    
    subscriber.subscribe("content.note.created", handler)
    
    # Publish event
    publisher.publish("content.note.created", test_event)
    
    # Wait for processing
    time.sleep(1)
    
    # Assert event was received
    assert len(received_events) == 1
```

---

## Best Practices

### 1. Event Design
- Keep events small and focused
- Use immutable event data
- Include all necessary context
- Version events explicitly

### 2. Error Handling
- Implement retry logic
- Use dead letter queues
- Log all failures
- Monitor error rates

### 3. Performance
- Batch events when possible
- Use connection pooling
- Optimize serialization
- Monitor queue depths

### 4. Security
- Encrypt sensitive event data
- Use TLS for connections
- Authenticate producers/consumers
- Validate event schemas

### 5. Testing
- Test event publishing
- Test event consumption
- Test error scenarios
- Test integration flows

---

## Troubleshooting

### Common Issues

**Issue: Events not being consumed**
- Check queue bindings
- Verify consumer is running
- Check for network issues
- Review RabbitMQ logs

**Issue: High queue depth**
- Increase consumer count
- Optimize consumer performance
- Check for blocking operations
- Review event volume

**Issue: Duplicate events**
- Implement idempotency
- Check acknowledgment logic
- Review retry configuration
- Use message deduplication

**Issue: Events in dead letter queue**
- Review error logs
- Check event schema
- Validate consumer logic
- Reprocess failed events

---

**Document Status:** Approved
**Next Review:** Q4 2026
**Owner:** Architecture Team
