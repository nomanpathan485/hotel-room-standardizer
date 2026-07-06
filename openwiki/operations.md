# Operations Guide

## Running the Application

### Initial Setup
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize database**
   ```python
   # In app/database.py, the table is created automatically on startup
   # or manually run: python -c "from app.models import Base; from app.database import ENGINE; Base.metadata.create_all(bind=ENGINE)"
   ```

3. **Import room data**
   ```bash
   # The loader service can be run to import rooms.json data
   # This script is designed to load supplier data into the database
   ```

### Usage

#### Running the API
To run the FastAPI application:
```bash
uvicorn app.main:app
```

The application exposes:
- `GET /`: Health check endpoint returning "Hotel room standardizer API is running!"

### Data Flow

1. **Import Phase**: Use `app/services/loader.py` to import JSON data from `data/rooms.json`
2. **Processing Phase**: Implement matching logic in `app/services/matcher.py`
3. **Storage**: Data persists in SQLite database `hotel.db`
4. **API Access**: REST endpoints provide read/ write access to the stored data

### Business Operations

- **Room Standardization**: Different suppliers describe rooms with varying names
- **Data Matching**: Match similar room names across different suppliers
- **Standard Naming**: Generate consistent room names for downstream systems
- **Data Persistence**: Store matched room data for future reference

### Monitoring

- Database connection handling is implemented in `app/database.py`
- The application includes error handling for database operations
- All operations are transaction-based with rollback on exceptions