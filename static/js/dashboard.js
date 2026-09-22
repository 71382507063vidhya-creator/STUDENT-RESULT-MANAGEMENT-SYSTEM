/* ============================================================
   dashboard.js
   Admin dashboard stats + Student / Subject / Marks / Results
   management pages. Each function only runs if its page elements
   exist, so this single file can be shared across templates.
   ============================================================ */

let chartInstance = null;

/* ---------------- Admin Dashboard (stat cards + chart) ---------------- */

async function loadDashboardStats() {
  const el = document.getElementById("dashboard-stats");
  if (!el) return;

  const { ok, data } = await apiRequest("/api/dashboard-stats");
  if (!ok) {
    showAlert("dashboard-alert", data.error || "Failed to load dashboard stats");
    return;
  }

  document.getElementById("stat-total-students").textContent = data.total_students;
  document.getElementById("stat-total-subjects").textContent = data.total_subjects;
  document.getElementById("stat-total-results").textContent = data.total_results;
  document.getElementById("stat-passed").textContent = data.passed_students;
  document.getElementById("stat-failed").textContent = data.failed_students;
  document.getElementById("stat-pass-percentage").textContent = data.pass_percentage + "%";

  renderResultChart(data.passed_students, data.failed_students);
  renderRecentResults(data.recent_results);
}

function renderResultChart(passed, failed) {
  const canvas = document.getElementById("resultChart");
  if (!canvas || typeof Chart === "undefined") return;

  if (chartInstance) chartInstance.destroy();

  chartInstance = new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: ["Passed", "Failed"],
      datasets: [{ data: [passed, failed], backgroundColor: ["#2ec4b6", "#e63946"] }],
    },
    options: { responsive: true, plugins: { legend: { position: "bottom" } } },
  });
}

function renderRecentResults(results) {
  const tbody = document.getElementById("recent-results-body");
  if (!tbody) return;

  if (!results || results.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No results yet</td></tr>`;
    return;
  }

  tbody.innerHTML = results
    .map(
      (r) => `
      <tr>
        <td>${r.name}</td>
        <td>${r.register_number}</td>
        <td>${r.total}</td>
        <td>${r.grade}</td>
        <td><span class="badge ${r.status === "PASS" ? "badge-pass" : "badge-fail"}">${r.status}</span></td>
      </tr>`
    )
    .join("");
}

/* ---------------- Students page ---------------- */

async function loadStudents() {
  const tbody = document.getElementById("students-body");
  if (!tbody) return;

  const search = document.getElementById("student-search")?.value || "";
  const department = document.getElementById("student-filter-department")?.value || "";
  const year = document.getElementById("student-filter-year")?.value || "";
  const semester = document.getElementById("student-filter-semester")?.value || "";

  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (department) params.set("department", department);
  if (year) params.set("year", year);
  if (semester) params.set("semester", semester);

  const { ok, data } = await apiRequest(`/api/students?${params.toString()}`);
  if (!ok) {
    showAlert("students-alert", data.error || "Failed to load students");
    return;
  }

  if (data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8"><div class="empty-state"><i class="bi bi-people"></i>No students found</div></td></tr>`;
    return;
  }

  tbody.innerHTML = data
    .map(
      (s) => `
      <tr>
        <td>${s.id}</td>
        <td>${s.name}</td>
        <td>${s.register_number}</td>
        <td>${s.email}</td>
        <td>${s.department}</td>
        <td>${s.year}</td>
        <td>${s.semester}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1" onclick="editStudent(${s.id})"><i class="bi bi-pencil"></i></button>
          <button class="btn btn-sm btn-outline-danger" onclick="confirmDeleteStudent(${s.id}, '${s.name.replace(/'/g, "\\'")}')"><i class="bi bi-trash"></i></button>
          <a class="btn btn-sm btn-outline-success" href="/admin/result/${s.id}"><i class="bi bi-file-earmark-text"></i></a>
        </td>
      </tr>`
    )
    .join("");
}

