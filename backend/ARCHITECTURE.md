# Backend Architecture

Clean architecture implementation with clear separation of concerns.

## Structure

```
backend/
├── app/
│   ├── api/                    # API Layer (Controllers)
│   │   ├── routes/
│   │   │   ├── health.py       # Health check endpoints
│   │   │   └── matching.py     # Matching endpoints
│   │   └── dependencies.py     # Dependency injection
│   │
│   ├── core/                   # Core Configuration
│   │   ├── config.py           # Settings management
│   │   └── exceptions.py       # Custom exceptions
│   │
│   ├── domain/                 # Domain Layer
│   │   ├── models.py           # Domain models
│   │   └── schemas.py          # Request/Response schemas
│   │
│   ├── services/               # Business Logic Layer
│   │   ├── matching_service.py # Resume matching logic
│   │   └── scraper_service.py  # Job scraping logic
│   │
│   ├── infrastructure/         # Infrastructure Layer
│   │   ├── cache/
│   │   │   └── redis_cache.py  # Redis implementation
│   │   ├── ml/
│   │   │   └── model_loader.py # ML model management
│   │   └── telegram/
│   │       └── scraper.py      # Telegram client
│   │
│   ├── utils/                  # Utilities
│   │   └── text_processing.py  # Text cleaning & PII removal
│   │
│   └── main.py                 # Application entry point
│
├── tests/                      # Tests
│   └── test_api.py             # API tests
│
├── .env                        # Environment variables
├── requirements.txt            # Dependencies
└── run_server.sh               # Startup script
```

## Layers

### 1. API Layer (`app/api/`)
- **Responsibility:** HTTP request/response handling
- **Components:**
  - Routes: Define endpoints
  - Dependencies: Dependency injection for services
- **Rules:**
  - No business logic
  - Only handles HTTP concerns
  - Delegates to services

### 2. Domain Layer (`app/domain/`)
- **Responsibility:** Core business entities and contracts
- **Components:**
  - Models: Domain entities (Job, MatchResult)
  - Schemas: API contracts (Request/Response models)
- **Rules:**
  - No external dependencies
  - Pure data structures
  - Framework-agnostic

### 3. Services Layer (`app/services/`)
- **Responsibility:** Business logic orchestration
- **Components:**
  - MatchingService: Resume-job matching logic
  - ScraperService: Job scraping orchestration
- **Rules:**
  - Coordinates between infrastructure and domain
  - Contains business rules
  - No HTTP concerns

### 4. Infrastructure Layer (`app/infrastructure/`)
- **Responsibility:** External integrations
- **Components:**
  - Cache: Redis implementation
  - ML: Model loading and inference
  - Telegram: Scraper implementation
- **Rules:**
  - Implements technical details
  - Can be swapped out
  - No business logic

### 5. Core (`app/core/`)
- **Responsibility:** Cross-cutting concerns
- **Components:**
  - Config: Application settings
  - Exceptions: Custom error types
- **Rules:**
  - Used by all layers
  - No layer-specific logic

### 6. Utils (`app/utils/`)
- **Responsibility:** Shared utilities
- **Components:**
  - Text processing functions
  - PII removal
  - Job title extraction
- **Rules:**
  - Pure functions
  - No state
  - Reusable

## Dependency Flow

```
API Layer
    ↓
Services Layer
    ↓
Infrastructure Layer
    ↓
External Systems (Redis, Telegram, ML Model)
```

## Key Principles

1. **Dependency Inversion:** High-level modules don't depend on low-level modules
2. **Single Responsibility:** Each module has one reason to change
3. **Separation of Concerns:** Clear boundaries between layers
4. **Testability:** Easy to mock and test each layer
5. **Maintainability:** Changes in one layer don't affect others

## Running

```bash
# Start server
./run_server.sh

# Run tests
python3 tests/test_api.py
```

## Adding New Features

1. **New endpoint:** Add route in `app/api/routes/`
2. **New business logic:** Add service in `app/services/`
3. **New external integration:** Add to `app/infrastructure/`
4. **New domain entity:** Add to `app/domain/models.py`
5. **New API contract:** Add to `app/domain/schemas.py`
