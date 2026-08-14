"""
Part 3 AI Assistant mock implementation for StudyTrack.

This module provides offline mock AI functions for study note summarization
and semantic search. All functions are deterministic, require no network calls,
and use no external AI or embedding APIs.
"""

import math
import re


# Fixed notes dataset (copied verbatim as required)
notes = [
    {
        "id": 1,
        "text": "Binary search requires a sorted array and repeatedly halves the search range using a midpoint comparison.",
    },
    {
        "id": 2,
        "text": "Insertion sort builds a sorted list one element at a time by shifting larger elements to the right.",
    },
    {
        "id": 3,
        "text": "FastAPI uses Pydantic models to validate request bodies and automatically generates Swagger documentation.",
    },
    {
        "id": 4,
        "text": "SQL joins combine rows from two tables using a matching column, such as inner join, left join, and full join.",
    },
    {
        "id": 5,
        "text": "Prompt engineering structures a task, context, constraints, and desired output format to guide an LLM's response.",
    },
]


def summarize_notes(raw_text: str) -> dict:
    """
    Deterministic offline mock summarizer for study notes.

    Returns exactly three keys: topic, key_points, difficulty.

    Topic rule:
    - For non-empty input, use the first non-empty line after stripping whitespace.
    - If input is empty or whitespace-only, return the literal string "untitled".

    Key points rule:
    - Split raw_text into sentences using '.', '!' and '?' as delimiters.
    - Take up to the first 3 non-empty sentences.
    - Strip surrounding whitespace from each sentence.
    - Return as a list of strings.
    - For empty/whitespace-only input, return [].

    Difficulty rule (word count thresholds):
    - < 40 words = "easy"
    - 40–100 words = "medium"
    - > 100 words = "hard"
    - Empty input (0 words) returns "easy".

    Args:
        raw_text: Study notes as a string.

    Returns:
        dict with keys: topic, key_points, difficulty.
    """
    # Extract topic from first non-empty line
    lines = raw_text.split("\n")
    topic = "untitled"
    for line in lines:
        stripped = line.strip()
        if stripped:
            topic = stripped
            break

    # Extract key points (up to 3 sentences)
    # Split on sentence delimiters: . ! ?
    key_points = []
    sentences = re.split(r"[.!?]", raw_text)
    for sentence in sentences:
        stripped = sentence.strip()
        if stripped and len(key_points) < 3:
            key_points.append(stripped)

    # Determine difficulty by word count
    word_count = len(raw_text.split())
    if word_count < 40:
        difficulty = "easy"
    elif word_count <= 100:
        difficulty = "medium"
    else:
        difficulty = "hard"

    return {
        "topic": topic,
        "key_points": key_points,
        "difficulty": difficulty,
    }


def mock_embed(text: str) -> list:
    """
    Generate a fixed 12-dimensional embedding vector for text.

    Uses an exact vocabulary of 12 terms and counts occurrences of exact
    whole-token matches (case-insensitive).

    Vocabulary (in order):
    0. sort
    1. search
    2. binary
    3. insertion
    4. sql
    5. join
    6. fastapi
    7. pydantic
    8. prompt
    9. llm
    10. database
    11. validate

    Tokenization:
    - Lowercase the input.
    - Split on any run of non-alphanumeric characters (spaces, punctuation, etc.).
    - "LLM's" tokenizes into ["llm", "s"].
    - Only exact whole-token matches count.
    - "sorted" does NOT count as "sort".

    Args:
        text: Input text to embed.

    Returns:
        list of exactly 12 floats representing word counts for each vocab term.
    """
    vocabulary = [
        "sort",
        "search",
        "binary",
        "insertion",
        "sql",
        "join",
        "fastapi",
        "pydantic",
        "prompt",
        "llm",
        "database",
        "validate",
    ]

    # Tokenize: lowercase, split on non-alphanumeric runs
    lowered = text.lower()
    tokens = re.split(r"[^a-z0-9]+", lowered)
    tokens = [token for token in tokens if token]  # Remove empty strings

    # Count exact matches for each vocabulary term
    embedding = []
    for term in vocabulary:
        count = tokens.count(term)
        embedding.append(float(count))

    return embedding


def cosine_similarity(vec_a: list, vec_b: list) -> float:
    """
    Calculate cosine similarity between two vectors from first principles.

    Formula:
    cosine_similarity = dot(vec_a, vec_b) / (magnitude(vec_a) * magnitude(vec_b))

    Uses math.sqrt for magnitude calculation.

    Zero-vector rule:
    - If either vector has magnitude exactly 0.0, return 0.0 immediately.
    - Never allows ZeroDivisionError.

    Args:
        vec_a: First vector (list of floats).
        vec_b: Second vector (list of floats).

    Returns:
        float: Cosine similarity in range [0, 1], or 0.0 if either vector is zero.
    """
    # Calculate dot product
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))

    # Calculate magnitudes
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))

    # Zero-vector rule: return 0.0 if either magnitude is 0
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    return dot_product / (mag_a * mag_b)