function openAddStudentModal() {
  document.getElementById("student-form").reset();
  document.getElementById("student-form-id").value = "";
  document.getElementById("student-modal-title").textContent = "Add Student";
  document.getElementById("student-password").required = true;
  new bootstrap.Modal(document.getElementById("studentModal")).show();
}

async function editStudent(id) {
  const { ok, data } = await apiRequest(`/api/students/${id}`);
  if (!ok) {
    showAlert("students-alert", data.error || "Student not found");
    return;
  }
  document.getElementById("student-form-id").value = data.id;
  document.getElementById("student-name").value = data.name;
  document.getElementById("student-register-number").value = data.register_number;
  document.getElementById("student-email").value = data.email;
  document.getElementById("student-department").value = data.department;
  document.getElementById("student-year").value = data.year;
  document.getElementById("student-semester").value = data.semester;
  document.getElementById("student-password").value = "";
  document.getElementById("student-password").required = false;
  document.getElementById("student-modal-title").textContent = "Edit Student";
  new bootstrap.Modal(document.getElementById("studentModal")).show();
}

async function submitStudentForm(e) {
  e.preventDefault();
  const id = document.getElementById("student-form-id").value;
  const payload = {
    name: document.getElementById("student-name").value.trim(),
    register_number: document.getElementById("student-register-number").value.trim(),
    email: document.getElementById("student-email").value.trim(),
    department: document.getElementById("student-department").value.trim(),
    year: document.getElementById("student-year").value,
    semester: document.getElementById("student-semester").value,
    password: document.getElementById("student-password").value,
  };

  const url = id ? `/api/students/${id}` : "/api/students";
  const method = id ? "PUT" : "POST";
  const { ok, data } = await apiRequest(url, method, payload);

  if (!ok) {
    showAlert("student-modal-alert", data.error || "Failed to save student");
    return;
  }

  bootstrap.Modal.getInstance(document.getElementById("studentModal")).hide();
  showAlert("students-alert", "Student saved successfully", "success");
  loadStudents();
}

let studentToDelete = null;
function confirmDeleteStudent(id, name) {
  studentToDelete = id;
  document.getElementById("delete-target-name").textContent = name;
  new bootstrap.Modal(document.getElementById("deleteStudentModal")).show();
}

async function deleteStudentConfirmed() {
  if (!studentToDelete) return;
  const { ok, data } = await apiRequest(`/api/students/${studentToDelete}`, "DELETE");
  bootstrap.Modal.getInstance(document.getElementById("deleteStudentModal")).hide();
  if (!ok) {
    showAlert("students-alert", data.error || "Failed to delete student");
    return;
  }
  showAlert("students-alert", "Student deleted successfully", "success");
  loadStudents();
}

/* ---------------- Subjects page ---------------- */

