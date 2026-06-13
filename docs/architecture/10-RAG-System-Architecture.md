# MEMORIA AI - RAG System Architecture

## Version: 1.0
## Date: June 13, 2026
## Status: Final

---

## Executive Summary

This document describes the Retrieval-Augmented Generation (RAG) system architecture for MEMORIA AI, including document processing, embedding generation, retrieval strategies, context assembly, and response generation. The RAG system enables AI to provide accurate, context-aware responses grounded in user data.

---

## Architecture Overview

### RAG Pipeline Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Document Ingestion                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Upload      │  │  Parse       │  │  Chunk       │  │  Clean       │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Embedding Generation                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Text Embed  │  │  Cache       │  │  Vector DB   │  │  Index       │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Retrieval Layer                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Query Embed │  │  Vector Srch │  │  Keyword Srch│  │  Hybrid Srch │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Reranking & Filtering                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Rerank      │  │  Filter      │  │  Deduplicate │  │  Select Top  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Context Assembly                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Compress    │  │  Order       │  │  Format      │  │  Add Citations│   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Response Generation                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Prompt      │  │  LLM Call    │  │  Process     │  │  Format      │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Document Processing Pipeline

### 1. Document Ingestion

```python
# rag/ingestion/processor.py
from typing import List, Dict, Optional
from enum import Enum

class DocumentType(Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MARKDOWN = "markdown"
    HTML = "html"

class DocumentProcessor:
    def __init__(
        self,
        parsers: Dict[DocumentType, BaseParser],
        chunker: TextChunker,
        cleaner: TextCleaner
    ):
        self.parsers = parsers
        self.chunker = chunker
        self.cleaner = cleaner
    
    async def process_document(
        self,
        file_path: str,
        document_type: DocumentType,
        metadata: Optional[Dict] = None
    ) -> ProcessedDocument:
        # Parse document
        parser = self.parsers.get(document_type)
        if not parser:
            raise ValueError(f"No parser for {document_type}")
        
        raw_text = await parser.parse(file_path)
        
        # Clean text
        cleaned_text = self.cleaner.clean(raw_text)
        
        # Chunk text
        chunks = self.chunker.chunk(cleaned_text)
        
        return ProcessedDocument(
            text=cleaned_text,
            chunks=chunks,
            metadata=metadata or {}
        )
```

### 2. Text Chunking Strategies

#### Fixed Size Chunking
```python
# rag/chunking/fixed_size.py
class FixedSizeChunker(TextChunker):
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk(self, text: str) -> List[TextChunk]:
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            chunks.append(TextChunk(
                text=chunk_text,
                start_index=start,
                end_index=end,
                metadata={"chunk_type": "fixed_size"}
            ))
            
            start = end - self.chunk_overlap
        
        return chunks
```

#### Semantic Chunking
```python
# rag/chunking/semantic.py
class SemanticChunker(TextChunker):
    def __init__(
        self,
        embedding_service: EmbeddingService,
        similarity_threshold: float = 0.85
    ):
        self.embedding_service = embedding_service
        self.similarity_threshold = similarity_threshold
    
    async def chunk(self, text: str) -> List[TextChunk]:
        # Split by sentences first
        sentences = self._split_sentences(text)
        
        # Group sentences by semantic similarity
        chunks = []
        current_chunk = [sentences[0]]
        
        for sentence in sentences[1:]:
            # Check similarity with current chunk
            chunk_text = " ".join(current_chunk)
            similarity = await self._calculate_similarity(
                chunk_text,
                sentence
            )
            
            if similarity < self.similarity_threshold:
                # Start new chunk
                chunks.append(TextChunk(
                    text=" ".join(current_chunk),
                    metadata={"chunk_type": "semantic"}
                ))
                current_chunk = [sentence]
            else:
                current_chunk.append(sentence)
        
        # Add final chunk
        if current_chunk:
            chunks.append(TextChunk(
                text=" ".join(current_chunk),
                metadata={"chunk_type": "semantic"}
            ))
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        # Use NLP to split sentences
        import nltk
        return nltk.sent_tokenize(text)
    
    async def _calculate_similarity(self, text1: str, text2: str) -> float:
        emb1 = await self.embedding_service.generate_embedding(text1)
        emb2 = await self.embedding_service.generate_embedding(text2)
        return self._cosine_similarity(emb1, emb2)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        import numpy as np
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
```

