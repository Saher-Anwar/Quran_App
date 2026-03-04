# Quran App Backend

FastAPI backend with PostgreSQL database that supports Arabic language with diacritics.

## Backend Package Structure Template
- `constants.py`: Module specific constants and error codes
- `dependencies.py`: Router dependencies
- `exceptions.py`: Module specific exceptions, e.g. PostNotFound, InvalidUserData
- `models.py`: Database models
- `router.py`: Core of each module with all the endpoints
- `schemas.py`: Pdantic models
- `service.py`: Module specific business logic
- `utils.py`: Non-business logic functions, e.g. response normalization, data enrichment, etc

## Features

- FastAPI for high-performance REST API
- PostgreSQL with full UTF-8 support for Arabic text with diacritics
- Alembic for database migrations
- Docker Compose for easy development setup
- Async database operations with SQLAlchemy

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

## Quick Start

### Using Docker Compose (Recommended)

1. Start the services:
```bash
docker-compose up -d
```

2. Run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

3. Access the API:
- API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Local Development (Without Docker)

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Update `.env` file with local database settings:
```env
DATABASE_URL=postgresql://admin:admin@localhost:5432/quran_db
ASYNC_DATABASE_URL=postgresql+asyncpg://admin:admin@localhost:5432/quran_db
```

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the development server:
```bash
uvicorn src.main:app --reload
```

## Database Migrations

### Create a new migration:
```bash
# With Docker
docker-compose exec backend alembic revision --autogenerate -m "description"

# Local
alembic revision --autogenerate -m "description"
```

### Apply migrations:
```bash
# With Docker
docker-compose exec backend alembic upgrade head

# Local
alembic upgrade head
```

### Rollback migration:
```bash
# With Docker
docker-compose exec backend alembic downgrade -1

# Local
alembic downgrade -1
```

## Project Structure

```
backend/
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py           # Alembic configuration
├── src/
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration settings
│   ├── database.py      # Database connection
│   └── models.py        # SQLAlchemy models
├── tests/               # Test files
├── .env                 # Environment variables (not in git)
├── alembic.ini         # Alembic settings
├── Dockerfile          # Docker image definition
└── requirements.txt    # Python dependencies
```

## Database Configuration

The PostgreSQL database is configured with:
- UTF-8 encoding for proper Arabic text storage
- `en_US.UTF-8` locale for character support
- pg_trgm extension for text search
- uuid-ossp extension for UUID support

Database credentials:
- User: `admin`
- Password: `admin`
- Database: `quran_db`
- Port: `5432`

## Example Models

The project includes example models for storing Quranic data:

- **Surah**: Stores chapter information with Arabic names
- **Verse**: Stores verses with Arabic text (with and without diacritics)

## API Endpoints

- `GET /` - Health check
- `GET /health` - Service health status
- `GET /api/docs` - Swagger UI documentation
- `GET /api/redoc` - ReDoc documentation

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql://admin:admin@postgres:5432/quran_db |
| ASYNC_DATABASE_URL | Async PostgreSQL connection | postgresql+asyncpg://admin:admin@postgres:5432/quran_db |
| APP_NAME | Application name | Quran App API |
| DEBUG | Debug mode | True |

## Stopping Services

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (careful: deletes database data)
docker-compose down -v
```

## Troubleshooting

### Database connection errors
- Ensure PostgreSQL container is healthy: `docker-compose ps`
- Check logs: `docker-compose logs postgres`

### Migration errors
- Ensure models are imported in `alembic/env.py`
- Check database connectivity
- Verify migration files in `alembic/versions/`

### Arabic text not displaying correctly
- Verify database encoding: `SHOW SERVER_ENCODING;` (should be UTF8)
- Check client encoding in connection string
