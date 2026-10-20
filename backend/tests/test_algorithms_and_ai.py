from backend.ai_service import cosine_similarity, mock_embed, summarize_notes
from backend.algorithms import (
    binary_search_by_name,
    count_students_meeting_min_age,
    insertion_sort_by_field,
)


def test_insertion_sort_handles_empty_and_ties():
    assert insertion_sort_by_field([], "age") == []
    students = [{"age": 3}, {"age": 1}, {"age": 3}, {"age": 2}]
    assert [s["age"] for s in insertion_sort_by_field(students, "age")] == [1, 2, 3, 3]


def test_binary_search_empty_and_missing():
    assert binary_search_by_name([], "A") == -1
    people = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
    assert binary_search_by_name(people, "C") == {"name": "C"}
    assert binary_search_by_name(people, "D") == -1


def test_count_students_meeting_min_age():
    assert count_students_meeting_min_age([{"age": 20}, {"age": 21}], 21) == 1


def test_summarize_empty_input():
    assert summarize_notes("   ") == {"topic": "untitled", "key_points": [], "difficulty": "easy"}


def test_summarize_takes_first_three_sentences():
    result = summarize_notes("Topic line\nOne. Two! Three? Four.")
    assert result["topic"] == "Topic line"
    assert result["key_points"] == ["Topic line\nOne", "Two", "Three"]


def test_mock_embed_whole_tokens_only():
    vector = mock_embed("Sorted sort LLM's")
    assert vector[0] == 1.0  # "sort" counted once; "sorted" ignored
    assert vector[9] == 1.0  # "llm" from "LLM's"


def test_cosine_similarity_zero_vector():
    assert cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0


def test_search_endpoint_ranks_matching_note_first(client):
    results = client.get("/assistant/search?query=binary search").json()
    assert results[0]["id"] == 1
    assert len(results) == 5


def test_summarize_endpoint(client):
    response = client.post("/assistant/summarize", json={"text": "<b>x</b>"})
    assert response.json()["topic"] == "<b>x</b>"