#### Recursive Chunking
```python
# rag/chunking/recursive.py
class RecursiveChunker(TextChunker):
    def __init__(
        self,
        separators: List[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.separators = separators or ["\n\n", "\n", ". ", " "]
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk(self, text: str) -> List[TextChunk]:
        return self._recursive_split(text, self.separators)
    
    def _recursive_split(self, text: str, separators: List[str]) -> List[TextChunk]:
        # Try splitting with each separator
        for separator in separators:
            if separator in text:
                parts = text.split(separator)
                
                # Check if any part is still too large
                if any(len(part) > self.chunk_size for part in parts):
                    # Recurse with next separator
                    return self._recursive_split(text, separators[separators.index(separator) + 1:])
                
                # Return chunks
                chunks = []
                for i, part in enumerate(parts):
                    if i > 0:
                        # Add overlap
                        prev_chunk = chunks[-1]
                        overlap_text = prev_chunk.text[-self.chunk_overlap:]
                        chunks[-1].text = prev_chunk.text[:-self.chunk_overlap]
                        part = overlap_text + part
                    
                    chunks.append(TextChunk(
                        text=part,
                        metadata={"chunk_type": "recursive", "separator": separator}
                    ))
                
                return chunks
        
        # No separator found, return as single chunk
        return [TextChunk(text=text, metadata={"chunk_type": "recursive"})]
```

---

## Embedding Generation

### Embedding Service

```python
# rag/embeddings/service.py
from typing import List, Dict, Optional
from enum import Enum

class EmbeddingModel(Enum):
    OPENAI_SMALL = "text-embedding-3-small"
    OPENAI_LARGE = "text-embedding-3-large"
    COHERE_EMBED = "embed-english-v3.0"
    HUGGINGFACE = "sentence-transformers/all-MiniLM-L6-v2"

class EmbeddingService:
    def __init__(
        self,
        llm_service: LLMService,
        cache: Cache,
        default_model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL
    ):
        self.llm_service = llm_service
        self.cache = cache
        self.default_model = default_model
    
    async def generate_embedding(
        self,
        text: str,
        model: Optional[EmbeddingModel] = None
    ) -> List[float]:
        model = model or self.default_model
        
        # Check cache
        cache_key = f"embedding:{model.value}:{hash(text)}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Generate embedding
        if model == EmbeddingModel.OPENAI_SMALL:
            embedding = await self._openai_embedding(text, model.value)
        elif model == EmbeddingModel.COHERE_EMBED:
            embedding = await self._cohere_embedding(text, model.value)
        else:
            embedding = await self._huggingface_embedding(text, model.value)
        
        # Cache embedding
        await self.cache.set(cache_key, embedding, ttl=86400)
        
        return embedding
    
    async def generate_embeddings_batch(
        self,
        texts: List[str],
        model: Optional[EmbeddingModel] = None
    ) -> List[List[float]]:
        # Process in batches
        batch_size = 100
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = await self._generate_batch_embeddings(batch, model)
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    async def _openai_embedding(self, text: str, model: str) -> List[float]:
        response = await self.llm_service.openai_client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
    
    async def _cohere_embedding(self, text: str, model: str) -> List[float]:
        import cohere
        co = cohere.Client(self.llm_service.config.COHERE_API_KEY)
        response = co.embed(texts=[text], model=model)
        return response.embeddings[0]
    
    async def _huggingface_embedding(self, text: str, model: str) -> List[float]:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(model)
        embedding = model.encode(text)
        return embedding.tolist()
```

---

## Retrieval Strategies

### 1. Vector Search

```python
# rag/retrieval/vector_search.py
class VectorRetriever(BaseRetriever):
    def __init__(
        self,
        vector_db: VectorDatabase,
        embedding_service: EmbeddingService,
        top_k: int = 5
    ):
        self.vector_db = vector_db
        self.embedding_service = embedding_service
        self.top_k = top_k
    
    async def retrieve(
        self,
        query: str,
        filters: Optional[Dict] = None,
        collection: str = "default"
    ) -> List[RetrievedDocument]:
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_embedding(query)
        
        # Search vector database
        results = await self.vector_db.search(
            collection=collection,
            query_vector=query_embedding,
            filters=filters,
            limit=self.top_k
        )
        
        return [
            RetrievedDocument(
                id=result.id,
                content=result.metadata.get("content", ""),
                score=result.score,
                metadata=result.metadata
            )
            for result in results
        ]
```

