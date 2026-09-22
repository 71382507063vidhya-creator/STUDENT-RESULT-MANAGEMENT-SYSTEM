/* ============================================================
   main.js - shared helpers + landing page / login page logic
   ============================================================ */

/** Show a Bootstrap alert inside a given container element. */
function showAlert(containerId, message, type = "danger") {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>`;
}

/** Small wrapper around fetch() that always sends/receives JSON + cookies. */
async function apiRequest(url, method = "GET", body = null) {
  const options = {
    method,
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
  };
  if (body) options.body = JSON.stringify(body);

  const response = await fetch(url, options);
  let data = {};
  try {
    data = await response.json();
  } catch (err) {
    data = {};
  }
  return { ok: response.ok, status: response.status, data };
}

document.addEventListener("DOMContentLoaded", () => {
  const adminForm = document.getElementById("admin-login-form");
  if (adminForm) {
    adminForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("admin-username").value.trim();
      const password = document.getElementById("admin-password").value;

      const { ok, data } = await apiRequest("/api/admin/login", "POST", { username, password });
      if (ok) {
        window.location.href = "/admin/dashboard";
      } else {
        showAlert("admin-login-alert", data.error || "Login failed", "danger");
      }
    });
  }

  const studentForm = document.getElementById("student-login-form");
  if (studentForm) {
    studentForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const register_number = document.getElementById("student-register-number").value.trim();
      const password = document.getElementById("student-password").value;

      const { ok, data } = await apiRequest("/api/student/login", "POST", { register_number, password });
      if (ok) {
        window.location.href = "/student/dashboard";
      } else {
        showAlert("student-login-alert", data.error || "Login failed", "danger");
      }
    });
  }

  // Wire up any logout buttons found on the page.
  document.querySelectorAll(".logout-btn").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      await apiRequest("/api/logout", "POST");
      window.location.href = "/";
    });
  });

  // Mobile sidebar toggle (used on dashboard-style pages).
  const toggleBtn = document.querySelector(".sidebar-toggle-btn");
  const sidebar = document.querySelector(".sidebar");
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => sidebar.classList.toggle("show"));
  }
});
