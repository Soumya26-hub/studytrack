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
pip install -r backend/requirements.txt
```

Start the application:

```bash
uvicorn backend.main:app --reload
```

Open the application:


http://localhost:8000


API documentation:

http://localhost:8000/docs


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


GET /students/search
GET /students/sorted
GET /students/report


The algorithm implementations are in:


backend/algorithms.py

## Complexity

- **Insertion sort:** O(n²) time in the worst case and O(1) extra space.
- **Binary search:** O(log n) time because the search range is halved each time.
- **Roster report:** O(n) time because every student is processed once.
- **Minimum-age count:** O(n) time because every student is checked once.

## Part 3 – AI Helper

The dashboard includes an AI Helper with two features:

- Study note summarization
- Study note search

### Summarize Notes


POST /assistant/summarize


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


GET /assistant/search?query=<text>


The search uses a fixed set of study notes, mock word-count embeddings,
and cosine similarity to rank the results.

An empty query or a query with no matching vocabulary returns all five
notes with a similarity score of `0.0`.

### AI Mode

Part 3 uses an offline mock implementation.

No API key, internet connection, or external AI service is required.

## Real LLM Prompt

The project uses offline mock mode for grading. If a real LLM mode were implemented, this is the prompt that would be used:

```text
You are a study note summarizer.

Task:
Summarize the study notes provided below and return a JSON object with exactly these three keys:
- topic
- key_points
- difficulty

Rules:
1. topic: Use the first non-empty line of the notes after stripping whitespace. If the input is empty or contains only whitespace, use "untitled".
2. key_points: Split the notes into sentences using ., !, or ? as delimiters. Return up to the first 3 non-empty sentences after stripping whitespace. For empty input, return [].
3. difficulty: Count the total number of words in the input:
   - fewer than 40 words: "easy"
   - 40 to 100 words: "medium"
   - more than 100 words: "hard"
   - an empty input has 0 words and is therefore "easy".

Constraints:
- Return exactly the three keys: topic, key_points, difficulty.
- Do not add any other keys.
- Return only valid JSON.
- Do not include explanations, markdown, or any text outside the JSON object.
- Use the rules above deterministically.

Input notes:
<raw study notes>
```


## Project Structure


studytrack/
├── backend/
│   ├── algorithms.py
│   ├── ai_service.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   ├── schemas.py
│   └── seed_data.py
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── .env.example
├── .gitignore
└── README.md


## Security

No API keys or production secrets are committed to the repository.

The application can run locally without any external AI service.