### 2. Keyword Search

```python
# rag/retrieval/keyword_search.py
class KeywordRetriever(BaseRetriever):
    def __init__(
        self,
        search_service: SearchService,
        top_k: int = 5
    ):
        self.search_service = search_service
        self.top_k = top_k
    
    async def retrieve(
        self,
        query: str,
        filters: Optional[Dict] = None
    ) -> List[RetrievedDocument]:
        # Perform full-text search
        results = await self.search_service.search(
            query=query,
            filters=filters,
            limit=self.top_k
        )
        
        return [
            RetrievedDocument(
                id=result.id,
                content=result.content,
                score=result.rank,
                metadata=result.metadata
            )
            for result in results
        ]
```

### 3. Hybrid Search

```python
# rag/retrieval/hybrid_search.py
class HybridRetriever(BaseRetriever):
    def __init__(
        self,
        vector_retriever: VectorRetriever,
        keyword_retriever: KeywordRetriever,
        weights: Dict[str, float] = None,
        top_k: int = 5
    ):
        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever
        self.weights = weights or {"vector": 0.7, "keyword": 0.3}
        self.top_k = top_k
    
    async def retrieve(
        self,
        query: str,
        filters: Optional[Dict] = None
    ) -> List[RetrievedDocument]:
        # Retrieve from both sources
        vector_results = await self.vector_retriever.retrieve(query, filters)
        keyword_results = await self.keyword_retriever.retrieve(query, filters)
        
        # Combine and deduplicate
        combined = self._combine_results(vector_results, keyword_results)
        
        # Return top k
        return combined[:self.top_k]
    
    def _combine_results(
        self,
        vector_results: List[RetrievedDocument],
        keyword_results: List[RetrievedDocument]
    ) -> List[RetrievedDocument]:
        # Create document map
        doc_map = {}
        
        # Add vector results
        for doc in vector_results:
            doc_map[doc.id] = {
                "document": doc,
                "vector_score": doc.score,
                "keyword_score": 0.0
            }
        
        # Add keyword results
        for doc in keyword_results:
            if doc.id in doc_map:
                doc_map[doc.id]["keyword_score"] = doc.score
            else:
                doc_map[doc.id] = {
                    "document": doc,
                    "vector_score": 0.0,
                    "keyword_score": doc.score
                }
        
        # Calculate combined scores
        combined = []
        for doc_id, data in doc_map.items():
            combined_score = (
                self.weights["vector"] * data["vector_score"] +
                self.weights["keyword"] * data["keyword_score"]
            )
            
            combined.append(RetrievedDocument(
                id=data["document"].id,
                content=data["document"].content,
                score=combined_score,
                metadata=data["document"].metadata
            ))
        
        # Sort by combined score
        combined.sort(key=lambda x: x.score, reverse=True)
        
        return combined
```

### 4. Multi-Query Retrieval

```python
# rag/retrieval/multi_query.py
class MultiQueryRetriever(BaseRetriever):
    def __init__(
        self,
        base_retriever: BaseRetriever,
        llm_service: LLMService,
        num_queries: int = 3
    ):
        self.base_retriever = base_retriever
        self.llm_service = llm_service
        self.num_queries = num_queries
    
    async def retrieve(
        self,
        query: str,
        filters: Optional[Dict] = None
    ) -> List[RetrievedDocument]:
        # Generate multiple queries
        queries = await self._generate_queries(query)
        
        # Retrieve for each query
        all_results = []
        for q in queries:
            results = await self.base_retriever.retrieve(q, filters)
            all_results.extend(results)
        
        # Deduplicate and rerank
        unique_results = self._deduplicate(all_results)
        
        return unique_results
    
    async def _generate_queries(self, query: str) -> List[str]:
        prompt = f"""Generate {self.num_queries} different search queries based on the following question:
        
Question: {query}

Queries:"""
        
        response = await self.llm_service.chat_completion([
            {"role": "system", "content": "You are a helpful assistant that generates search queries."},
            {"role": "user", "content": prompt}
        ])
        
        queries = [q.strip() for q in response.split("\n") if q.strip()]
        return queries[:self.num_queries]
    
    def _deduplicate(self, results: List[RetrievedDocument]) -> List[RetrievedDocument]:
        seen = set()
        unique = []
        
        for result in results:
            if result.id not in seen:
                seen.add(result.id)
                unique.append(result)
        
        return unique
```

