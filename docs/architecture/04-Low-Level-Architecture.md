# MEMORIA AI - Low Level Architecture

## Version: 1.0
## Date: June 13, 2026
## Status: Final

---

## Executive Summary

This document provides detailed low-level architecture specifications for MEMORIA AI, including component designs, class structures, data models, and implementation details for each service and subsystem.

---

## Backend Service Architecture

### Service Layer Structure

Each backend service follows this layered structure:

```
service_name/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── dependencies.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── security.py
│   ├── exceptions.py
│   └── constants.py
├── models/
│   ├── __init__.py
│   ├── base.py
│   └── entity.py
├── repositories/
│   ├── __init__.py
│   ├── base.py
│   └── repository.py
├── services/
│   ├── __init__.py
│   ├── service.py
│   └── handlers.py
├── schemas/
│   ├── __init__.py
│   ├── request.py
│   └── response.py
├── events/
│   ├── __init__.py
│   ├── publisher.py
│   └── subscriber.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

---

## Authentication Service

### Component Design

#### Models

```python
# models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))
    avatar_url = Column(String(500))
    preferences = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    oauth_accounts = relationship("OAuthAccount", back_populates="user")
    sessions = relationship("Session", back_populates="user")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_revoked = Column(Boolean, default=False)
    device_info = Column(JSON)
    
    user = relationship("User", back_populates="refresh_tokens")

class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # google, github, microsoft
    provider_user_id = Column(String(255), nullable=False)
    access_token = Column(Text)
    refresh_token = Column(Text)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="oauth_accounts")
    __table_args__ = (UniqueConstraint('provider', 'provider_user_id'),)

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_token = Column(String(500), unique=True, nullable=False, index=True)
    user_agent = Column(String(500))
    ip_address = Column(String(50))
    location = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")
```

#### Services

```python
# services/auth_service.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import pyotp
import secrets

class AuthService:
    def __init__(self, config: Config):
        self.config = config
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.jwt_algorithm = "HS256"
    
    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user_id: str, expires_delta: timedelta = None) -> str:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {"sub": user_id, "exp": expire}
        return jwt.encode(to_encode, self.config.SECRET_KEY, algorithm=self.jwt_algorithm)
    
    def create_refresh_token(self, user_id: str) -> tuple[str, datetime]:
        token = secrets.token_urlsafe(64)
        expires_at = datetime.utcnow() + timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS)
        return token, expires_at
    
    def verify_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.config.SECRET_KEY, algorithms=[self.jwt_algorithm])
            user_id = payload.get("sub")
            if user_id is None:
                raise InvalidTokenException
            return user_id
        except JWTError:
            raise InvalidTokenException
    
    def generate_2fa_secret(self) -> str:
        return pyotp.random_base32()
    
    def verify_2fa_token(self, secret: str, token: str) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
```

#### API Routes

```python
# api/v1/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.request import LoginRequest, RegisterRequest, Verify2FARequest
from schemas.response import TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, service: AuthService = Depends()):
    # Check if user exists
    if await service.user_exists(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = await service.create_user(request)
    return UserResponse.from_orm(user)

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, service: AuthService = Depends()):
    # Authenticate user
    user = await service.authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check 2FA
    if user.two_factor_enabled:
        if not request.two_factor_token:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="2FA token required",
                headers={"X-2FA-Required": "true"}
            )
        if not service.verify_2fa_token(user.two_factor_secret, request.two_factor_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid 2FA token"
            )
    
    # Generate tokens
    access_token = service.create_access_token(str(user.id))
    refresh_token, expires_at = service.create_refresh_token(str(user.id))
    
    # Store refresh token
    await service.store_refresh_token(user.id, refresh_token, expires_at)
    
    # Create session
    await service.create_session(user.id, request.user_agent, request.ip_address)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=service.config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, service: AuthService = Depends()):
    # Verify refresh token
    token_data = await service.verify_refresh_token(request.refresh_token)
    if not token_data or token_data.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Generate new tokens
    access_token = service.create_access_token(str(token_data.user_id))
    new_refresh_token, expires_at = service.create_refresh_token(str(token_data.user_id))
    
    # Revoke old token
    await service.revoke_refresh_token(request.refresh_token)
    
    # Store new token
    await service.store_refresh_token(token_data.user_id, new_refresh_token, expires_at)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=service.config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
