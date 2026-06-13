# MEMORIA AI - Database Schema

## Version: 1.0
## Date: June 13, 2026
## Status: Final

---

## Executive Summary

This document provides the complete database schema for MEMORIA AI, including all tables, relationships, indexes, constraints, and optimization strategies. The schema is designed for PostgreSQL 15+ with support for JSON columns, full-text search, and advanced indexing.

---

## Database Overview

### Database Name: memoria_ai

### Schemas
- `public` - Main schema for all tables
- `auth` - Authentication and authorization tables
- `content` - Notes, documents, and content tables
- `learning` - Learning and study tracking tables
- `career` - Career and job tracking tables
- `projects` - Project management tables
- `tasks` - Task and todo tables
- `calendar` - Calendar and event tables
- `agents` - AI agent tables
- `analytics` - Analytics and metrics tables
- `audit` - Audit log tables

---

## Schema: auth

### Table: users

```sql
CREATE TABLE auth.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    two_factor_enabled BOOLEAN DEFAULT false,
    two_factor_secret VARCHAR(255),
    avatar_url VARCHAR(500),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_users_email ON auth.users(email);
CREATE INDEX idx_users_is_active ON auth.users(is_active);
CREATE INDEX idx_users_created_at ON auth.users(created_at);

-- Triggers
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Table: refresh_tokens

```sql
CREATE TABLE auth.refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT false,
    device_info JSONB
);

-- Indexes
CREATE INDEX idx_refresh_tokens_token ON auth.refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_user_id ON auth.refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires_at ON auth.refresh_tokens(expires_at);
CREATE INDEX idx_refresh_tokens_is_revoked ON auth.refresh_tokens(is_revoked);
```

### Table: oauth_accounts

```sql
CREATE TABLE auth.oauth_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider, provider_user_id)
);

-- Indexes
CREATE INDEX idx_oauth_accounts_user_id ON auth.oauth_accounts(user_id);
CREATE INDEX idx_oauth_accounts_provider ON auth.oauth_accounts(provider);
```

### Table: sessions

```sql
CREATE TABLE auth.sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    session_token VARCHAR(500) UNIQUE NOT NULL,
    user_agent VARCHAR(500),
    ip_address VARCHAR(50),
    location JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_sessions_session_token ON auth.sessions(session_token);
CREATE INDEX idx_sessions_user_id ON auth.sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON auth.sessions(expires_at);
```

### Table: api_keys

```sql
CREATE TABLE auth.api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(500) UNIQUE NOT NULL,
    scopes JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_api_keys_key_hash ON auth.api_keys(key_hash);
CREATE INDEX idx_api_keys_user_id ON auth.api_keys(user_id);
CREATE INDEX idx_api_keys_is_active ON auth.api_keys(is_active);
```

---

## Schema: content

### Table: folders

```sql
CREATE TABLE content.folders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    parent_id UUID REFERENCES content.folders(id) ON DELETE SET NULL,
    icon VARCHAR(50),
    color VARCHAR(7),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_folders_user_id ON content.folders(user_id);
CREATE INDEX idx_folders_parent_id ON content.folders(parent_id);
```

### Table: tags

```sql
CREATE TABLE content.tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL UNIQUE,
    color VARCHAR(7),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_tags_user_id ON content.tags(user_id);
CREATE INDEX idx_tags_name ON content.tags(name);
```

### Table: notes

```sql
CREATE TABLE content.notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    note_type VARCHAR(50) DEFAULT 'rich_text' CHECK (note_type IN ('rich_text', 'markdown', 'code')),
    is_pinned BOOLEAN DEFAULT false,
    is_favorite BOOLEAN DEFAULT false,
    is_archived BOOLEAN DEFAULT false,
    folder_id UUID REFERENCES content.folders(id) ON DELETE SET NULL,
    ai_generated_title BOOLEAN DEFAULT false,
    ai_generated_tags BOOLEAN DEFAULT false,
    ai_summary TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_notes_user_id ON content.notes(user_id);
CREATE INDEX idx_notes_folder_id ON content.notes(folder_id);
CREATE INDEX idx_notes_is_pinned ON content.notes(is_pinned);
CREATE INDEX idx_notes_is_favorite ON content.notes(is_favorite);
CREATE INDEX idx_notes_is_archived ON content.notes(is_archived);
CREATE INDEX idx_notes_created_at ON content.notes(created_at);
CREATE INDEX idx_notes_updated_at ON content.notes(updated_at);

