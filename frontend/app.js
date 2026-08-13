const studentForm = document.querySelector("#student-form");
const rosterList = document.querySelector("#roster-list");
const statusMessage = document.querySelector("#status-message");

function showStatus(message, isSuccess = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("success", isSuccess);
}

async function getErrorMessage(response) {
  try {
    const data = await response.json();
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

function renderStudents(students) {
  rosterList.replaceChildren();

  if (students.length === 0) {
    const message = document.createElement("p");
    message.className = "empty-roster";
    message.textContent = "No students have been added yet.";
    rosterList.append(message);
    return;
  }

  students.forEach((student) => {
    const card = document.createElement("article");
    card.className = "student-card";

    const name = document.createElement("h3");
    name.textContent = student.name;

    const currentAge = document.createElement("p");
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
    rosterList.append(card);
  });
}

async function loadStudents() {
  try {
    const response = await fetch("/students/");
    if (!response.ok) {
      throw new Error(await getErrorMessage(response));
    }
    renderStudents(await response.json());
  } catch (error) {
    rosterList.replaceChildren();
    showStatus(`Could not load students: ${error.message}`);
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
    studentForm.reset();
    showStatus("Student added successfully.", true);
    await loadStudents();
  } catch (error) {
    showStatus(`Could not add student: ${error.message}`);
  }
}

async function updateAge(studentId, ageInput) {
  const newAge = Number(ageInput.value);
  if (!Number.isInteger(newAge) || newAge <= 0) {
    showStatus("Enter an age greater than zero.");
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
    showStatus("Student age updated successfully.", true);
    await loadStudents();
  } catch (error) {
    showStatus(`Could not update age: ${error.message}`);
  }
}

async function deleteStudent(studentId) {
  try {
    const response = await fetch(`/students/${studentId}`, { method: "DELETE" });
    if (!response.ok) {
      throw new Error(await getErrorMessage(response));
    }
    showStatus("Student deleted successfully.", true);
    await loadStudents();
  } catch (error) {
    showStatus(`Could not delete student: ${error.message}`);
  }
}

studentForm.addEventListener("submit", addStudent);

// One listener handles buttons in current and future roster cards.
rosterList.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button || !rosterList.contains(button)) {
    return;
  }

  const studentId = button.dataset.studentId;
  if (button.dataset.action === "save-age") {
    const ageInput = rosterList.querySelector(`[data-age-input="${studentId}"]`);
    await updateAge(studentId, ageInput);
  }
  if (button.dataset.action === "delete") {
    await deleteStudent(studentId);
  }
});

loadStudents();