async function loadSubjects() {
  const tbody = document.getElementById("subjects-body");
  if (!tbody) return;

  const search = document.getElementById("subject-search")?.value || "";
  const department = document.getElementById("subject-filter-department")?.value || "";
  const semester = document.getElementById("subject-filter-semester")?.value || "";

  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (department) params.set("department", department);
  if (semester) params.set("semester", semester);

  const { ok, data } = await apiRequest(`/api/subjects?${params.toString()}`);
  if (!ok) {
    showAlert("subjects-alert", data.error || "Failed to load subjects");
    return;
  }

  if (data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><i class="bi bi-journal-bookmark"></i>No subjects found</div></td></tr>`;
    return;
  }

  tbody.innerHTML = data
    .map(
      (s) => `
      <tr>
        <td>${s.id}</td>
        <td>${s.subject_code}</td>
        <td>${s.subject_name}</td>
        <td>${s.department}</td>
        <td>${s.semester}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1" onclick="editSubject(${s.id})"><i class="bi bi-pencil"></i></button>
          <button class="btn btn-sm btn-outline-danger" onclick="confirmDeleteSubject(${s.id}, '${s.subject_name.replace(/'/g, "\\'")}')"><i class="bi bi-trash"></i></button>
        </td>
      </tr>`
    )
    .join("");
}

function openAddSubjectModal() {
  document.getElementById("subject-form").reset();
  document.getElementById("subject-form-id").value = "";
  document.getElementById("subject-modal-title").textContent = "Add Subject";
  new bootstrap.Modal(document.getElementById("subjectModal")).show();
}

async function editSubject(id) {
  const { ok, data } = await apiRequest(`/api/subjects/${id}`);
  if (!ok) {
    showAlert("subjects-alert", data.error || "Subject not found");
    return;
  }
  document.getElementById("subject-form-id").value = data.id;
  document.getElementById("subject-code").value = data.subject_code;
  document.getElementById("subject-name").value = data.subject_name;
  document.getElementById("subject-department").value = data.department;
  document.getElementById("subject-semester").value = data.semester;
  document.getElementById("subject-modal-title").textContent = "Edit Subject";
  new bootstrap.Modal(document.getElementById("subjectModal")).show();
}

async function submitSubjectForm(e) {
  e.preventDefault();
  const id = document.getElementById("subject-form-id").value;
  const payload = {
    subject_code: document.getElementById("subject-code").value.trim(),
    subject_name: document.getElementById("subject-name").value.trim(),
    department: document.getElementById("subject-department").value.trim(),
    semester: document.getElementById("subject-semester").value,
  };

  const url = id ? `/api/subjects/${id}` : "/api/subjects";
  const method = id ? "PUT" : "POST";
  const { ok, data } = await apiRequest(url, method, payload);

  if (!ok) {
    showAlert("subject-modal-alert", data.error || "Failed to save subject");
    return;
  }

  bootstrap.Modal.getInstance(document.getElementById("subjectModal")).hide();
  showAlert("subjects-alert", "Subject saved successfully", "success");
  loadSubjects();
}

let subjectToDelete = null;
function confirmDeleteSubject(id, name) {
  subjectToDelete = id;
  document.getElementById("delete-subject-target-name").textContent = name;
  new bootstrap.Modal(document.getElementById("deleteSubjectModal")).show();
}

async function deleteSubjectConfirmed() {
  if (!subjectToDelete) return;
  const { ok, data } = await apiRequest(`/api/subjects/${subjectToDelete}`, "DELETE");
  bootstrap.Modal.getInstance(document.getElementById("deleteSubjectModal")).hide();
  if (!ok) {
    showAlert("subjects-alert", data.error || "Failed to delete subject");
    return;
  }
  showAlert("subjects-alert", "Subject deleted successfully", "success");
  loadSubjects();
}

/* ---------------- Marks page ---------------- */

async function populateMarksDropdowns() {
  const studentSelect = document.getElementById("marks-student");
  const subjectSelect = document.getElementById("marks-subject");
  if (!studentSelect || !subjectSelect) return;

  const [studentsRes, subjectsRes] = await Promise.all([
    apiRequest("/api/students"),
    apiRequest("/api/subjects"),
  ]);

  if (studentsRes.ok) {
    studentSelect.innerHTML =
      `<option value="">Select Student</option>` +
      studentsRes.data.map((s) => `<option value="${s.id}">${s.name} (${s.register_number})</option>`).join("");
  }
  if (subjectsRes.ok) {
    subjectSelect.innerHTML =
      `<option value="">Select Subject</option>` +
      subjectsRes.data.map((s) => `<option value="${s.id}">${s.subject_code} - ${s.subject_name}</option>`).join("");
  }
}

async function loadMarks() {
  const tbody = document.getElementById("marks-body");
  if (!tbody) return;

  const { ok, data } = await apiRequest("/api/marks");
  if (!ok) {
    showAlert("marks-alert", data.error || "Failed to load marks");
    return;
  }

  if (data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><i class="bi bi-pencil-square"></i>No marks recorded yet</div></td></tr>`;
    return;
  }

  tbody.innerHTML = data
    .map(
      (m) => `
      <tr>
        <td>${m.student_name} (${m.register_number})</td>
        <td>${m.subject_code} - ${m.subject_name}</td>
        <td>${m.marks}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1" onclick="editMarks(${m.id}, ${m.marks})"><i class="bi bi-pencil"></i></button>
          <button class="btn btn-sm btn-outline-danger" onclick="deleteMarksEntry(${m.id})"><i class="bi bi-trash"></i></button>
        </td>
      </tr>`
    )
    .join("");
}