-- Full-text search index
CREATE INDEX idx_notes_search ON content.notes USING GIN(to_tsvector('english', title || ' ' || content));

-- Triggers
CREATE TRIGGER update_notes_updated_at
    BEFORE UPDATE ON content.notes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Table: note_tags

```sql
CREATE TABLE content.note_tags (
    note_id UUID NOT NULL REFERENCES content.notes(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES content.tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (note_id, tag_id)
);

-- Indexes
CREATE INDEX idx_note_tags_note_id ON content.note_tags(note_id);
CREATE INDEX idx_note_tags_tag_id ON content.note_tags(tag_id);
```

### Table: note_versions

```sql
CREATE TABLE content.note_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_id UUID NOT NULL REFERENCES content.notes(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_note_versions_note_id ON content.note_versions(note_id);
CREATE INDEX idx_note_versions_version_number ON content.note_versions(note_id, version_number);
```

### Table: note_links

```sql
CREATE TABLE content.note_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_note_id UUID NOT NULL REFERENCES content.notes(id) ON DELETE CASCADE,
    target_note_id UUID NOT NULL REFERENCES content.notes(id) ON DELETE CASCADE,
    link_type VARCHAR(50) DEFAULT 'reference' CHECK (link_type IN ('reference', 'citation', 'related')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_note_links_source_note_id ON content.note_links(source_note_id);
CREATE INDEX idx_note_links_target_note_id ON content.note_links(target_note_id);
```

### Table: documents

```sql
CREATE TABLE content.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    file_name VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL CHECK (file_type IN ('pdf', 'docx', 'txt', 'csv', 'xlsx', 'pptx', 'image', 'audio', 'video', 'zip')),
    file_size BIGINT NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    thumbnail_path VARCHAR(1000),
    status VARCHAR(50) DEFAULT 'uploading' CHECK (status IN ('uploading', 'processing', 'ready', 'failed')),
    extracted_text TEXT,
    metadata JSONB DEFAULT '{}',
    ocr_required BOOLEAN DEFAULT false,
    ocr_completed BOOLEAN DEFAULT false,
    indexed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_documents_user_id ON content.documents(user_id);
CREATE INDEX idx_documents_status ON content.documents(status);
CREATE INDEX idx_documents_file_type ON content.documents(file_type);
CREATE INDEX idx_documents_created_at ON content.documents(created_at);

-- Full-text search index
CREATE INDEX idx_documents_search ON content.documents USING GIN(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(extracted_text, '')));

-- Triggers
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON content.documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Table: document_chunks

```sql
CREATE TABLE content.document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES content.documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    start_page INTEGER,
    end_page INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_document_chunks_document_id ON content.document_chunks(document_id);
CREATE INDEX idx_document_chunks_chunk_index ON content.document_chunks(document_id, chunk_index);

-- Full-text search index
CREATE INDEX idx_document_chunks_search ON content.document_chunks USING GIN(to_tsvector('english', content));
```

### Table: document_shares

```sql
CREATE TABLE content.document_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES content.documents(id) ON DELETE CASCADE,
    shared_with_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    share_token VARCHAR(100) UNIQUE,
    permission VARCHAR(50) DEFAULT 'view' CHECK (permission IN ('view', 'edit', 'comment')),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_document_shares_document_id ON content.document_shares(document_id);
CREATE INDEX idx_document_shares_shared_with_user_id ON content.document_shares(shared_with_user_id);
CREATE INDEX idx_document_shares_share_token ON content.document_shares(share_token);
```

### Table: collections

```sql
CREATE TABLE content.collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(7),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_collections_user_id ON content.collections(user_id);
```

### Table: collection_items

```sql
CREATE TABLE content.collection_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID NOT NULL REFERENCES content.collections(id) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL CHECK (item_type IN ('note', 'document')),
    item_id UUID NOT NULL,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_collection_items_collection_id ON content.collection_items(collection_id);
