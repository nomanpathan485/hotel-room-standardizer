# Engineering Journal

## Day 1 - Project Setup

### Goal
Build a backend system to standardize hotel room names from different suppliers.

### Completed
- Created project structure.
- Created Python virtual environment.
- Installed project dependencies.
- Initialized Git repository.
- Connected project to GitHub.
- Created `.gitignore`.
- Set up FastAPI.
- Set up SQLite database.
- Configured SQLAlchemy ORM.

### Learned
- What FastAPI is.
- What SQLite is.
- What SQLAlchemy ORM is.
- Difference between ORM and raw SQL.
- Purpose of `Base`, `ENGINE`, and `SessionLocal`.

---

## Day 2 - Database Design

### Completed
Created the `Room` model with:

- id
- supplier_code
- supplier_name
- supplier_room_name
- standard_room_name

### Learned
- Primary Keys
- SQLAlchemy models
- Database tables
- Why `standard_room_name` is nullable initially

### Problems Faced
- SQLAlchemy type errors
- Wrong import (`string` instead of `String`)
- Missing database table

### Solution
Fixed imports and recreated the database.

---

## Day 3 - Importing Data

### Completed
- Created `import_rooms()` service.
- Read room data from JSON.
- Inserted all supplier room names into SQLite.
- Successfully imported 103 room records.

### Learned
- Reading JSON files.
- Creating SQLAlchemy objects.
- Using `db.add()`.
- Using `db.commit()`.
- Rolling back transactions on errors.

### Problems Faced
- Duplicate imports
- Database recreation
- Deleted test records

### Solution
Recreated the database and re-imported the JSON.

---

## Day 4 - FastAPI CRUD

### Completed

Implemented API endpoints:

- GET room by ID
- POST room
- PUT room
- DELETE room

### Learned

- Request vs Response
- Response Models
- Dependency Injection (`Depends`)
- Database sessions
- HTTP methods
- Response validation

### Problems Faced

- ResponseValidationError
- Internal Server Error
- Method Not Allowed
- Missing records

### Solution

Debugged each issue and fixed endpoint logic.

---

## Day 5 - Text Normalization

### Goal

Prepare room names for matching.

### Implemented

- Convert to lowercase.
- Replace hyphens with spaces.
- Remove extra spaces.

Example:

Input:

Bed in 6-Bed Mixed Dormitory

Output:

bed in 6 bed mixed dormitory

### Learned

Normalization reduces differences caused only by formatting.

---

## Day 6 - Dataset Exploration

### Goal

Understand the room-name dataset before designing matching rules.

### Completed

Loaded every room from the database and analyzed the dataset.

### Observations

Found many duplicate concepts:

- DOUBLE
- Double
- Double Room
- DOUBLE ROOM

Twin variations:

- Twin
- Twin Room
- Twin Single Use

Dormitory variations:

- Bed in 6-Bed Mixed Dormitory
- Bed in 6 Bed Dormitory Room

Found common patterns:

- Different capitalization
- Hyphens
- Commas
- Parentheses
- Smoking information
- Bed configuration
- Occupancy information

### Engineering Lesson

Do not create normalization rules before understanding the data.

Analyze first.
Implement later.

---

## Day 7 - Project Direction Changed

### New Information

The lead developer explained the production workflow.

Current workflow:

Multiple Supplier APIs
        ↓
Collect complete hotel offers
        ↓
Send complete JSON to Vervotech
        ↓
Receive standardized room information

### Internship Scope

Current task is ONLY to work with room names.

Other fields will be ignored for now.

### Important Realization

The objective is NOT to build CRUD.

The objective is to research whether a local solution can standardize room names and potentially reduce dependence on Vervotech.

---

## Day 8 - Baseline Research

### Goal

Build a baseline before using AI.

Installed:

RapidFuzz

Compared similarity scorers.

Results:

King Deluxe Room
vs
Deluxe King Room

ratio() = 68.75

token_sort_ratio() = 100

token_set_ratio() = 100

### Learned

- ratio() is sensitive to word order.
- token_sort_ratio() handles reordered words.
- token_set_ratio() handles reordered words and extra descriptive words.

### Engineering Lesson

Never assume an algorithm is good.

Evaluate it using experiments.

---

## Current Status

Backend Foundation ✅

- FastAPI
- SQLite
- SQLAlchemy
- CRUD
- JSON Import
- Text Normalization
- Dataset Exploration
- RapidFuzz Baseline Started

## Day 9 - RapidFuzz Baseline

### Completed
- Compared every room against every other room using `token_set_ratio()`.
- Found the highest similarity match for each room.

### Observations
- Correctly matched rooms with different capitalization and word order.
- Produced false positives for some semantically different room names.
- Concluded that string similarity alone is insufficient for perfect room standardization.

### Next Step
Improve normalization and evaluate its impact before introducing embeddings.