/* ── Chart Initialization ────────────────────────────────── */
async function initCharts() {
  initVelocityChart();
  initDonutChart();
}

async function initVelocityChart() {
  const canvas = document.getElementById('taskChart');
  if (!canvas) return;

  try {
    const resp = await fetch('/api/chart-data');
    if (!resp.ok) return;
    const { labels, data } = await resp.json();

    const ctx = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 220);
    gradient.addColorStop(0, 'rgba(255,107,26,0.35)');
    gradient.addColorStop(0.6, 'rgba(255,107,26,0.06)');
    gradient.addColorStop(1, 'rgba(255,107,26,0)');

    new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Tasks Completed',
          data,
          borderColor: '#FF6B1A',
          borderWidth: 2.5,
          pointBackgroundColor: '#FF6B1A',
          pointBorderColor: '#0a0a0a',
          pointBorderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 6,
          fill: true,
          backgroundColor: gradient,
          tension: 0.5,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#1a1a1a',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            titleColor: '#f1f5f9',
            bodyColor: '#94a3b8',
            padding: 10,
            callbacks: {
              label: ctx => ` ${ctx.parsed.y} task${ctx.parsed.y !== 1 ? 's' : ''} completed`
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255,255,255,0.04)' },
            ticks: { color: '#64748b', font: { size: 11 } },
            border: { color: 'transparent' },
          },
          y: {
            grid: { color: 'rgba(255,255,255,0.04)' },
            ticks: { color: '#64748b', font: { size: 11 }, stepSize: 1 },
            border: { color: 'transparent' },
            beginAtZero: true,
          }
        }
      }
    });
  } catch (e) { console.error("Velocity chart failed", e); }
}

function initDonutChart() {
  const donutCanvas = document.getElementById('teamDonut');
  if (!donutCanvas) return;

  try {
    new Chart(donutCanvas.getContext('2d'), {
      type: 'doughnut',
      data: {
        labels: ['Engineering', 'Design', 'Product', 'Ops'],
        datasets: [{
          data: [45, 25, 20, 10],
          backgroundColor: ['#FF6B1A', '#7c3aed', '#3b82f6', '#10b981'],
          borderWidth: 0,
          hoverOffset: 10
        }]
      },
      options: {
        cutout: '80%',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        }
      }
    });
  } catch (e) { console.error("Donut chart failed", e); }
}

/* ── Modal Helpers ───────────────────────────────────────── */
function openModal(id) {
  const overlay = document.getElementById(id);
  if (overlay) {
    overlay.classList.add('open');
    // Focus first input
    setTimeout(() => {
      const first = overlay.querySelector('input, select, textarea');
      if (first) first.focus();
    }, 100);
  }
}

function closeModal(id) {
  const overlay = document.getElementById(id);
  if (overlay) overlay.classList.remove('open');
}

// Close on backdrop click
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay') || e.target.classList.contains('command-palette-overlay')) {
    e.target.classList.remove('open');
  }
});

function openCommandPalette() {
  const overlay = document.getElementById('commandPaletteOverlay');
  const input = document.getElementById('commandPaletteInput');
  if (!overlay) return;
  overlay.classList.add('open');
  setTimeout(() => input?.focus(), 100);
}

function closeCommandPalette() {
  const overlay = document.getElementById('commandPaletteOverlay');
  if (overlay) overlay.classList.remove('open');
}

function bindCommandPaletteActions() {
  document.querySelectorAll('.cp-actions button[data-action]').forEach(button => {
    button.addEventListener('click', () => {
      const action = button.dataset.action;
      if (!action) return;
      const routes = {
        dashboard: '/dashboard',
        projects: '/projects',
        tasks: '/tasks'
      };
      const target = routes[action] || '/';
      window.location.href = target;
    });
  });
}

// Close on Escape
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open, .command-palette-overlay.open').forEach(m => m.classList.remove('open'));
  }
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    openCommandPalette();
  }
});