CREATE INDEX idx_collection_items_item ON content.collection_items(item_type, item_id);
```

---

## Schema: learning

### Table: topics

```sql
CREATE TABLE learning.topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES learning.topics(id) ON DELETE SET NULL,
    color VARCHAR(7),
    icon VARCHAR(50),
    difficulty_level VARCHAR(50) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_topics_user_id ON learning.topics(user_id);
CREATE INDEX idx_topics_parent_id ON learning.topics(parent_id);
```

### Table: learning_sessions

```sql
CREATE TABLE learning.learning_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    topic_id UUID REFERENCES learning.topics(id) ON DELETE SET NULL,
    note_id UUID REFERENCES content.notes(id) ON DELETE SET NULL,
    document_id UUID REFERENCES content.documents(id) ON DELETE SET NULL,
    duration_minutes INTEGER NOT NULL,
    notes TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_learning_sessions_user_id ON learning.learning_sessions(user_id);
CREATE INDEX idx_learning_sessions_topic_id ON learning.learning_sessions(topic_id);
CREATE INDEX idx_learning_sessions_started_at ON learning.learning_sessions(started_at);
```

### Table: topic_progress

```sql
CREATE TABLE learning.topic_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    topic_id UUID NOT NULL REFERENCES learning.topics(id) ON DELETE CASCADE,
    total_minutes INTEGER DEFAULT 0,
    session_count INTEGER DEFAULT 0,
    mastery_level DECIMAL(5,2) DEFAULT 0.00 CHECK (mastery_level >= 0 AND mastery_level <= 100),
    last_studied_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, topic_id)
);

-- Indexes
CREATE INDEX idx_topic_progress_user_id ON learning.topic_progress(user_id);
CREATE INDEX idx_topic_progress_topic_id ON learning.topic_progress(topic_id);
```

### Table: flashcards

```sql
CREATE TABLE learning.flashcards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    topic_id UUID REFERENCES learning.topics(id) ON DELETE SET NULL,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    deck_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_flashcards_user_id ON learning.flashcards(user_id);
CREATE INDEX idx_flashcards_topic_id ON learning.flashcards(topic_id);
CREATE INDEX idx_flashcards_deck_name ON learning.flashcards(deck_name);
```

### Table: flashcard_reviews

```sql
CREATE TABLE learning.flashcard_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flashcard_id UUID NOT NULL REFERENCES learning.flashcards(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    quality INTEGER NOT NULL CHECK (quality >= 0 AND quality <= 5),
    ease_factor DECIMAL(5,2) DEFAULT 2.50,
    interval_days INTEGER DEFAULT 0,
    next_review_date TIMESTAMP WITH TIME ZONE,
    reviewed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_flashcard_reviews_flashcard_id ON learning.flashcard_reviews(flashcard_id);
CREATE INDEX idx_flashcard_reviews_user_id ON learning.flashcard_reviews(user_id);
CREATE INDEX idx_flashcard_reviews_next_review_date ON learning.flashcard_reviews(next_review_date);
```

### Table: quizzes

```sql
CREATE TABLE learning.quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    topic_id UUID REFERENCES learning.topics(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    question_count INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_quizzes_user_id ON learning.quizzes(user_id);
CREATE INDEX idx_quizzes_topic_id ON learning.quizzes(topic_id);
```

### Table: quiz_questions

```sql
CREATE TABLE learning.quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL REFERENCES learning.quizzes(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    options JSONB NOT NULL,
    correct_answer INTEGER NOT NULL,
    explanation TEXT,
    order_index INTEGER NOT NULL
);

-- Indexes
CREATE INDEX idx_quiz_questions_quiz_id ON learning.quiz_questions(quiz_id);
```

### Table: quiz_attempts

```sql
CREATE TABLE learning.quiz_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL REFERENCES learning.quizzes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_quiz_attempts_quiz_id ON learning.quiz_attempts(quiz_id);
CREATE INDEX idx_quiz_attempts_user_id ON learning.quiz_attempts(user_id);
```

### Table: revision_plans

```sql
CREATE TABLE learning.revision_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    topics JSONB NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    daily_hours DECIMAL(4,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_revision_plans_user_id ON learning.revision_plans(user_id);
```

---

## Schema: career

### Table: resumes

```sql
CREATE TABLE career.resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    file_path VARCHAR(1000),
    content TEXT,
    parsed_data JSONB,
    ats_score DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_resumes_user_id ON career.resumes(user_id);
```

### Table: skills

```sql
CREATE TABLE career.skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    proficiency_level VARCHAR(50) CHECK (proficiency_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    years_of_experience DECIMAL(4,1),
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, name)
);

-- Indexes
CREATE INDEX idx_skills_user_id ON career.skills(user_id);
CREATE INDEX idx_skills_category ON career.skills(category);
```

### Table: job_applications

```sql
CREATE TABLE career.job_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    job_description TEXT,
    application_url VARCHAR(1000),
    status VARCHAR(50) DEFAULT 'applied' CHECK (status IN ('wishlist', 'applied', 'screening', 'interview', 'offer', 'rejected', 'withdrawn')),
    applied_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_job_applications_user_id ON career.job_applications(user_id);
CREATE INDEX idx_job_applications_status ON career.job_applications(status);
CREATE INDEX idx_job_applications_company_name ON career.job_applications(company_name);
```

### Table: interview_preparations

```sql
CREATE TABLE career.interview_preparations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    job_application_id UUID REFERENCES career.job_applications(id) ON DELETE SET NULL,
    company_name VARCHAR(255),
    interview_type VARCHAR(50) CHECK (interview_type IN ('technical', 'behavioral', 'system_design', 'culture_fit')),
    interview_date TIMESTAMP WITH TIME ZONE,
    questions JSONB,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_interview_preparations_user_id ON career.interview_preparations(user_id);
CREATE INDEX idx_interview_preparations_job_application_id ON career.interview_preparations(job_application_id);
```

### Table: career_roadmaps

```sql
CREATE TABLE career.career_roadmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    target_role VARCHAR(255) NOT NULL,
    current_role VARCHAR(255),
    milestones JSONB,
    skills_to_acquire JSONB,
    estimated_months INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_career_roadmaps_user_id ON career.career_roadmaps(user_id);
```

### Table: internships

```sql
CREATE TABLE career.internships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'ongoing' CHECK (status IN ('ongoing', 'completed', 'upcoming')),
    description TEXT,
    learnings TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_internships_user_id ON career.internships(user_id);
CREATE INDEX idx_internships_status ON career.internships(status);
```

---

## Schema: projects

### Table: projects

```sql
CREATE TABLE projects.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'archived', 'on_hold')),
    start_date DATE,
    end_date DATE,
    github_url VARCHAR(1000),
    repository_name VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_projects_user_id ON projects.projects(user_id);
