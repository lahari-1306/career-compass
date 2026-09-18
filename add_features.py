import os

# 1. Update templates/index.html with Admin Console Modal & Footer link
with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Add Admin Verification Link in Footer if not present
if "Admin Verification Console" not in html:
    footer_target = "<li><a href=\"#\" onclick=\"navigateToSection('about'); return false;\">About CareerCompass</a></li>"
    replacement = footer_target + "\n          <li><a href=\"#\" onclick=\"openAdminModal(); return false;\"><i data-lucide=\"shield-check\" class=\"icon-xs text-primary\"></i> Admin Verification Console</a></li>"
    html = html.replace(footer_target, replacement)

# Add Admin Verification Modal before </body>
if "admin-modal" not in html:
    admin_modal_html = """
  <!-- Admin Data Verification Modal -->
  <div id="admin-modal" class="modal-overlay hidden" onclick="closeAdminModal(event)">
    <div class="modal-card" style="max-width: 780px;" onclick="event.stopPropagation()">
      <div class="modal-header">
        <div class="badge badge-warning"><i data-lucide="shield-check" class="icon-xs"></i> ADMIN CONSOLE</div>
        <button class="close-btn" onclick="closeAdminModal()">&times;</button>
      </div>
      <h3 class="modal-title">Official Data Verification Console</h3>
      <p class="modal-org">Review, verify, and update notification timestamps and status badges</p>
      <div class="modal-body">
        <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem;">
          In accordance with CareerCompass integrity principles, this console allows administrators to manually timestamp verified official notices, edit active windows, and immediately update the live ticker feed without scraping or hallucinating.
        </p>
        <div class="table-responsive" style="max-height: 380px; overflow-y: auto;">
          <table class="data-table" style="font-size: 0.8rem;">
            <thead>
              <tr>
                <th>Title / Event</th>
                <th>Category</th>
                <th>Status</th>
                <th>Last Verified</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody id="admin-notifs-tbody">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="closeAdminModal()">Close Console</button>
      </div>
    </div>
  </div>
"""
    html = html.replace("</body>", admin_modal_html + "\n</body>")

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("index.html updated with Admin Console.")

# 2. Append JS handlers for Admin Console & Bookmarking in static/js/app.js
with open("static/js/app.js", "r", encoding="utf-8") as f:
    js = f.read()

if "openAdminModal" not in js:
    admin_js = """
// ==========================================
// 10. ADMIN VERIFICATION CONSOLE
// ==========================================
function openAdminModal() {
  const modal = document.getElementById('admin-modal');
  const tbody = document.getElementById('admin-notifs-tbody');
  const notifs = AppState.datasets.allNotifications || [];

  tbody.innerHTML = notifs.map(n => `
    <tr>
      <td><strong>${escapeHtml(n.title)}</strong><br><small style="color: var(--text-muted);">${escapeHtml(n.organization)}</small></td>
      <td><span class="badge badge-primary">${escapeHtml(n.category)}</span></td>
      <td>
        <select id="status-select-${n.id}" style="padding: 0.2rem 0.4rem; font-size: 0.75rem; border-radius: 4px; border: 1px solid var(--border-color); background: var(--bg-surface); color: var(--text-main);">
          <option value="OPEN" ${n.status === 'OPEN' ? 'selected' : ''}>OPEN</option>
          <option value="LIVE" ${n.status === 'LIVE' ? 'selected' : ''}>LIVE</option>
          <option value="CLOSING_SOON" ${n.status === 'CLOSING_SOON' ? 'selected' : ''}>CLOSING_SOON</option>
          <option value="UPCOMING" ${n.status === 'UPCOMING' ? 'selected' : ''}>UPCOMING</option>
          <option value="RESULT" ${n.status === 'RESULT' ? 'selected' : ''}>RESULT</option>
          <option value="CLOSED" ${n.status === 'CLOSED' ? 'selected' : ''}>CLOSED</option>
        </select>
      </td>
      <td><small>${new Date(n.last_verified_at).toLocaleDateString()}</small></td>
      <td>
        <button class="btn btn-primary" style="padding: 0.25rem 0.55rem; font-size: 0.72rem;" onclick="adminVerifyNotification('${n.id}')">
          <i data-lucide="check" class="icon-xs"></i> Verify Now
        </button>
      </td>
    </tr>
  `).join('');

  modal.classList.remove('hidden');
  refreshIcons();
}

function closeAdminModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains('close-btn')) return;
  document.getElementById('admin-modal').classList.add('hidden');
}

async function adminVerifyNotification(id) {
  const selectElem = document.getElementById(`status-select-${id}`);
  const newStatus = selectElem ? selectElem.value : null;

  try {
    const res = await fetch('/api/admin/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: id, status: newStatus })
    });
    const result = await res.json();
    if (result.success) {
      alert(`Notification verified and timestamp updated successfully! Ticker refreshed.`);
      // Reload notifications & ticker
      const notifsRes = await fetch('/api/notifications/all').then(r => r.json());
      AppState.datasets.allNotifications = notifsRes.notifications || [];
      renderNotificationsCenter();
      initTicker();
      openAdminModal(); // Refresh modal view
    } else {
      alert('Error updating notification: ' + result.message);
    }
  } catch (err) {
    alert('Verification request failed.');
  }
}
"""
    with open("static/js/app.js", "a", encoding="utf-8") as f:
        f.write(admin_js)
    print("static/js/app.js updated with Admin JS.")

# 3. Add print media styles to static/css/styles.css
with open("static/css/styles.css", "r", encoding="utf-8") as f:
    css = f.read()

if "@media print" not in css:
    print_css = """
/* Print Styling for Roadmaps */
@media print {
  body {
    background: #ffffff !important;
    color: #000000 !important;
  }
  .ticker-container, .site-header, .site-footer, .breadcrumb-container, .hero-wrapper, .filter-bar, .roadmap-actions, .btn, .theme-btn {
    display: none !important;
  }
  .page-section {
    display: block !important;
  }
  .roadmap-result-container {
    border: 2px solid #000000 !important;
    box-shadow: none !important;
    padding: 1.5rem !important;
  }
  .roadmap-step {
    border: 1px solid #cccccc !important;
    background: #ffffff !important;
  }
}
"""
    with open("static/css/styles.css", "a", encoding="utf-8") as f:
        f.write(print_css)
    print("static/css/styles.css updated with Print styles.")
