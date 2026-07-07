# Hotel Room Standardizer

![GitHub repo size](https://img.shields.io/github/repo-size/nomanpathan485/hotel-room-standardizer)
![GitHub language count](https://img.shields.io/github/languages/count/nomanpathan485/hotel-room-standardizer)
![GitHub top language](https://img.shields.io/github/languages/top/nomanpathan485/hotel-room-standardizer)
![GitHub last commit](https://img.shields.io/github/last-commit/nomanpathan485/hotel-room-standardizer)
![GitHub issues](https://img.shields.io/github/issues/nomanpathan485/hotel-room-standardizer)
![GitHub license](https://img.shields.io/github/license/nomanpathan485/hotel-room-standardizer)

## Overview

This project is being developed as part of an AI & Data Science internship.

The goal is to standardize hotel room names received from different suppliers. Different suppliers may describe the same room using different names. This backend system will store supplier data, perform room matching, and generate standardized room names.

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** SQLite with SQLAlchemy ORM
- **Version Control:** Git & GitHub
- **Data Format:** JSON (supplier data)
- **API:** RESTful endpoints

## Project Status

- [x] Project setup completed
- [x] Database models defined
- [x] Supplier data loaded into SQLite
- [x] Basic FastAPI endpoint (`/`) operational
- [x] `GET /rooms` endpoint returning list of rooms
- [x] Pydantic response schemas defined
- [x] Project structured into `routers`, `services`, and `models` modules
- [ ] Room matching algorithm implementation (`app/services/matcher.py` is a placeholder)
- [ ] Standardized room name generation
- [ ] API endpoints for matching, retrieval, update, and delete
- [ ] API documentation (Swagger UI)
- [ ] Testing suite
- [ ] Deployment preparation

## Architecture

```mermaid
graph TD
    A["Supplier Data (JSON)"] --> B["Data Loader"]
    B --> C["SQLite Database"]
    C --> D["Matching Service"]
    D --> E["Standardized Room Names"]
    E --> F["FastAPI Endpoints"]
    F --> G["Consumers / Frontend"]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#9f6,stroke:#333,stroke-width:2px
```

## Project Structure

```
hotel-room-standardizer/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLAlchemy engine & session
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemes.py           # Pydantic response/request schemas
│   ├── routers/
│   │   └── rooms.py         # Room-related API routes
│   └── services/
│       ├── loader.py        # JSON → DB loader
│       └── matcher.py       # Room matching (not yet implemented)
├── data/
│   └── rooms.json           # Supplier room data
├── hotel.db                 # SQLite database
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/nomanpathan485/hotel-room-standardizer.git
   cd hotel-room-standardizer
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure the data file exists (`data/rooms.json`). It should already be present.

5. (Optional) Reload supplier data into the database by running the loader:
   ```bash
   python -m app.services.loader
   ```

6. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

7. Open your browser at `http://127.0.0.1:8000` to see the welcome message, or visit `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

## Usage

- The API currently provides:
  - `GET /` – Welcome message confirming the API is running.
  - `GET /rooms` – Returns a JSON list of all rooms currently stored in the database.
- Future endpoints will include:
  - `POST /rooms/match` – Submit a room name and receive standardized suggestions.
  - `GET /rooms/{id}` – Retrieve a specific room record.
  - `PUT /rooms/{id}` – Update a room record.
  - `DELETE /rooms/{id}` – Delete a room record.

## API Endpoints

| Method | Endpoint          | Status        | Description                          |
|--------|-------------------|---------------|--------------------------------------|
| GET    | `/`               | ✅ Implemented | Welcome message                      |
| GET    | `/rooms`          | ✅ Implemented | List all stored rooms                |
| GET    | `/rooms/{id}`     | ⏳ Planned     | Get a specific room by ID            |
| POST   | `/rooms/match`    | ⏳ Planned     | Match a supplier room name to standard |
| PUT    | `/rooms/{id}`     | ⏳ Planned     | Update a room record                 |
| DELETE | `/rooms/{id}`     | ⏳ Planned     | Delete a room record                 |

## Roadmap

- [ ] Implement fuzzy matching algorithm in `app/services/matcher.py` (e.g., fuzzywuzzy, rapidfuzz, or custom NLP)
- [ ] Develop standardization logic (canonical room names)
- [ ] Add remaining CRUD endpoints for rooms
- [ ] Add comprehensive API documentation with Swagger UI
- [ ] Write unit and integration tests
- [ ] Dockerize the application
- [ ] Deploy to a cloud platform (e.g., Heroku, Render, or AWS)

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

Please ensure your code follows the project's style and includes appropriate tests.

## License

This project is intended to be licensed under the MIT License. A `LICENSE` file has not yet been added to the repository — please add one before publishing or accepting external contributions.

---

*Made with ❤️ during the AI & Data Science internship.*