CREATE INDEX idx_projects_status ON projects.projects(status);
CREATE INDEX idx_projects_github_url ON projects.projects(github_url);

-- Triggers
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects.projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Table: milestones

```sql
CREATE TABLE projects.milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects.projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_milestones_project_id ON projects.milestones(project_id);
CREATE INDEX idx_milestones_status ON projects.milestones(status);
CREATE INDEX idx_milestones_due_date ON projects.milestones(due_date);
```

### Table: project_tasks

```sql
CREATE TABLE projects.project_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects.projects(id) ON DELETE CASCADE,
    milestone_id UUID REFERENCES projects.milestones(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'todo' CHECK (status IN ('todo', 'in_progress', 'completed', 'cancelled')),
    priority VARCHAR(50) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    assignee_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    due_date DATE,
    estimated_hours DECIMAL(4,2),
    actual_hours DECIMAL(4,2),
    github_issue_number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_project_tasks_project_id ON projects.project_tasks(project_id);
CREATE INDEX idx_project_tasks_milestone_id ON projects.project_tasks(milestone_id);
CREATE INDEX idx_project_tasks_status ON projects.project_tasks(status);
CREATE INDEX idx_project_tasks_assignee_id ON projects.project_tasks(assignee_id);
CREATE INDEX idx_project_tasks_due_date ON projects.project_tasks(due_date);
```

### Table: project_risks

```sql
CREATE TABLE projects.project_risks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects.projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    probability VARCHAR(50) CHECK (probability IN ('low', 'medium', 'high')),
    impact VARCHAR(50) CHECK (impact IN ('low', 'medium', 'high')),
    mitigation_plan TEXT,
    status VARCHAR(50) DEFAULT 'open' CHECK (status IN ('open', 'mitigated', 'closed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_project_risks_project_id ON projects.project_risks(project_id);
CREATE INDEX idx_project_risks_status ON projects.project_risks(status);
```