```

---

## Notes Service

### Component Design

#### Models

```python
# models/note.py
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import uuid
from datetime import datetime

class NoteType(enum.Enum):
    RICH_TEXT = "rich_text"
    MARKDOWN = "markdown"
    CODE = "code"

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    note_type = Column(Enum(NoteType), default=NoteType.RICH_TEXT)
    is_pinned = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("folders.id"), nullable=True)
    ai_generated_title = Column(Boolean, default=False)
    ai_generated_tags = Column(Boolean, default=False)
    ai_summary = Column(Text)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    folder = relationship("Folder", back_populates="notes")
    tags = relationship("Tag", secondary="note_tags", back_populates="notes")
    versions = relationship("NoteVersion", back_populates="note", cascade="all, delete-orphan")
    links_from = relationship("NoteLink", foreign_keys="NoteLink.source_note_id", back_populates="source_note")
    links_to = relationship("NoteLink", foreign_keys="NoteLink.target_note_id", back_populates="target_note")

class Folder(Base):
    __tablename__ = "folders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("folders.id"), nullable=True)
    icon = Column(String(50))
    color = Column(String(7))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    parent = relationship("Folder", remote_side=[id])
    children = relationship("Folder")
    notes = relationship("Note", back_populates="folder")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, unique=True)
    color = Column(String(7))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    notes = relationship("Note", secondary="note_tags", back_populates="tags")

class NoteTag(Base):
    __tablename__ = "note_tags"
    
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class NoteVersion(Base):
    __tablename__ = "note_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    version_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    note = relationship("Note", back_populates="versions")

class NoteLink(Base):
    __tablename__ = "note_links"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=False)
    target_note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=False)
    link_type = Column(String(50), default="reference")  # reference, citation, related
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    source_note = relationship("Note", foreign_keys=[source_note_id], back_populates="links_from")
    target_note = relationship("Note", foreign_keys=[target_note_id], back_populates="links_to")
```

#### Services

```python
# services/note_service.py
class NoteService:
    def __init__(
        self,
        repository: NoteRepository,
        ai_service: AIService,
        knowledge_service: KnowledgeService,
        event_publisher: EventPublisher
    ):
        self.repository = repository
        self.ai_service = ai_service
        self.knowledge_service = knowledge_service
        self.event_publisher = event_publisher
    
    async def create_note(
        self,
        user_id: str,
        title: str,
        content: str,
        note_type: NoteType,
        folder_id: str = None,
        tags: List[str] = None
    ) -> Note:
        # Create note
        note = await self.repository.create(
            user_id=user_id,
            title=title,
            content=content,
            note_type=note_type,
            folder_id=folder_id
        )
        
        # Add tags if provided
        if tags:
            await self._add_tags_to_note(note.id, tags)
        
        # Generate embeddings
        await self._generate_embeddings(note)
        
        # Extract entities for knowledge graph
        await self._extract_entities(note)
        
        # Publish event
        await self.event_publisher.publish(
            "note.created",
            NoteCreatedEvent(
                note_id=str(note.id),
                user_id=user_id,
                title=title
            )
        )
        
        return note
    
    async def generate_ai_title(self, note_id: str) -> str:
        note = await self.repository.get_by_id(note_id)
        
        # Generate title using AI
        title = await self.ai_service.generate_title(note.content)
        
        # Update note
        await self.repository.update(note_id, title=title, ai_generated_title=True)
        
        return title
    
    async def generate_ai_tags(self, note_id: str) -> List[str]:
        note = await self.repository.get_by_id(note_id)
        
        # Generate tags using AI
        tags = await self.ai_service.generate_tags(note.content)
        
        # Add tags to note
        await self._add_tags_to_note(note_id, tags)
        
        # Update note
        await self.repository.update(note_id, ai_generated_tags=True)
        
        return tags
    
    async def generate_ai_summary(self, note_id: str) -> str:
        note = await self.repository.get_by_id(note_id)
        
        # Generate summary using AI
        summary = await self.ai_service.generate_summary(note.content)
        
        # Update note
        await self.repository.update(note_id, ai_summary=summary)
        
        return summary
    
    async def _generate_embeddings(self, note: Note):
        # Combine title and content for embedding
        text = f"{note.title}\n\n{note.content}"
        
        # Generate embedding
        embedding = await self.ai_service.generate_embedding(text)
        
        # Store in vector database
        await self.vector_db.store(
            collection="notes",
            id=str(note.id),
            embedding=embedding,
            metadata={
                "user_id": str(note.user_id),
                "title": note.title,
                "note_type": note.note_type.value
            }
        )
    
    async def _extract_entities(self, note: Note):
        # Extract entities using AI
        entities = await self.knowledge_service.extract_entities(note.content)
        
        # Store in knowledge graph
        for entity in entities:
            await self.knowledge_service.add_entity(
                name=entity.name,
                type=entity.type,
                source_note_id=str(note.id),
                user_id=str(note.user_id)
            )
    
    async def _add_tags_to_note(self, note_id: str, tag_names: List[str]):
        for tag_name in tag_names:
            # Get or create tag
            tag = await self.tag_repository.get_or_create(
                user_id=note.user_id,
                name=tag_name
            )
            
            # Add tag to note
            await self.repository.add_tag(note_id, tag.id)