### 5. Parent-Child Retrieval

```python
# rag/retrieval/parent_child.py
class ParentChildRetriever(BaseRetriever):
    def __init__(
        self,
        child_retriever: BaseRetriever,
        document_store: DocumentStore,
        top_k: int = 5
    ):
        self.child_retriever = child_retriever
        self.document_store = document_store
        self.top_k = top_k
    
    async def retrieve(
        self,
        query: str,
        filters: Optional[Dict] = None
    ) -> List[RetrievedDocument]:
        # Retrieve child chunks
        child_results = await self.child_retriever.retrieve(query, filters)
        
        # Get parent documents
        parent_docs = []
        for child in child_results:
            parent = await self.document_store.get_parent(child.id)
            if parent:
                parent_docs.append(RetrievedDocument(
                    id=parent.id,
                    content=parent.content,
                    score=child.score,
                    metadata={
                        **parent.metadata,
                        "child_id": child.id,
                        "child_score": child.score
                    }
                ))
        
        return parent_docs[:self.top_k]
```

---

## Reranking Strategies

### 1. Cross-Encoder Reranking

```python
# rag/reranking/cross_encoder.py
class CrossEncoderReranker(BaseReranker):
    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        from sentence_transformers import CrossEncoder
        self.model = CrossEncoder(model_name)
    
    async def rerank(
        self,
        query: str,
        documents: List[RetrievedDocument],
        top_k: int = 5
    ) -> List[RetrievedDocument]:
        # Prepare pairs
        pairs = [[query, doc.content] for doc in documents]
        
        # Predict scores
        scores = self.model.predict(pairs)
        
        # Update scores
        for doc, score in zip(documents, scores):
            doc.score = float(score)
        
        # Sort and return top k
        documents.sort(key=lambda x: x.score, reverse=True)
        return documents[:top_k]
```

### 2. LLM Reranking

```python
# rag/reranking/llm_reranker.py
class LLMReranker(BaseReranker):
    def __init__(
        self,
        llm_service: LLMService,
        top_k: int = 5
    ):
        self.llm_service = llm_service
        self.top_k = top_k
    
    async def rerank(
        self,
        query: str,
        documents: List[RetrievedDocument]
    ) -> List[RetrievedDocument]:
        # Prepare context
        context = "\n\n".join([
            f"Document {i+1}: {doc.content[:200]}..."
            for i, doc in enumerate(documents[:10])
        ])
        
        prompt = f"""Given the query: "{query}"
        
Rank the following documents by relevance to the query. Return only the document numbers in order of most relevant to least relevant.

{context}

Ranked documents (comma-separated):"""
        
        response = await self.llm_service.chat_completion([
            {"role": "system", "content": "You are a helpful reranking assistant."},
            {"role": "user", "content": prompt}
        ])
        
        # Parse response
        ranked_indices = [int(x.strip()) - 1 for x in response.split(",")]
        
        # Reorder documents
        reranked = [documents[i] for i in ranked_indices if i < len(documents)]
        
        return reranked[:self.top_k]
```

---

## Context Compression

### 1. Context Window Management

