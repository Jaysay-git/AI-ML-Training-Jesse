@'
# Naija Cost of Living Intelligence

An AI-powered application for exploring, comparing, and understanding essential commodity prices across selected Nigerian cities.

## Project Overview

Naija Cost of Living Intelligence helps users explore commodity prices, compare prices across locations, submit new price records, and obtain AI-assisted insights through **FoodBud AI**.

The application combines a structured price database, analytics, bulk data import, and retrieval-augmented generation (RAG) to provide an accessible cost-of-living intelligence platform.

## Key Features

### 1. Price Intelligence Dashboard
- View an overview of recorded commodity prices.
- Explore latest recorded prices.
- Analyse price distributions and trends.
- Compare commodity prices across Nigerian cities.

### 2. Price Explorer
- Filter prices by commodity, location, and date.
- Explore historical price records.
- View recorded prices and their data sources.

### 3. City Comparison
- Compare commodity prices across Lagos, Ibadan, and Abuja.
- Identify differences in recorded prices between locations.

### 4. Price Submission
- Submit individual commodity price records.
- View personal submissions.
- Edit or delete records submitted by the authenticated user.

### 5. Bulk Price Upload
- Import multiple price records using CSV or Excel files.
- Preview and validate records before importing.
- Identify invalid records and duplicates.
- Import valid records without modifying the existing simulated dataset.

Required upload columns:

`commodity, location, price, recorded_at`

Supported formats: `.csv` and `.xlsx`.

### 6. FoodBud AI

FoodBud AI provides a conversational interface for price intelligence and supporting project information.

It uses:
- Structured database tools for commodity lookups.
- Price comparison and price-change calculations.
- Retrieval-augmented generation for project documentation and supporting information.
- Authenticated PDF and TXT document uploads.
- User-scoped document retrieval.
- Gemini models for AI-generated responses, with deterministic fallback responses when the model is unavailable.

### 7. Authentication and Access Control
- User registration and login.
- Password hashing.
- JWT-based authentication.
- Rate limiting on selected endpoints.
- Users can manage only their own submitted price records.
- Seeded simulated records are read-only.

## Technology Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI |
| Frontend | Streamlit |
| Programming Language | Python |
| Database | SQLite |
| ORM | SQLAlchemy |
| Data Processing | Pandas |
| Data Visualisation | Plotly |
| Authentication | JWT |
| AI Integration | Google Gemini |
| Vector Database | ChromaDB |
| Embeddings | Google Gemini Embeddings |
| Document Processing | PyMuPDF |
| Testing | Pytest |
| Containerisation | Docker and Docker Compose |

## Dataset

The initial dataset contains **432 simulated commodity price records**.

### Dataset coverage
- Locations: Lagos, Ibadan, and Abuja.
- Commodities: 12 essential food commodities.
- Time range: January–December 2025.
- Records: 432.

The commodities include rice, beans, maize, garri, eggs, chicken, beef, fish, palm oil, vegetable oil, tomatoes, and yam.

**Important:** The initial dataset is simulated for development and demonstration purposes. It must not be interpreted as verified market prices or official Nigerian cost-of-living statistics.

User-submitted records are stored separately from the simulated records through their `data_source` classification.

See `documents/dataset_guide.md` for additional dataset information.

## Project Architecture

```text
Week 12/
│
├── app/
│   ├── agent/
│   │   ├── agent.py
│   │   ├── rag.py
│   │   └── tools.py
│   │
│   ├── api/
│   │   ├── auth.py
│   │   ├── dependencies.py
│   │   ├── prices.py
│   │   ├── analytics.py
│   │   ├── catalogue.py
│   │   ├── agent.py
│   │   └── documents.py
│   │
│   ├── core/
│   ├── database/
│   ├── schemas/
│   └── services/
│
├── data/
│   └── raw/
│       └── commodity_prices.csv
│
├── documents/
│   └── dataset_guide.md
│
├── frontend/
│   └── app.py
│
├── scripts/
│   ├── generate_dataset.py
│   ├── seed_data.py
│   └── index_documents.py
│
├── tests/
│   ├── conftest.py
│   ├── test_agent.py
│   ├── test_analytics.py
│   ├── test_auth.py
│   ├── test_documents.py
│   ├── test_price_import.py
│   └── test_rbac.py
│
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements-api.txt
└── README.md