```

---

## Documents Service

### Component Design

#### Models

```python
# models/document.py
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, JSON, BigInteger, Enum
from sqlalchemy.dialects.postgresql import UUID
import enum
import uuid
from datetime import datetime

class DocumentStatus(enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class DocumentType(enum.Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    CSV = "csv"
    XLSX = "xlsx"
    PPTX = "pptx"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    ZIP = "zip"

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_type = Column(Enum(DocumentType), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_path = Column(String(1000), nullable=False)
    thumbnail_path = Column(String(1000))
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADING)
    extracted_text = Column(Text)
    metadata = Column(JSON, default={})
    ocr_required = Column(Boolean, default=False)
    ocr_completed = Column(Boolean, default=False)
    indexed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    shares = relationship("DocumentShare", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    start_page = Column(Integer)
    end_page = Column(Integer)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")

class DocumentShare(Base):
    __tablename__ = "document_shares"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    shared_with_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    share_token = Column(String(100), unique=True, nullable=True)
    permission = Column(String(50), default="view")  # view, edit, comment
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="shares")
```

#### Services

```python
# services/document_service.py
from typing import Optional, List
import aiofiles
import PyPDF2
import docx
import pandas as pd
from PIL import Image
import pytesseract
import io

class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
        storage_service: StorageService,
        ai_service: AIService,
        vector_db: VectorDatabase,
        event_publisher: EventPublisher
    ):
        self.repository = repository
        self.storage_service = storage_service
        self.ai_service = ai_service
        self.vector_db = vector_db
        self.event_publisher = event_publisher
        self.parsers = {
            DocumentType.PDF: self._parse_pdf,
            DocumentType.DOCX: self._parse_docx,
            DocumentType.TXT: self._parse_txt,
            DocumentType.CSV: self._parse_csv,
            DocumentType.XLSX: self._parse_xlsx,
            DocumentType.IMAGE: self._parse_image,
        }
    
    async def upload_document(
        self,
        user_id: str,
        file: UploadFile,
        title: str = None
    ) -> Document:
        # Determine file type
        file_type = self._determine_file_type(file.filename)
        
        # Upload to storage
        file_path = await self.storage_service.upload_file(file)
        
        # Create document record
        document = await self.repository.create(
            user_id=user_id,
            title=title or file.filename,
            file_name=file.filename,
            file_type=file_type,
            file_size=file.size,
            file_path=file_path,
            status=DocumentStatus.PROCESSING
        )
        
        # Queue processing task
        await self._queue_processing_task(document.id)
        
        # Publish event
        await self.event_publisher.publish(
            "document.uploaded",
            DocumentUploadedEvent(
                document_id=str(document.id),
                user_id=user_id,
                file_type=file_type.value
            )
        )
        
        return document
    
    async def process_document(self, document_id: str):
        document = await self.repository.get_by_id(document_id)
        
        try:
            # Update status
            await self.repository.update(document_id, status=DocumentStatus.PROCESSING)
            
            # Parse document
            parser = self.parsers.get(document.file_type)
            if parser:
                extracted_text = await parser(document.file_path)
            else:
                extracted_text = ""
            
            # OCR if needed
            if document.ocr_required and not document.ocr_completed:
                extracted_text = await self._perform_ocr(document.file_path)
                await self.repository.update(document_id, ocr_completed=True)
            
            # Store extracted text
            await self.repository.update(document_id, extracted_text=extracted_text)
            
            # Chunk document
            chunks = await self._chunk_document(document_id, extracted_text)
            
            # Generate embeddings for chunks
            await self._generate_chunk_embeddings(document_id, chunks)
            
            # Update status
            await self.repository.update(
                document_id,
                status=DocumentStatus.READY,
                indexed=True,
                processed_at=datetime.utcnow()
            )
            
            # Publish event
            await self.event_publisher.publish(
                "document.processed",
                DocumentProcessedEvent(
                    document_id=document_id,
                    user_id=str(document.user_id),
                    chunk_count=len(chunks)
                )
            )
            
        except Exception as e:
            await self.repository.update(document_id, status=DocumentStatus.FAILED)
            raise
    
    async def _parse_pdf(self, file_path: str) -> str:
        text = ""
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    async def _parse_docx(self, file_path: str) -> str:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    
    async def _parse_txt(self, file_path: str) -> str:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return await f.read()
    
    async def _parse_csv(self, file_path: str) -> str:
        df = pd.read_csv(file_path)
        return df.to_string()
    
    async def _parse_xlsx(self, file_path: str) -> str:
        df = pd.read_excel(file_path)
        return df.to_string()
    
    async def _parse_image(self, file_path: str) -> str:
        # OCR for images
        return await self._perform_ocr(file_path)
    
    async def _perform_ocr(self, file_path: str) -> str:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    
    async def _chunk_document(self, document_id: str, text: str) -> List[DocumentChunk]:
        # Chunk by character count with overlap
        chunk_size = 1000
        overlap = 200
        
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk_text = text[i:i + chunk_size]
            chunk = await self.chunk_repository.create(
                document_id=document_id,
                chunk_index=len(chunks),
                content=chunk_text
            )
            chunks.append(chunk)
        
        return chunks
    
    async def _generate_chunk_embeddings(self, document_id: str, chunks: List[DocumentChunk]):
        for chunk in chunks:
            # Generate embedding
            embedding = await self.ai_service.generate_embedding(chunk.content)
            
            # Store in vector database
            await self.vector_db.store(
                collection="document_chunks",
                id=str(chunk.id),
                embedding=embedding,
                metadata={
                    "document_id": document_id,
                    "chunk_index": chunk.chunk_index
                }
            )
```

---

## Search Service

### Component Design

#### Services

```python
# services/search_service.py
from typing import List, Optional
from enum import Enum

class SearchType(Enum):
    GLOBAL = "global"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    KEYWORD = "keyword"

class SearchService:
    def __init__(
        self,
        note_repository: NoteRepository,
        document_repository: DocumentRepository,
        vector_db: VectorDatabase,
        ai_service: AIService,
        cache: Cache
    ):
        self.note_repository = note_repository
        self.document_repository = document_repository
        self.vector_db = vector_db
        self.ai_service = ai_service
        self.cache = cache
    
    async def search(
        self,
        user_id: str,
        query: str,
        search_type: SearchType = SearchType.HYBRID,
        filters: Optional[SearchFilters] = None,
        limit: int = 20
    ) -> SearchResult:
        # Check cache
        cache_key = f"search:{user_id}:{query}:{search_type.value}:{filters}:{limit}"
        cached = await self.cache.get(cache_key)
        if cached:
            return SearchResult.parse_raw(cached)
        
        results = []
        
        if search_type in [SearchType.SEMANTIC, SearchType.HYBRID]:
            # Generate query embedding
            query_embedding = await self.ai_service.generate_embedding(query)
            
            # Vector search
            vector_results = await self._vector_search(
                user_id=user_id,
                query_embedding=query_embedding,
                filters=filters,
                limit=limit
            )
            results.extend(vector_results)
        
        if search_type in [SearchType.KEYWORD, SearchType.HYBRID]:
            # Keyword search
            keyword_results = await self._keyword_search(
                user_id=user_id,
                query=query,
                filters=filters,
                limit=limit
            )
            results.extend(keyword_results)
        
        if search_type == SearchType.HYBRID:
            # Rerank and deduplicate
            results = await self._rerank_results(query, results)
        
        # Apply limit
        results = results[:limit]
        
        # Cache results
        await self.cache.set(cache_key, results.json(), ttl=300)
        
        return SearchResult(results=results, total=len(results))
    
    async def _vector_search(
        self,
        user_id: str,
        query_embedding: List[float],
        filters: Optional[SearchFilters],
        limit: int
    ) -> List[SearchResultItem]:
        results = []
        
        # Search notes
        note_results = await self.vector_db.search(
            collection="notes",
            query_vector=query_embedding,
            filters={"user_id": user_id},
            limit=limit
        )
        
        for result in note_results:
            note = await self.note_repository.get_by_id(result.id)
            if note:
                results.append(SearchResultItem(
                    type="note",
                    id=str(note.id),
                    title=note.title,
                    content=note.content[:200],
                    score=result.score,
                    metadata={"note_type": note.note_type.value}
                ))
        
        # Search documents
        doc_results = await self.vector_db.search(
            collection="document_chunks",
            query_vector=query_embedding,
            filters={"user_id": user_id},
            limit=limit
        )
        
        for result in doc_results:
            document = await self.document_repository.get_by_id(result.metadata["document_id"])
            if document:
                results.append(SearchResultItem(
                    type="document",
                    id=str(document.id),
                    title=document.title,
                    content=result.metadata.get("content", "")[:200],
                    score=result.score,
                    metadata={"file_type": document.file_type.value}
                ))
        
        return results
    
    async def _keyword_search(
        self,
        user_id: str,
        query: str,
        filters: Optional[SearchFilters],
        limit: int
    ) -> List[SearchResultItem]:
        results = []
        
        # Search notes using PostgreSQL full-text search
        notes = await self.note_repository.search(
            user_id=user_id,
            query=query,
            filters=filters,
            limit=limit
        )
        
        for note in notes:
            results.append(SearchResultItem(
                type="note",
                id=str(note.id),
                title=note.title,
                content=note.content[:200],
                score=note.rank,
                metadata={"note_type": note.note_type.value}
            ))
        
        # Search documents
        documents = await self.document_repository.search(
            user_id=user_id,
            query=query,
            filters=filters,
            limit=limit
        )
        
        for document in documents:
            results.append(SearchResultItem(
                type="document",
                id=str(document.id),
                title=document.title,
                content=document.extracted_text[:200] if document.extracted_text else "",
                score=document.rank,
                metadata={"file_type": document.file_type.value}
            ))
        
        return results
    
    async def _rerank_results(self, query: str, results: List[SearchResultItem]) -> List[SearchResultItem]:
        # Use AI to rerank results
        if len(results) <= 1:
            return results
        
        # Prepare context for reranking
        context = "\n".join([
            f"{r.type}: {r.title} - {r.content}" 
            for r in results[:10]
        ])
        
        # Get reranking scores from AI
        rerank_scores = await self.ai_service.rerank_results(
            query=query,
            context=context,
            results=results
        )
        
        # Apply scores and sort
        for i, result in enumerate(results):
            if i < len(rerank_scores):
                result.score = rerank_scores[i]
        
        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results
```

---

## AI Service Layer

### Component Design

#### Services

```python
# services/ai_service.py
from typing import List, Optional, Dict, Any
from enum import Enum
import openai
import anthropic

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"

class ModelType(Enum):
    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"
    CLAUDE = "claude-3-opus"
    GEMINI = "gemini-pro"

class AIService:
    def __init__(self, config: Config):
        self.config = config
        self.openai_client = openai.AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
        self.cache = Cache()
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[ModelType] = None,
        provider: Optional[LLMProvider] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        # Select provider and model
        provider = provider or self._select_provider()
        model = model or self._select_model(provider)
        
        # Check cache
        cache_key = self._generate_cache_key(messages, model, temperature)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Generate response
        if provider == LLMProvider.OPENAI:
            response = await self._openai_chat(messages, model, temperature, max_tokens)
        elif provider == LLMProvider.ANTHROPIC:
            response = await self._anthropic_chat(messages, model, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Cache response
        await self.cache.set(cache_key, response, ttl=3600)
        
        return response
    
    async def _openai_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except openai.RateLimitError:
            # Fallback to another provider
            return await self._anthropic_chat(messages, "claude-3-sonnet", temperature, max_tokens)
    
    async def _anthropic_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        # Convert OpenAI format to Anthropic format
        system_message = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_messages = [m for m in messages if m["role"] in ["user", "assistant"]]
        
        response = await self.anthropic_client.messages.create(
            model=model,
            system=system_message,
            messages=user_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.content[0].text
    
    async def generate_embedding(self, text: str) -> List[float]:
        # Check cache
        cache_key = f"embedding:{hash(text)}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Generate embedding
        response = await self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        embedding = response.data[0].embedding
        
        # Cache embedding
        await self.cache.set(cache_key, embedding, ttl=86400)
        
        return embedding
    
    async def generate_title(self, content: str) -> str:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that generates concise, descriptive titles for notes and documents."
            },
            {
                "role": "user",
                "content": f"Generate a short, descriptive title (max 10 words) for the following content:\n\n{content[:500]}"
            }
        ]
        
        return await self.chat_completion(messages, temperature=0.3, max_tokens=50)
    
    async def generate_tags(self, content: str) -> List[str]:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that generates relevant tags for notes and documents. Return tags as a comma-separated list."
            },
            {
                "role": "user",
                "content": f"Generate 5-10 relevant tags for the following content:\n\n{content[:1000]}"
            }
        ]
        
        response = await self.chat_completion(messages, temperature=0.5, max_tokens=100)
        tags = [tag.strip() for tag in response.split(",")]
        return tags
    
    async def generate_summary(self, content: str) -> str:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that generates concise summaries of documents and notes."
            },
            {
                "role": "user",
                "content": f"Generate a concise summary (max 200 words) of the following content:\n\n{content}"
            }
        ]
        
        return await self.chat_completion(messages, temperature=0.5, max_tokens=300)
    
    async def rerank_results(self, query: str, context: str, results: List[SearchResultItem]) -> List[float]:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that reranks search results based on relevance to a query. Return scores as a comma-separated list of numbers between 0 and 1."
            },
            {
                "role": "user",
                "content": f"Query: {query}\n\nContext:\n{context}\n\nRerank the results by relevance. Return scores as a comma-separated list."
            }
        ]
        
        response = await self.chat_completion(messages, temperature=0.3, max_tokens=100)
        scores = [float(score.strip()) for score in response.split(",")]
        return scores
    
    def _select_provider(self) -> LLMProvider:
        # Simple round-robin or cost-based selection
        return LLMProvider.OPENAI
    
    def _select_model(self, provider: LLMProvider) -> str:
        if provider == LLMProvider.OPENAI:
            return "gpt-3.5-turbo"
        elif provider == LLMProvider.ANTHROPIC:
            return "claude-3-sonnet"
        return "gpt-3.5-turbo"
    
    def _generate_cache_key(self, messages: List[Dict], model: str, temperature: float) -> str:
        import hashlib
        content = str(messages) + model + str(temperature)
        return hashlib.md5(content.encode()).hexdigest()
