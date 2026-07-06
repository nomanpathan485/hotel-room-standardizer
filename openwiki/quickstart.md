## Hotel Room Standardizer Documentation

This repository standardizes hotel room names from different suppliers. Key components:

- **Tech Stack**: Python, FastAPI, SQLite, SQLAlchemy
- **Purpose**: Store supplier data, perform room matching, and generate standardized names
- **Status**: Project setup complete, development ongoing

### Getting Started
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Initialize SQLite database: `python app/database.py init`
4. Run FastAPI server: `uvicorn app.main:app`

### Core Architecture
- [Architecture overview](/openwiki/architecture.md)
- [Data models](/openwiki/data-models.md)
- [API endpoints](/openwiki/api.md)
- [Matching algorithm](/openwiki/matching.md)