---

## Schema: tasks

### Table: tasks

```sql
CREATE TABLE tasks.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'todo' CHECK (status IN ('todo', 'in_progress', 'completed', 'cancelled')),
    priority VARCHAR(50) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    due_date TIMESTAMP WITH TIME ZONE,
    due_time TIME,
    reminder_minutes_before INTEGER,
    is_recurring BOOLEAN DEFAULT false,
    recurrence_rule JSONB,
    parent_task_id UUID REFERENCES tasks.tasks(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects.projects(id) ON DELETE SET NULL,
    tags JSONB DEFAULT '[]',
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_tasks_user_id ON tasks.tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks.tasks(status);
CREATE INDEX idx_tasks_priority ON tasks.tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks.tasks(due_date);
CREATE INDEX idx_tasks_parent_task_id ON tasks.tasks(parent_task_id);
CREATE INDEX idx_tasks_project_id ON tasks.tasks(project_id);
CREATE INDEX idx_tasks_is_recurring ON tasks.tasks(is_recurring);

-- Triggers
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks.tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Table: task_dependencies

```sql
CREATE TABLE tasks.task_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks.tasks(id) ON DELETE CASCADE,
    depends_on_task_id UUID NOT NULL REFERENCES tasks.tasks(id) ON DELETE CASCADE,
    dependency_type VARCHAR(50) DEFAULT 'finish_to_start' CHECK (dependency_type IN ('finish_to_start', 'start_to_start', 'finish_to_finish', 'start_to_finish')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(task_id, depends_on_task_id)
);

-- Indexes
CREATE INDEX idx_task_dependencies_task_id ON tasks.task_dependencies(task_id);
CREATE INDEX idx_task_dependencies_depends_on_task_id ON tasks.task_dependencies(depends_on_task_id);
```

---

## Schema: calendar

### Table: calendars

```sql
CREATE TABLE calendar.calendars (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    color VARCHAR(7),
    provider VARCHAR(50) CHECK (provider IN ('local', 'google', 'outlook')),
    provider_calendar_id VARCHAR(255),
    is_default BOOLEAN DEFAULT false,
    is_synced BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_calendars_user_id ON calendar.calendars(user_id);
CREATE INDEX idx_calendars_provider ON calendar.calendars(provider);
```

### Table: events

```sql
CREATE TABLE calendar.events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    calendar_id UUID REFERENCES calendar.calendars(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    location VARCHAR(500),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    is_all_day BOOLEAN DEFAULT false,
    recurrence_rule JSONB,
    reminder_minutes_before INTEGER,
    status VARCHAR(50) DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'tentative', 'cancelled')),
    provider_event_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_events_user_id ON calendar.events(user_id);
CREATE INDEX idx_events_calendar_id ON calendar.events(calendar_id);
CREATE INDEX idx_events_start_time ON calendar.events(start_time);
CREATE INDEX idx_events_end_time ON calendar.events(end_time);
CREATE INDEX idx_events_status ON calendar.events(status);

-- Triggers
CREATE TRIGGER update_events_updated_at
    BEFORE UPDATE ON calendar.events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Table: event_attendees

```sql
CREATE TABLE calendar.event_attendees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES calendar.events(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255),
    name VARCHAR(255),
    response_status VARCHAR(50) DEFAULT 'needs_action' CHECK (response_status IN ('needs_action', 'accepted', 'declined', 'tentative')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_event_attendees_event_id ON calendar.event_attendees(event_id);
CREATE INDEX idx_event_attendees_user_id ON calendar.event_attendees(user_id);
```

---

## Schema: agents

### Table: agents

```sql
CREATE TABLE agents.agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    agent_type VARCHAR(50) NOT NULL CHECK (agent_type IN ('study', 'research', 'career', 'coding', 'document', 'planning', 'project', 'task')),
    description TEXT,
    configuration JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_agents_user_id ON agents.agents(user_id);
CREATE INDEX idx_agents_agent_type ON agents.agents(agent_type);
CREATE INDEX idx_agents_is_active ON agents.agents(is_active);
```

### Table: agent_executions

