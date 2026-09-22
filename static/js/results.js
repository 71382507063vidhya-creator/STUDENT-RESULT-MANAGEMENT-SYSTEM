/* ============================================================
   results.js
   Fetches ONE student's result from the backend and renders it.
   The backend's "status" field is the only thing that decides
   PASS vs FAIL - this file never re-computes that decision.
   ============================================================ */

async function loadResult(studentId) {
  const wrapper = document.getElementById("result-wrapper");
  if (!wrapper) return;

  const { ok, data } = await apiRequest(`/api/results/${studentId}`);

  if (!ok) {
    wrapper.innerHTML = `
      <div class="empty-state">
        <i class="bi bi-exclamation-triangle"></i>
        ${data.error || "Unable to load result"}
      </div>`;
    return;
  }

  if (data.status === "NO_RESULT") {
    wrapper.innerHTML = `
      <div class="empty-state">
        <i class="bi bi-hourglass-split"></i>
        No marks have been recorded for this student yet.
      </div>`;
    return;
  }

  renderResult(data);
}

function renderResult(result) {
  const wrapper = document.getElementById("result-wrapper");

  const subjectRows = result.subjects
    .map(
      (s) => `
      <tr>
        <td>${s.subject_code}</td>
        <td>${s.subject_name}</td>
        <td>${s.marks}</td>
      </tr>`
    )
    .join("");

  const celebrationHtml =
    result.status === "PASS"
      ? `
      <div class="celebration-box" id="celebration-box">
        <h2>🎉 CONGRATULATIONS! 🎉</h2>
        <p class="fs-5 fw-semibold mb-1">YOU PASSED!</p>
        <p class="mb-3">🍫 CHOCOLATE SHOWER 🍫</p>
        <button id="celebrate-again-btn" class="celebrate-again-btn no-print">
          🍫 Celebrate Again
        </button>
      </div>`
      : `
      <div class="fail-box">
        <h2>❌ RESULT: FAIL</h2>
        <p class="fs-5 fw-semibold mb-1">Keep Learning! 💪</p>
        <p class="mb-0">You can do better next time.</p>
      </div>`;

  wrapper.innerHTML = `
    <div class="result-card fade-in">
      <div class="result-header">
        <h3 class="mb-0">🎓 STUDENT RESULT MANAGEMENT</h3>
      </div>
      <div class="result-body">
        <div class="result-info-grid">
          <div><div class="label">Student Name</div><div class="value">${result.name}</div></div>
          <div><div class="label">Register Number</div><div class="value">${result.register_number}</div></div>
          <div><div class="label">Department</div><div class="value">${result.department}</div></div>
          <div><div class="label">Semester</div><div class="value">${result.semester}</div></div>
        </div>

        <table class="table table-bordered">
          <thead>
            <tr><th>Subject Code</th><th>Subject</th><th>Marks</th></tr>
          </thead>
          <tbody>${subjectRows}</tbody>
        </table>

        <div class="result-summary-grid">
          <div class="result-summary-item"><div class="num">${result.total}</div><div class="lbl">Total</div></div>
          <div class="result-summary-item"><div class="num">${result.average}</div><div class="lbl">Average</div></div>
          <div class="result-summary-item"><div class="num">${result.grade}</div><div class="lbl">Grade</div></div>
          <div class="result-summary-item"><div class="num">${result.status}</div><div class="lbl">Status</div></div>
        </div>

        ${celebrationHtml}

        <div class="d-flex gap-2 justify-content-center mt-4 no-print">
          <button class="btn btn-primary-custom" onclick="window.print()"><i class="bi bi-printer"></i> Print Result</button>
          <button class="btn btn-outline-secondary" onclick="window.print()"><i class="bi bi-download"></i> Download Result</button>
          <a class="btn btn-outline-dark" href="${window.RESULT_VIEWER === 'admin' ? '/admin/dashboard' : '/student/dashboard'}">
            <i class="bi bi-arrow-left"></i> Back to Dashboard
          </a>
        </div>
      </div>
    </div>`;

  // Backend is the single source of truth: only a PASS status may
  // trigger the chocolate shower, and only PASS wires up the replay button.
  if (result.status === "PASS") {
    showChocolateShower();
  }
  initCelebrateAgainButton(result.status);
}

document.addEventListener("DOMContentLoaded", () => {
  if (window.RESULT_STUDENT_ID) {
    loadResult(window.RESULT_STUDENT_ID);
  }
});
