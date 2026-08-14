# StudyTrack

StudyTrack is a student roster management application built with FastAPI,
SQLite, and a simple HTML/CSS/JavaScript frontend.

## Features

- Add, view, update, and delete students
- Search and sort students
- Generate student reports
- Basic algorithm implementations
- AI Helper for study notes
- Semantic search for study notes

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- HTML, CSS, JavaScript

## Setup

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
uvicorn backend.main:app --reload
```

Open the application:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

## Part 1 – Student Roster

The dashboard allows users to:

- Add students
- View the roster
- Update student age
- Delete students
- Handle duplicate emails and other errors

### Main Endpoints

```text
POST   /students/
GET    /students/
PUT    /students/{student_id}
DELETE /students/{student_id}
```

## Part 2 – Algorithms

Part 2 adds student search, sorting, and reporting functionality.

### Main Endpoints

```text
GET /students/search
GET /students/sorted
GET /students/report
```

The algorithm implementations are in:

```text
backend/algorithms.py
```

## Part 3 – AI Helper

The dashboard includes an AI Helper with two features:

- Study note summarization
- Study note search

### Summarize Notes

```text
POST /assistant/summarize
```

The endpoint accepts study notes and returns:

```json
{
  "topic": "...",
  "key_points": [],
  "difficulty": "easy"
}
```

The mock summarizer:

- Uses the first non-empty line as the topic
- Extracts up to three sentences as key points
- Uses word count to determine difficulty
- Returns `untitled`, `[]`, and `easy` for empty input

### Search Notes

```text
GET /assistant/search?query=<text>
```

The search uses a fixed set of study notes, mock word-count embeddings,
and cosine similarity to rank the results.

An empty query or a query with no matching vocabulary returns all five
notes with a similarity score of `0.0`.

### AI Mode

Part 3 uses an offline mock implementation.

No API key, internet connection, or external AI service is required.

## Project Structure

```text
studytrack/
├── backend/
│   ├── algorithms.py
│   ├── ai_service.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── seed_data.py
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Security

No API keys or production secrets are committed to the repository.

The application can run locally without any external AI service.