```sql
CREATE TABLE agents.agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents.agents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    input JSONB,
    output JSONB,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER
);

-- Indexes
CREATE INDEX idx_agent_executions_agent_id ON agents.agent_executions(agent_id);
CREATE INDEX idx_agent_executions_user_id ON agents.agent_executions(user_id);
CREATE INDEX idx_agent_executions_status ON agents.agent_executions(status);
CREATE INDEX idx_agent_executions_started_at ON agents.agent_executions(started_at);
```

### Table: agent_memories

```sql
CREATE TABLE agents.agent_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents.agents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    memory_type VARCHAR(50) NOT NULL CHECK (memory_type IN ('short_term', 'long_term', 'semantic', 'episodic', 'procedural')),
    content JSONB NOT NULL,
    importance_score DECIMAL(3,2) DEFAULT 0.50,
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_agent_memories_agent_id ON agents.agent_memories(agent_id);
CREATE INDEX idx_agent_memories_user_id ON agents.agent_memories(user_id);
CREATE INDEX idx_agent_memories_memory_type ON agents.agent_memories(memory_type);
CREATE INDEX idx_agent_memories_expires_at ON agents.agent_memories(expires_at);
```

---

## Schema: analytics

### Table: daily_stats

```sql
CREATE TABLE analytics.daily_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    stat_date DATE NOT NULL,
    notes_created INTEGER DEFAULT 0,
    documents_uploaded INTEGER DEFAULT 0,
    learning_minutes INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    search_queries INTEGER DEFAULT 0,
    ai_interactions INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, stat_date)
);

-- Indexes
CREATE INDEX idx_daily_stats_user_id ON analytics.daily_stats(user_id);
CREATE INDEX idx_daily_stats_stat_date ON analytics.daily_stats(stat_date);
```

### Table: knowledge_growth

```sql
CREATE TABLE analytics.knowledge_growth (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    topic_id UUID REFERENCES learning.topics(id) ON DELETE SET NULL,
    metric_date DATE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_knowledge_growth_user_id ON analytics.knowledge_growth(user_id);
CREATE INDEX idx_knowledge_growth_topic_id ON analytics.knowledge_growth(topic_id);
CREATE INDEX idx_knowledge_growth_metric_date ON analytics.knowledge_growth(metric_date);
```

### Table: activity_logs

```sql
CREATE TABLE analytics.activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    metadata JSONB DEFAULT '{}',
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_activity_logs_user_id ON analytics.activity_logs(user_id);
CREATE INDEX idx_activity_logs_action ON analytics.activity_logs(action);
CREATE INDEX idx_activity_logs_resource ON analytics.activity_logs(resource_type, resource_id);
CREATE INDEX idx_activity_logs_created_at ON analytics.activity_logs(created_at);

-- Partition by month for large datasets
-- CREATE TABLE analytics.activity_logs_2026_06 PARTITION OF analytics.activity_logs
-- FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
```

---

## Schema: audit

### Table: audit_logs

```sql
CREATE TABLE audit.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    changed_by UUID REFERENCES auth.users(id),
    ip_address VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_audit_logs_user_id ON audit.audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit.audit_logs(action);
CREATE INDEX idx_audit_logs_table_name ON audit.audit_logs(table_name);
CREATE INDEX idx_audit_logs_record_id ON audit.audit_logs(record_id);
CREATE INDEX idx_audit_logs_created_at ON audit.audit_logs(created_at);
```

---

## Database Functions

### Updated At Trigger Function

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Full-Text Search Function

```sql
CREATE OR REPLACE FUNCTION search_notes(query_text TEXT)
RETURNS TABLE (
    id UUID,
    title VARCHAR(500),
    content TEXT,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        n.id,
        n.title,
        n.content,
        ts_rank(to_tsvector('english', n.title || ' ' || n.content), plainto_tsquery('english', query_text)) as rank
    FROM content.notes n
    WHERE 
        to_tsvector('english', n.title || ' ' || n.content) @@ plainto_tsquery('english', query_text)
        AND n.is_archived = false
    ORDER BY rank DESC;
END;
$$ LANGUAGE plpgsql;
```

---

## Database Views

### User Dashboard View