```python
# rag/context/compressor.py
class ContextCompressor:
    def __init__(
        self,
        max_tokens: int = 4000,
        model: str = "gpt-4"
    ):
        self.max_tokens = max_tokens
        self.model = model
        self.tokenizer = self._get_tokenizer(model)
    
    def compress(
        self,
        documents: List[RetrievedDocument],
        query: str
    ) -> str:
        # Calculate total tokens
        total_tokens = sum(
            self._count_tokens(doc.content)
            for doc in documents
        )
        
        if total_tokens <= self.max_tokens:
            # No compression needed
            return self._format_context(documents)
        
        # Compress if needed
        compressed_docs = self._compress_documents(
            documents,
            self.max_tokens
        )
        
        return self._format_context(compressed_docs)
    
    def _compress_documents(
        self,
        documents: List[RetrievedDocument],
        max_tokens: int
    ) -> List[RetrievedDocument]:
        compressed = []
        used_tokens = 0
        
        # Sort by score
        documents.sort(key=lambda x: x.score, reverse=True)
        
        for doc in documents:
            doc_tokens = self._count_tokens(doc.content)
            
            if used_tokens + doc_tokens <= max_tokens:
                compressed.append(doc)
                used_tokens += doc_tokens
            else:
                # Truncate document
                remaining_tokens = max_tokens - used_tokens
                if remaining_tokens > 100:  # Minimum tokens
                    truncated = self._truncate_to_tokens(
                        doc.content,
                        remaining_tokens
                    )
                    compressed.append(RetrievedDocument(
                        id=doc.id,
                        content=truncated,
                        score=doc.score,
                        metadata=doc.metadata
                    ))
                break
        
        return compressed
    
    def _count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))
    
    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        tokens = self.tokenizer.encode(text)
        truncated_tokens = tokens[:max_tokens]
        return self.tokenizer.decode(truncated_tokens)
    
    def _format_context(self, documents: List[RetrievedDocument]) -> str:
        context_parts = []
        
        for i, doc in enumerate(documents):
            context_parts.append(
                f"[Document {i+1}]: {doc.content}\n"
                f"[Source: {doc.metadata.get('source', 'Unknown')}]\n"
                f"[Relevance: {doc.score:.2f}]"
            )
        
        return "\n\n".join(context_parts)
    
    def _get_tokenizer(self, model: str):
        import tiktoken
        return tiktoken.encoding_for_model(model)
```

### 2. Selective Context

```python
# rag/context/selective.py
class SelectiveContextCompressor:
    def __init__(
        self,
        llm_service: LLMService,
        max_tokens: int = 4000
    ):
        self.llm_service = llm_service
        self.max_tokens = max_tokens
    
    async def compress(
        self,
        documents: List[RetrievedDocument],
        query: str
    ) -> str:
        # Use LLM to select most relevant parts
        context = "\n\n".join([
            f"Document {i+1}: {doc.content}"
            for i, doc in enumerate(documents)
        ])
        
        prompt = f"""Given the query: "{query}"

From the following documents, select and extract only the most relevant parts that directly answer the query. Be concise and focus on key information.

{context}

Relevant context:"""
        
        response = await self.llm_service.chat_completion([
            {"role": "system", "content": "You are a helpful context selector."},
            {"role": "user", "content": prompt}
        ], max_tokens=self.max_tokens)
        
        return response
```

---

## RAG Pipeline

### Complete Pipeline

```python
# rag/pipeline.py
from typing import List, Dict, Optional

class RAGPipeline:
    def __init__(
        self,
        retriever: BaseRetriever,
        reranker: Optional[BaseReranker] = None,
        compressor: Optional[ContextCompressor] = None,
        llm_service: LLMService,
        citation_generator: Optional[CitationGenerator] = None
    ):
        self.retriever = retriever
        self.reranker = reranker
        self.compressor = compressor
        self.llm_service = llm_service
        self.citation_generator = citation_generator
    
    async def run(
        self,
        query: str,
        filters: Optional[Dict] = None,
        top_k: int = 5
    ) -> RAGResponse:
        # Step 1: Retrieve documents
        documents = await self.retriever.retrieve(query, filters)
        
        # Step 2: Rerank if configured
        if self.reranker:
            documents = await self.reranker.rerank(query, documents, top_k)
        
        # Step 3: Compress context if configured
        if self.compressor:
            context = self.compressor.compress(documents, query)
        else:
            context = self._format_context(documents)
        
        # Step 4: Generate response
        response = await self._generate_response(query, context)
        
        # Step 5: Generate citations if configured
        citations = None
        if self.citation_generator:
            citations = await self.citation_generator.generate(
                response,
                documents
            )
        
        return RAGResponse(
            answer=response,
            sources=documents,
            context=context,
            citations=citations
        )
    
    async def _generate_response(self, query: str, context: str) -> str:
        prompt = f"""You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Question: {query}

Answer:"""
        
        response = await self.llm_service.chat_completion([
            {
                "role": "system",
                "content": "You are a helpful assistant that provides accurate answers based on the given context. Always cite your sources."
            },
            {
                "role": "user",
                "content": prompt
            }
        ])
        
        return response
    
    def _format_context(self, documents: List[RetrievedDocument]) -> str:
        context_parts = []
        
        for i, doc in enumerate(documents):
            context_parts.append(
                f"[Document {i+1}]: {doc.content}\n"
                f"[Source: {doc.metadata.get('source', 'Unknown')}]"
            )
        
        return "\n\n".join(context_parts)
```

