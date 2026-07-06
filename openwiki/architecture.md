## Hotel Room Standardizer Architecture

### Core Components
1. **API Layer**
   - Implemented via FastAPI for RESTful endpoints
   - Central endpoint: `app/main.py` with root route `/`

2. **Database Layer**
   - SQLite storage via SQLAlchemy ORM
   - Database initialization in `app/database.py`
   - Models defined in `app/models.py` (SQLAlchemy declarative base)

3. **Service Layer**
   - Business logic in `app/services/` directory
   - Current services:
     - `/services/loader.py`: Data loading
     - `/services/matcher.py`: Room matching logic

4. **Configuration**
   - Environment-agnostic setup
   - Database engine created at startup: `Base.metadata.create_all(bind=ENGINE)`

### Project Structure