```sql
CREATE OR REPLACE VIEW analytics.user_dashboard AS
SELECT 
    u.id as user_id,
    u.email,
    u.full_name,
    COUNT(DISTINCT n.id) as total_notes,
    COUNT(DISTINCT d.id) as total_documents,
    COUNT(DISTINCT t.id) as total_tasks,
    COUNT(DISTINCT ls.id) as total_learning_sessions,
    SUM(ls.duration_minutes) as total_learning_minutes,
    MAX(n.created_at) as last_note_created,
    MAX(d.created_at) as last_document_uploaded
FROM auth.users u
LEFT JOIN content.notes n ON u.id = n.user_id AND n.is_archived = false
LEFT JOIN content.documents d ON u.id = d.user_id
LEFT JOIN tasks.tasks t ON u.id = t.user_id AND t.status != 'completed'
LEFT JOIN learning.learning_sessions ls ON u.id = ls.user_id
GROUP BY u.id, u.email, u.full_name;
```

### Learning Progress View

```sql
CREATE OR REPLACE VIEW learning.learning_progress_view AS
SELECT 
    tp.user_id,
    t.name as topic_name,
    tp.total_minutes,
    tp.session_count,
    tp.mastery_level,
    tp.last_studied_at
FROM learning.topic_progress tp
JOIN learning.topics t ON tp.topic_id = t.id
ORDER BY tp.mastery_level DESC;
```

---

## Database Optimization Strategies

### 1. Indexing Strategy

**Primary Indexes:**
- All primary keys are UUID with B-tree indexes
- Foreign keys have indexes for join optimization

**Secondary Indexes:**
- User_id indexes on all user-specific tables
- Status indexes for filtering
- Date indexes for time-based queries
- Full-text search indexes using GIN

**Composite Indexes:**
- (user_id, status) for filtered user queries
- (user_id, created_at) for time-series queries
- (document_id, chunk_index) for ordered retrieval

### 2. Partitioning Strategy

**Activity Logs Partitioning:**
- Partition by month for activity_logs table
- Automatic partition creation
- Old partition archiving

**Time-Based Partitioning:**
- Consider partitioning for large tables
- daily_stats by year
- activity_logs by month

### 3. Connection Pooling

**Configuration:**
- Pool size: 20 connections
- Max overflow: 10 connections
- Pool timeout: 30 seconds
- Pool recycle: 3600 seconds

### 4. Query Optimization

**Common Query Patterns:**
- Use EXPLAIN ANALYZE for slow queries
- Add appropriate indexes
- Use materialized views for complex aggregations
- Implement query caching with Redis

### 5. Vacuum and Analyze

**Maintenance Strategy:**
- Autovacuum enabled with default settings
- Manual VACUUM ANALYZE weekly
- REINDEX for heavily updated tables monthly

### 6. Backup Strategy

**Backup Configuration:**
- Full backup every 6 hours
- Incremental backup every hour
- Point-in-time recovery enabled
- 30-day retention period

---

## Migration Strategy

### Alembic Configuration

```python
# alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:password@localhost/memoria_ai

[post_write_hooks]
# format with "black"
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 79 REVISION_SCRIPT_FILENAME

# Environment-specific configurations
[env:development]
sqlalchemy.url = postgresql://user:password@localhost/memoria_ai_dev

[env:production]
sqlalchemy.url = postgresql://user:password@prod-host/memoria_ai
```

### Migration Best Practices

1. **Always create migrations in pairs** (upgrade and downgrade)
2. **Test migrations on staging before production**
3. **Use transactions for atomic migrations**
4. **Add indexes separately from table creation**
5. **Back up database before major migrations**

---

## Security Considerations

### Row-Level Security

```sql
-- Enable RLS on user-specific tables
ALTER TABLE content.notes ENABLE ROW LEVEL SECURITY;

-- Create policy for notes
CREATE POLICY user_notes_policy ON content.notes
    FOR ALL
    USING (user_id = current_setting('app.current_user_id')::UUID);

-- Set user context in application
SET app.current_user_id = 'user-uuid';
```

### Data Encryption

- Use pgcrypto for sensitive data encryption
- Encrypt at rest with TLS
- Encrypt specific columns with pgcrypto
- Use application-level encryption for API keys

### Audit Logging

- All DML operations logged
- Track who changed what and when
- Store old and new values
- Immutable audit logs

---

**Document Status:** Approved
**Next Review:** Q4 2026
**Owner:** Database Architecture Team
