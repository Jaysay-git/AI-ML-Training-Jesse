# Week 8 — RAG Document Ingestion and Retrieval

## Overview

This week's project extends the Hospital Patient Tracker into a Retrieval-Augmented Generation (RAG) document ingestion and retrieval pipeline.

The pipeline supports:

1. Secure document upload
2. PDF and TXT text extraction
3. Two chunking strategies
4. Gemini embeddings
5. Chroma vector storage
6. Metadata for source and page tracking
7. Semantic search
8. Strategy-specific retrieval
9. Automated testing

The implementation was evaluated using a three-page employee Q2 review PDF.

---

## RAG Pipeline

Document Upload
       ↓
File Validation
       ↓
Text Extraction
       ↓
Chunking
   ↙         ↘
Fixed       Paragraph
   ↓           ↓
Embedding Generation
       ↓
Chroma Vector Store
       ↓
Semantic Search
       ↓
Retrieved Chunks + Metadata


---

## 1. Secure Document Upload

The API provides:


POST /documents/upload

Supported file types:

* PDF
* TXT

The upload implementation applies several security controls:

### File type restriction

Only `.pdf` and `.txt` extensions are accepted.

Unsupported files receive a `400 Bad Request`.

### File size restriction

The maximum upload size is:

5 MB


Files exceeding this limit are rejected.

### Path traversal protection

Uploaded filenames are sanitized using:


Path(file.filename or "uploaded_file").name


This prevents filenames such as:


../../evil.txt


from creating files outside the upload directory.

### No SSRF through document ingestion

The ingestion pipeline accepts local uploaded files rather than remote URLs. It does not fetch arbitrary URLs supplied by users.

---

## 2. Text Extraction

PDF documents are processed using PyMuPDF.

The PDF extraction process preserves page numbers:


{
    "page": 1,
    "text": "..."
}


This allows retrieved chunks to retain information about which PDF page they originated from.

The test document contains:


3 pages


The extraction tests confirmed that all three pages are successfully extracted and that the combined page-aware text matches the standard text extraction output.

---

## 3. Chunking Strategies

Two chunking strategies were implemented and evaluated using the same document.

### Strategy A — Fixed-size chunking

Fixed-size chunking uses:


Chunk size: 500 characters
Overlap: 50 characters


The overlap helps preserve context between adjacent chunks.

The test document produced:


7 fixed-size chunks


#### Advantages

* Simple to implement
* Predictable chunk sizes
* Consistent processing
* Overlap helps preserve information near boundaries
* Strong semantic matching in the retrieval experiment

#### Disadvantages

Character-based boundaries can split:

* words
* sentences
* questions
* answers

For example, retrieved chunks contained fragments such as:


"d benefit you in the..."


and:


"xt quarter?:"


This reduces readability and can separate related question-and-answer content.

---

### Strategy B — Paragraph-based chunking

Paragraph-based chunking attempts to preserve natural paragraph boundaries while enforcing a maximum size of:


1,000 characters


The same document produced:


4 paragraph-based chunks


#### Advantages

* Preserves natural text boundaries
* Keeps related questions and answers together
* Produces more coherent retrieval units
* Easier for a user to read and interpret

#### Disadvantages

* Chunk sizes are less uniform
* Very large paragraphs still need to be split
* May produce larger chunks than fixed-size chunking

---

## 4. Chunking Comparison

The same query was used for both strategies:

> What training and development does the employee want in the next quarter?

### Fixed-size retrieval

Top three distances:

| Rank | Distance | Page(s) |
| ---- | -------: | ------- |
| 1    |   0.4466 | 2, 3    |
| 2    |   0.4801 | 2       |
| 3    |   0.6206 | 2       |

The first result contained the actual answer:

> The development of the use of Artificial Intelligence. How to use, how to build, how to deploy.

However, the chunk began in the middle of a sentence, demonstrating the effect of fixed character boundaries.

