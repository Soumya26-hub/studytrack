const studentForm = document.querySelector("#student-form");
const rosterList = document.querySelector("#roster-list");
const statusMessage = document.querySelector("#status-message");
const errorBanner = document.querySelector("#error-banner");

function showStatus(message, isSuccess = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("success", isSuccess);
}

function showError(message) {
  errorBanner.textContent = message;
  // Don't leave a stale success message next to a new error.
  showStatus("");
}

function clearError() {
  errorBanner.textContent = "";
}

async function getErrorMessage(response) {
  try {
    const data = await response.json();
    // FastAPI validation errors (422) return detail as a list of {msg, ...} objects.
    if (Array.isArray(data.detail)) {
      return data.detail.map((item) => item.msg).join("; ");
    }
    return data.detail || "The request could not be completed.";
  } catch {
    return "The request could not be completed.";
  }
}

function createButton(label, action, studentId, className = "") {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = label;
  button.dataset.action = action;
  button.dataset.studentId = studentId;
  button.className = className;
  return button;
}

function createStudentCard(student) {
  const card = document.createElement("article");
  card.className = "student-card";
  card.dataset.studentId = student.id;

  const name = document.createElement("h3");
  name.textContent = student.name;

  const currentAge = document.createElement("p");
  currentAge.className = "current-age";
  currentAge.textContent = `Current age: ${student.age}`;

  const email = document.createElement("p");
  email.className = "student-email";
  email.textContent = student.email;

  const ageEditor = document.createElement("div");
  ageEditor.className = "age-editor";
  const ageLabel = document.createElement("label");
  ageLabel.textContent = "Edit age";
  const ageInput = document.createElement("input");
  ageInput.type = "number";
  ageInput.min = "1";
  ageInput.value = student.age;
  ageInput.dataset.ageInput = student.id;
  ageLabel.append(ageInput);
  ageEditor.append(ageLabel, createButton("Save Age", "save-age", student.id));

  card.append(
    name,
    currentAge,
    email,
    ageEditor,
    createButton("Delete", "delete", student.id, "delete-button"),
  );
  return card;
}

function renderEmptyRoster() {
  const message = document.createElement("p");
  message.className = "empty-roster";
  message.textContent = "No students have been added yet.";
  rosterList.append(message);
}

function createSummaryItem(labelText, valueText) {
  const item = document.createElement("div");
  item.className = "summary-item";
  const label = document.createElement("label");
  label.textContent = labelText;
  item.append(label);
  if (valueText !== undefined) {
    const value = document.createElement("div");
    value.className = "value";
    value.textContent = valueText;
    item.append(value);
  }
  return item;
}

function renderStudents(students) {
  rosterList.replaceChildren();

  if (students.length === 0) {
    renderEmptyRoster();
    return;
  }

  students.forEach((student) => {
    rosterList.append(createStudentCard(student));
  });
}

async function loadStudents() {
  try {
    const response = await fetch("/students/");
    if (!response.ok) {
      throw new Error(await getErrorMessage(response));
    }
    clearError();
    renderStudents(await response.json());
  } catch (error) {
    rosterList.replaceChildren();
    showError(`Could not load students: ${error.message}`);
  }
}

async function addStudent(event) {
  event.preventDefault();
  const formData = new FormData(studentForm);
  const student = {
    name: formData.get("name").trim(),
    email: formData.get("email").trim(),
    age: Number(formData.get("age")),
  };

  try {
    const response = await fetch("/students/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(student),
    });
    if (!response.ok) {
      throw new Error(await getErrorMessage(response));
    }
    const newStudent = await response.json();
    studentForm.reset();
    clearError();
    showStatus("Student added successfully.", true);
    rosterList.querySelector(".empty-roster")?.remove();
    rosterList.append(createStudentCard(newStudent));
  } catch (error) {
    showError(`Could not add student: ${error.message}`);
  }
}