---

## Citation Generation

### Citation Generator

```python
# rag/citations/generator.py
class CitationGenerator:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    async def generate(
        self,
        response: str,
        documents: List[RetrievedDocument]
    ) -> List[Citation]:
        # Extract claims from response
        claims = await self._extract_claims(response)
        
        # Find supporting documents for each claim
        citations = []
        for claim in claims:
            supporting_docs = await self._find_supporting_documents(
                claim,
                documents
            )
            
            if supporting_docs:
                citations.append(Citation(
                    claim=claim,
                    sources=[doc.id for doc in supporting_docs],
                    confidence=self._calculate_confidence(supporting_docs)
                ))
        
        return citations
    
    async def _extract_claims(self, text: str) -> List[str]:
        prompt = f"""Extract the key factual claims from the following text. Return each claim on a separate line.

Text: {text}

Claims:"""
        
        response = await self.llm_service.chat_completion([
            {
                "role": "system",
                "content": "You are a helpful assistant that extracts factual claims."
            },
            {
                "role": "user",
                "content": prompt
            }
        ])
        
        claims = [claim.strip() for claim in response.split("\n") if claim.strip()]
        return claims
    
    async def _find_supporting_documents(
        self,
        claim: str,
        documents: List[RetrievedDocument]
    ) -> List[RetrievedDocument]:
        # Use semantic similarity to find supporting documents
        supporting = []
        
        for doc in documents:
            similarity = await self._calculate_similarity(claim, doc.content)
            if similarity > 0.7:  # Threshold
                supporting.append(doc)
        
        return supporting
    
    async def _calculate_similarity(self, text1: str, text2: str) -> float:
        # Simple implementation - use embeddings in production
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _calculate_confidence(self, documents: List[RetrievedDocument]) -> float:
        # Average score of supporting documents
        if not documents:
            return 0.0
        return sum(doc.score for doc in documents) / len(documents)
```

---

## Advanced RAG Techniques

### 1. Query Expansion

```python
# rag/advanced/query_expansion.py
class QueryExpander:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    async def expand(self, query: str) -> List[str]:
        prompt = f"""Generate 3 different variations of the following query to improve search results. Each variation should focus on different aspects or use different terminology.

Original query: {query}

Expanded queries (one per line):"""
        
        response = await self.llm_service.chat_completion([
            {
                "role": "system",
                "content": "You are a helpful assistant that generates search query variations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ])
        
        queries = [q.strip() for q in response.split("\n") if q.strip()]
        return queries[:3]
```

### 2. Knowledge Graph Retrieval

```python
# rag/advanced/kg_retrieval.py
class KnowledgeGraphRetriever(BaseRetriever):
    def __init__(
        self,
        knowledge_graph: KnowledgeGraph,
        embedding_service: EmbeddingService,
        top_k: int = 5
    ):
        self.knowledge_graph = knowledge_graph
        self.embedding_service = embedding_service
        self.top_k = top_k
    
    async def retrieve(
        self,
        query: str,
        filters: Optional[Dict] = None
    ) -> List[RetrievedDocument]:
        # Extract entities from query
        entities = await self._extract_entities(query)
        
        # Query knowledge graph
        related_entities = []
        for entity in entities:
            related = await self.knowledge_graph.get_related_entities(
                entity,
                filters
            )
            related_entities.extend(related)
        
        # Convert to documents
        documents = []
        for entity in related_entities[:self.top_k]:
            documents.append(RetrievedDocument(
                id=entity.id,
                content=entity.description,
                score=entity.relevance_score,
                metadata={
                    "type": "knowledge_graph",
                    "entity_type": entity.type
                }
            ))
        
        return documents
    
    async def _extract_entities(self, text: str) -> List[str]:
        # Use NLP to extract entities
        # Simplified implementation
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        
        entities = [ent.text for ent in doc.ents]
        return entities
```

### 3. Self-Query Retrieval