### Paragraph-based retrieval

Top three distances:

| Rank | Distance | Page(s) |
| ---- | -------: | ------- |
| 1    |   0.5237 | 2, 3    |
| 2    |   0.6107 | 3       |
| 3    |   0.6120 | 2       |

The top paragraph chunk contained the complete surrounding Q&A context, including questions 16–19.

### Evaluation

Fixed-size chunking produced lower embedding distances for this query, indicating stronger raw semantic similarity.

However, lower distance alone does not determine whether a chunk is more useful. The fixed-size results contained text fragments caused by character-based boundaries.

Paragraph-based chunking produced higher distances but preserved more complete question-and-answer context and produced more interpretable retrieval results.

### Selected strategy

For this particular Q&A document, **paragraph-based chunking was selected as the more useful strategy** because the document is structured around questions and answers. Preserving those natural boundaries improves readability and provides better contextual units for retrieval and citations.

Fixed-size chunking remains useful as a baseline because it is simple, predictable, and produced strong semantic similarity.

---

## 5. Embeddings

Gemini's embedding model was used to convert each chunk into a numerical vector:


gemini-embedding-001


The generated embeddings have:

3072 dimensions


The same embedding process is used for both document chunks and search queries.

This allows semantic similarity to be calculated between the user's query and stored document chunks.

---

## 6. Vector Store

Chroma was selected as the vector database for this week's implementation.

The collection uses persistent local storage:


./chroma_db


Each stored chunk contains:

* document text
* embedding
* filename
* chunk index
* source path
* chunking strategy
* page numbers

The vector store currently contains:


4 paragraph chunks
7 fixed-size chunks
--------------------
11 total chunks


---

## 7. Metadata and Citations

Each chunk stores metadata similar to:


{
  "filename": "Jesse Osifade - (Q2).pdf",
  "chunk_index": 2,
  "source": "uploads/Jesse Osifade - (Q2).pdf",
  "chunking_strategy": "paragraph",
  "pages": "2,3"
}


This metadata makes retrieved information traceable to its original document and page.

Page information is particularly useful for future RAG responses because an answer can reference the source page rather than only returning generated text.

---

## 8. Search API

Semantic search is available through:


POST /documents/search


The endpoint supports:

* query text
* number of results
* chunking strategy filtering

The number of results is restricted to:


1–10


The strategy can be:

paragraph
fixed


This makes it possible to compare retrieval performance between the two chunking approaches.

---

## 9. Automated Testing

The Week 8 implementation contains tests covering the major parts of the pipeline.

### Test results


Chunking tests:       5 passed
PDF ingestion:        2 passed
Search endpoint:      4 passed
Upload security:      3 passed
Vector store:         4 passed
--------------------------------
Total:               18 passed


Final test command:


python -m pytest tests -v


Result:


18 passed


The tests verify:

* fixed-size chunk creation
* chunk overlap
* empty input handling
* paragraph chunking
* PDF page extraction
* search validation
* strategy filtering
* upload type restrictions
* upload size restrictions
* path traversal protection
* vector-store metadata
* expected chunk counts

---

## 10. Final Assessment

The Week 8 implementation demonstrates a complete document ingestion and retrieval pipeline:


Upload
  ↓
Validation
  ↓
Text Extraction
  ↓
Chunking
  ↓
Embedding
  ↓
Vector Storage
  ↓
Semantic Search
  ↓
Metadata + Source Information


The comparison demonstrated that chunking strategy affects both semantic retrieval and the usefulness of retrieved context.

For the evaluated employee Q&A document, paragraph-based chunking produced more coherent retrieval units because it preserved natural question-and-answer boundaries. Fixed-size chunking provided a useful baseline and achieved lower embedding distances for the test query, but its character boundaries sometimes split words and sentences.

The resulting system provides a foundation for future RAG functionality, where retrieved chunks can be passed to an LLM to generate grounded answers with document and page references.