async function updateAge(studentId, ageInput) {
  const newAge = Number(ageInput.value);
  if (!Number.isInteger(newAge) || newAge <= 0) {
    showError("Enter a whole-number age greater than zero.");
    return;
  }

  try {
    const response = await fetch(`/students/${studentId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ age: newAge }),
    });
    if (!response.ok) {
      throw new Error(await getErrorMessage(response));
    }
    const updatedStudent = await response.json();
    clearError();
    showStatus("Student age updated successfully.", true);

    // Update the card directly
    const card = rosterList.querySelector(`[data-student-id="${studentId}"]`);
    if (card) {
      const currentAgeElement = card.querySelector(".current-age");
      if (currentAgeElement) {
        currentAgeElement.textContent = `Current age: ${updatedStudent.age}`;
      }
    }
  } catch (error) {
    showError(`Could not update age: ${error.message}`);
  }
}

async function deleteStudent(studentId) {
  try {
    const response = await fetch(`/students/${studentId}`, { method: "DELETE" });
    if (!response.ok) {
      throw new Error(await getErrorMessage(response));
    }
    clearError();
    showStatus("Student deleted successfully.", true);

    // Remove the card directly
    const card = rosterList.querySelector(`[data-student-id="${studentId}"]`);
    if (card) {
      card.remove();

      // Show empty message if no more students
      if (rosterList.children.length === 0) {
        renderEmptyRoster();
      }
    }
  } catch (error) {
    showError(`Could not delete student: ${error.message}`);
  }
}

studentForm.addEventListener("submit", addStudent);
studentForm.addEventListener("input", clearError);

// One listener handles buttons in current and future roster cards.
rosterList.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button || !rosterList.contains(button)) {
    return;
  }

  const studentId = button.dataset.studentId;
  // Disable while the request runs so double-clicks don't send duplicate requests.
  button.disabled = true;
  try {
    if (button.dataset.action === "save-age") {
      const ageInput = rosterList.querySelector(`[data-age-input="${studentId}"]`);
      await updateAge(studentId, ageInput);
    }
    if (button.dataset.action === "delete") {
      const studentName = button.closest(".student-card")?.querySelector("h3")?.textContent;
      if (window.confirm(`Delete ${studentName || "this student"}? Their courses will also be removed.`)) {
        await deleteStudent(studentId);
      }
    }
  } finally {
    button.disabled = false;
  }
});

// AI Helper functionality (Part 3)

async function summarizeNotes() {
  const notesTextarea = document.querySelector("#notes-textarea");
  const summaryResults = document.querySelector("#summary-results");
  const rawText = notesTextarea.value;

  try {
    const response = await fetch("/assistant/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: rawText }),
    });

    if (!response.ok) {
      throw new Error(await getErrorMessage(response));
    }

    const summary = await response.json();
    clearError();

    // Render summary results with textContent only: the topic is user-typed text.
    summaryResults.replaceChildren();

    summaryResults.appendChild(createSummaryItem("Topic", summary.topic));

    const keyPointsDiv = createSummaryItem("Key Points");
    if (summary.key_points && summary.key_points.length > 0) {
      const ul = document.createElement("ul");
      ul.className = "key-points-list";
      summary.key_points.forEach((point) => {
        const li = document.createElement("li");
        li.textContent = point;
        ul.appendChild(li);
      });
      keyPointsDiv.appendChild(ul);
    } else {
      const noPoints = document.createElement("div");
      noPoints.className = "value";
      noPoints.textContent = "(no key points extracted)";
      keyPointsDiv.appendChild(noPoints);
    }
    summaryResults.appendChild(keyPointsDiv);

    summaryResults.appendChild(createSummaryItem("Difficulty", summary.difficulty));
  } catch (error) {
    showError(`Could not summarize notes: ${error.message}`);
  }
}

async function searchNotes() {
  const searchQuery = document.querySelector("#search-query").value;
  const searchResults = document.querySelector("#search-results");

  try {
    const encodedQuery = encodeURIComponent(searchQuery);
    const response = await fetch(`/assistant/search?query=${encodedQuery}`);

    if (!response.ok) {
      throw new Error(await getErrorMessage(response));
    }

    const results = await response.json();
    clearError();

    // Render search results
    searchResults.replaceChildren();

    if (!results || results.length === 0) {
      const noResults = document.createElement("p");
      noResults.textContent = "No results found.";
      searchResults.appendChild(noResults);
      return;
    }

    results.forEach((note) => {
      const resultDiv = document.createElement("div");
      resultDiv.className = "search-result";

      const textDiv = document.createElement("div");
      textDiv.className = "search-result-text";
      textDiv.textContent = note.text;
      resultDiv.appendChild(textDiv);

      const scoreDiv = document.createElement("div");
      scoreDiv.className = "search-result-score";
      scoreDiv.textContent = `Similarity: ${(note.similarity * 100).toFixed(1)}%`;
      resultDiv.appendChild(scoreDiv);

      searchResults.appendChild(resultDiv);
    });
  } catch (error) {
    showError(`Could not search notes: ${error.message}`);
  }
}

// Attach AI Helper event listeners
const summarizeBtn = document.querySelector("#summarize-btn");
const searchBtn = document.querySelector("#search-btn");

if (summarizeBtn) {
  summarizeBtn.addEventListener("click", summarizeNotes);
}
if (searchBtn) {
  searchBtn.addEventListener("click", searchNotes);
}

loadStudents();