```

---

## Vector Database Layer

### Component Design

#### Abstraction Layer

```python
# core/vector_db.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class VectorDatabase(ABC):
    @abstractmethod
    async def store(
        self,
        collection: str,
        id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> None:
        pass
    
    @abstractmethod
    async def search(
        self,
        collection: str,
        query_vector: List[float],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        pass
    
    @abstractmethod
    async def delete(self, collection: str, id: str) -> None:
        pass
    
    @abstractmethod
    async def update(
        self,
        collection: str,
        id: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        pass

class ChromaDBAdapter(VectorDatabase):
    def __init__(self, config: Config):
        import chromadb
        self.client = chromadb.Client()
        self.collections = {}
    
    async def store(
        self,
        collection: str,
        id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> None:
        if collection not in self.collections:
            self.collections[collection] = self.client.get_or_create_collection(collection)
        
        self.collections[collection].add(
            ids=[id],
            embeddings=[embedding],
            metadatas=[metadata]
        )
    
    async def search(
        self,
        collection: str,
        query_vector: List[float],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        if collection not in self.collections:
            return []
        
        results = self.collections[collection].query(
            query_embeddings=[query_vector],
            n_results=limit,
            where=filters
        )
        
        return [
            SearchResult(
                id=results["ids"][0][i],
                score=1 - results["distances"][0][i],  # Convert distance to similarity
                metadata=results["metadatas"][0][i]
            )
            for i in range(len(results["ids"][0]))
        ]
    
    async def delete(self, collection: str, id: str) -> None:
        if collection in self.collections:
            self.collections[collection].delete(ids=[id])
    
    async def update(
        self,
        collection: str,
        id: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        if collection not in self.collections:
            return
        
        if embedding:
            self.collections[collection].update(
                ids=[id],
                embeddings=[embedding]
            )
        
        if metadata:
            self.collections[collection].update(
                ids=[id],
                metadatas=[metadata]
            )
```

---

## Event System

### Component Design

#### Event Publisher

```python
# core/events/publisher.py
from typing import Any, Dict
import json
import pika

class EventPublisher:
    def __init__(self, config: Config):
        self.config = config
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=config.RABBITMQ_HOST)
        )
        self.channel = self.connection.channel()
    
    async def publish(self, event_type: str, event_data: Any) -> None:
        # Declare exchange
        self.channel.exchange_declare(
            exchange=event_type,
            exchange_type='fanout'
        )
        
        # Serialize event
        message = json.dumps(event_data.dict())
        
        # Publish event
        self.channel.basic_publish(
            exchange=event_type,
            routing_key='',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                timestamp=int(datetime.utcnow().timestamp())
            )
        )
    
    def close(self):
        self.connection.close()
```

#### Event Subscriber

```python
# core/events/subscriber.py
from typing import Callable, Dict
import pika
import json

class EventSubscriber:
    def __init__(self, config: Config):
        self.config = config
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=config.RABBITMQ_HOST)
        )
        self.channel = self.connection.channel()
        self.handlers: Dict[str, Callable] = {}
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        self.handlers[event_type] = handler
        
        # Declare exchange and queue
        self.channel.exchange_declare(
            exchange=event_type,
            exchange_type='fanout'
        )
        
        queue_name = f"{event_type}_queue"
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.queue_bind(exchange=event_type, queue=queue_name)
        
        # Start consuming
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=lambda ch, method, properties, body: self._handle_message(event_type, body),
            auto_ack=True
        )
    
    def _handle_message(self, event_type: str, body: bytes) -> None:
        try:
            event_data = json.loads(body)
            handler = self.handlers.get(event_type)
            if handler:
                handler(event_data)
        except Exception as e:
            print(f"Error handling event {event_type}: {e}")
    
    def start(self):
        self.channel.start_consuming()
    
    def close(self):
        self.connection.close()
```

---

## Repository Pattern

### Base Repository

```python
# repositories/base.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import TypeVar, Generic, Type, List, Optional

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get_by_id(self, id: str) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[ModelType]:
        result = await self.session.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return result.scalars().all()
    
    async def create(self, **kwargs) -> ModelType:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj
    
    async def update(self, id: str, **kwargs) -> Optional[ModelType]:
        await self.session.execute(
            update(self.model).where(self.model.id == id).values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(id)
    
    async def delete(self, id: str) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.commit()
        return result.rowcount > 0
```

---

## Configuration Management

### Configuration Class

```python
# core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Config(BaseSettings):
    # Application
    APP_NAME: str = "MEMORIA AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str
    REDIS_POOL_SIZE: int = 10
    
    # RabbitMQ
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    
    # Email
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

---

**Document Status:** Approved
**Next Review:** Q4 2026
**Owner:** Architecture Team