/* ── Inline Status Update (AJAX) ────────────────────────── */
function setupStatusDropdowns() {
  document.querySelectorAll('.js-status-select').forEach(select => {
    select.addEventListener('change', async function () {
      const taskId = this.dataset.taskId;
      const newStatus = this.value;
      const row = this.closest('tr');

      try {
        const resp = await fetch(`/tasks/${taskId}/status`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus }),
        });

        if (!resp.ok) {
          showToast('Update failed — permission denied.', 'error');
          return;
        }

        const data = await resp.json();

        // Update badge in same row
        const badge = row.querySelector('.js-status-badge');
        if (badge) {
          badge.className = 'badge js-status-badge ' + statusBadgeClass(newStatus);
          badge.innerHTML = statusDot(newStatus) + newStatus;
        }

        // Overdue border
        if (row) {
          row.classList.toggle('overdue-row', data.is_overdue);
        }

        // Restyle dropdown
        styleStatusSelect(this, newStatus);

        showToast(`Status updated to "${newStatus}"`, 'success');
      } catch {
        showToast('Network error. Please try again.', 'error');
      }
    });

    // Apply initial style
    styleStatusSelect(select, select.value);
  });
}

function statusBadgeClass(s) {
  return { 'Todo': 'badge-todo', 'In Progress': 'badge-progress', 'Done': 'badge-done' }[s] || 'badge-todo';
}

function statusDot(s) {
  const colors = { 'Todo': '#64748b', 'In Progress': '#f59e0b', 'Done': '#10b981' };
  return `<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:${colors[s] || '#64748b'};"></span>`;
}

function styleStatusSelect(el, status) {
  el.style.background = { 'Todo': 'rgba(100,116,139,0.15)', 'In Progress': 'rgba(245,158,11,0.15)', 'Done': 'rgba(16,185,129,0.15)' }[status] || 'rgba(100,116,139,0.15)';
  el.style.color = { 'Todo': '#94a3b8', 'In Progress': '#f59e0b', 'Done': '#10b981' }[status] || '#94a3b8';
  el.style.borderColor = { 'Todo': 'rgba(100,116,139,0.3)', 'In Progress': 'rgba(245,158,11,0.3)', 'Done': 'rgba(16,185,129,0.3)' }[status] || 'rgba(100,116,139,0.3)';
}

/* ── Toast Notifications ─────────────────────────────────── */
let toastContainer;

function showToast(msg, type = 'info') {
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:999;display:flex;flex-direction:column;gap:8px;';
    document.body.appendChild(toastContainer);
  }

  const colors = {
    success: { bg: 'rgba(16,185,129,0.12)', border: 'rgba(16,185,129,0.25)', color: '#10b981' },
    error: { bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.25)', color: '#ef4444' },
    info: { bg: 'rgba(100,116,139,0.15)', border: 'rgba(255,255,255,0.08)', color: '#94a3b8' },
  };
  const c = colors[type] || colors.info;

  const toast = document.createElement('div');
  toast.style.cssText = `background:${c.bg};border:1px solid ${c.border};color:${c.color};padding:10px 16px;border-radius:8px;font-size:13px;font-weight:500;font-family:Inter,sans-serif;backdrop-filter:blur(12px);animation:slideIn .2s ease;max-width:300px;`;
  toast.textContent = msg;

  toastContainer.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity .3s'; setTimeout(() => toast.remove(), 300); }, 3000);
}

/* ── Form Validation ─────────────────────────────────────── */
function setupFormValidation() {
  document.querySelectorAll('form[data-validate]').forEach(form => {
    form.addEventListener('submit', e => {
      let valid = true;
      form.querySelectorAll('[required]').forEach(field => {
        if (!field.value.trim()) {
          field.style.borderColor = '#ef4444';
          field.style.boxShadow = '0 0 0 3px rgba(239,68,68,0.15)';
          valid = false;
          field.addEventListener('input', () => {
            field.style.borderColor = '';
            field.style.boxShadow = '';
          }, { once: true });
        }
      });
      if (!valid) {
        e.preventDefault();
        showToast('Please fill in all required fields.', 'error');
      }
    });
  });
}

/* ── Flash Auto-dismiss ──────────────────────────────────── */
function setupFlashDismiss() {
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .4s, max-height .4s';
      el.style.opacity = '0';
      el.style.maxHeight = '0';
      el.style.overflow = 'hidden';
      el.style.padding = '0';
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });
}

/* ── Init ────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initCharts();
  setupStatusDropdowns();
  setupFormValidation();
  setupFlashDismiss();
  bindCommandPaletteActions();
});