async function submitMarksForm(e) {
  e.preventDefault();
  const payload = {
    student_id: document.getElementById("marks-student").value,
    subject_id: document.getElementById("marks-subject").value,
    marks: document.getElementById("marks-value").value,
  };

  const { ok, data } = await apiRequest("/api/marks", "POST", payload);
  if (!ok) {
    showAlert("marks-alert", data.error || "Failed to add marks");
    return;
  }

  showAlert("marks-alert", "Marks added successfully", "success");
  document.getElementById("marks-form").reset();
  loadMarks();
}

function editMarks(id, currentMarks) {
  const newValue = prompt("Enter new marks (0-100):", currentMarks);
  if (newValue === null) return;
  updateMarksEntry(id, newValue);
}

async function updateMarksEntry(id, marks) {
  const { ok, data } = await apiRequest(`/api/marks/${id}`, "PUT", { marks });
  if (!ok) {
    showAlert("marks-alert", data.error || "Failed to update marks");
    return;
  }
  showAlert("marks-alert", "Marks updated successfully", "success");
  loadMarks();
}

async function deleteMarksEntry(id) {
  if (!confirm("Delete this marks entry?")) return;
  const { ok, data } = await apiRequest(`/api/marks/${id}`, "DELETE");
  if (!ok) {
    showAlert("marks-alert", data.error || "Failed to delete marks");
    return;
  }
  showAlert("marks-alert", "Marks deleted successfully", "success");
  loadMarks();
}

/* ---------------- Results listing page (admin) ---------------- */

async function loadAllResults() {
  const tbody = document.getElementById("all-results-body");
  if (!tbody) return;

  const { ok, data } = await apiRequest("/api/results");
  if (!ok) {
    showAlert("results-alert", data.error || "Failed to load results");
    return;
  }

  const rows = data.filter((r) => r.status !== "NO_RESULT");
  if (rows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><i class="bi bi-bar-chart"></i>No results available yet</div></td></tr>`;
    return;
  }

  tbody.innerHTML = rows
    .map(
      (r) => `
      <tr>
        <td>${r.name}</td>
        <td>${r.register_number}</td>
        <td>${r.department}</td>
        <td>${r.total}</td>
        <td>${r.average}</td>
        <td>${r.grade}</td>
        <td><span class="badge ${r.status === "PASS" ? "badge-pass" : "badge-fail"}">${r.status}</span></td>
        <td><a class="btn btn-sm btn-outline-primary" href="/admin/result/${r.student_id}">View</a></td>
      </tr>`
    )
    .join("");
}

document.addEventListener("DOMContentLoaded", () => {
  loadDashboardStats();
  loadStudents();
  loadSubjects();
  populateMarksDropdowns();
  loadMarks();
  loadAllResults();

  document.getElementById("student-form")?.addEventListener("submit", submitStudentForm);
  document.getElementById("subject-form")?.addEventListener("submit", submitSubjectForm);
  document.getElementById("marks-form")?.addEventListener("submit", submitMarksForm);
  document.getElementById("student-search")?.addEventListener("input", loadStudents);
  document.getElementById("student-filter-department")?.addEventListener("change", loadStudents);
  document.getElementById("student-filter-year")?.addEventListener("change", loadStudents);
  document.getElementById("student-filter-semester")?.addEventListener("change", loadStudents);
  document.getElementById("subject-search")?.addEventListener("input", loadSubjects);
  document.getElementById("subject-filter-department")?.addEventListener("change", loadSubjects);
  document.getElementById("subject-filter-semester")?.addEventListener("change", loadSubjects);
  document.getElementById("confirm-delete-student-btn")?.addEventListener("click", deleteStudentConfirmed);
  document.getElementById("confirm-delete-subject-btn")?.addEventListener("click", deleteSubjectConfirmed);
});