```python
# rag/advanced/self_query.py
class SelfQueryRetriever(BaseRetriever):
    def __init__(
        self,
        base_retriever: BaseRetriever,
        llm_service: LLMService,
        metadata_schema: Dict
    ):
        self.base_retriever = base_retriever
        self.llm_service = llm_service
        self.metadata_schema = metadata_schema
    
    async def retrieve(
        self,
        query: str,
        filters: Optional[Dict] = None
    ) -> List[RetrievedDocument]:
        # Extract filters from query
        extracted_filters = await self._extract_filters(query)
        
        # Merge with provided filters
        if filters:
            extracted_filters.update(filters)
        
        # Retrieve with filters
        return await self.base_retriever.retrieve(query, extracted_filters)
    
    async def _extract_filters(self, query: str) -> Dict:
        schema_str = "\n".join([
            f"{key}: {value}" for key, value in self.metadata_schema.items()
        ])
        
        prompt = f"""Extract metadata filters from the following query based on the schema.

Schema:
{schema_str}

Query: {query}

Return filters as JSON:"""
        
        response = await self.llm_service.chat_completion([
            {
                "role": "system",
                "content": "You are a helpful assistant that extracts metadata filters."
            },
            {
                "role": "user",
                "content": prompt
            }
        ])
        
        import json
        try:
            filters = json.loads(response)
            return filters
        except:
            return {}
```

---

## Evaluation

### RAG Evaluation Metrics

```python
# rag/evaluation/metrics.py
class RAGEvaluator:
    def __init__(
        self,
        llm_service: LLMService
    ):
        self.llm_service = llm_service
    
    async def evaluate(
        self,
        query: str,
        response: str,
        ground_truth: str,
        retrieved_docs: List[RetrievedDocument]
    ) -> RAGEvaluationResult:
        # Faithfulness
        faithfulness = await self._evaluate_faithfulness(
            response,
            retrieved_docs
        )
        
        # Answer relevance
        relevance = await self._evaluate_relevance(
            query,
            response,
            ground_truth
        )
        
        # Context precision
        precision = await self._evaluate_context_precision(
            query,
            retrieved_docs,
            ground_truth
        )
        
        # Context recall
        recall = await self._evaluate_context_recall(
            query,
            retrieved_docs,
            ground_truth
        )
        
        return RAGEvaluationResult(
            faithfulness=faithfulness,
            answer_relevance=relevance,
            context_precision=precision,
            context_recall=recall
        )
    
    async def _evaluate_faithfulness(
        self,
        response: str,
        docs: List[RetrievedDocument]
    ) -> float:
        context = "\n".join([doc.content for doc in docs])
        
        prompt = f"""Evaluate if the following response is faithful to the provided context. Return a score between 0 and 1.

Response: {response}

Context: {context}

Score:"""
        
        response = await self.llm_service.chat_completion([
            {
                "role": "system",
                "content": "You are a helpful evaluator."
            },
            {
                "role": "user",
                "content": prompt
            }
        ])
        
        try:
            return float(response.strip())
        except:
            return 0.0
    
    async def _evaluate_relevance(
        self,
        query: str,
        response: str,
        ground_truth: str
    ) -> float:
        prompt = f"""Evaluate the relevance of the response to the query compared to the ground truth. Return a score between 0 and 1.

Query: {query}

Response: {response}

Ground Truth: {ground_truth}

Score:"""
        
        response = await self.llm_service.chat_completion([
            {
                "role": "system",
                "content": "You are a helpful evaluator."
            },
            {
                "role": "user",
                "content": prompt
            }
        ])
        
        try:
            return float(response.strip())
        except:
            return 0.0
```

---

## Best Practices

### 1. Chunking
- Use semantic chunking for better coherence
- Maintain appropriate overlap (10-20%)
- Consider document type when choosing strategy
- Test different chunk sizes for optimal results

### 2. Embeddings
- Choose appropriate embedding model for your use case
- Cache embeddings to reduce costs
- Use batch processing for efficiency
- Monitor embedding quality

### 3. Retrieval
- Use hybrid search for better results
- Implement reranking for precision
- Use multi-query for complex queries
- Consider knowledge graph for context

### 4. Context
- Compress context to fit token limits
- Prioritize high-relevance documents
- Include source information
- Use selective context for efficiency

### 5. Evaluation
- Evaluate on multiple metrics
- Use human evaluation for quality
- Monitor retrieval quality over time
- A/B test different strategies

---

**Document Status:** Approved
**Next Review:** Q4 2026
**Owner:** AI Architecture Team
