 (function () {
  const API_LIST = "/api/mitra_list/";
  const API_DETAIL = (id) => `/api/mitra_detail/${id}/`;
  let currentSort = { key: 'tanggal_daftar', dir: 'desc' };

  function escapeHtml(unsafe) {
    if (!unsafe) return "";
    return String(unsafe)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function showToast(message, type = "success", timeout = 3500) {
    const root = document.getElementById('toast-root') || document.body;
    const el = document.createElement('div');
    // keep an identifiable class and inline style for compatibility
    el.className = 'toast-item px-4 py-2 rounded text-white shadow-lg transition-all duration-300';
    el.style.zIndex = 9999;
    el.style.opacity = '0';
    el.style.transform = 'translateY(8px)';
    if (type === 'success') el.style.background = 'linear-gradient(90deg,#16a34a,#22c55e)';
    else if (type === 'error') el.style.background = 'linear-gradient(90deg,#dc2626,#f97316)';
    else el.style.background = 'rgba(55,65,81,0.95)';
    el.textContent = message;
    (root === document.body ? document.body.appendChild(el) : root.appendChild(el));
    // fade in
    requestAnimationFrame(()=>{ el.style.opacity='1'; el.style.transform='translateY(0)'; });
    // fade out after timeout
    setTimeout(()=>{
      el.style.opacity='0';
      el.style.transform='translateY(8px)';
      setTimeout(()=>el.remove(), 300);
    }, timeout);
  }

  async function fetchMitra() {
    try {
      document.getElementById('table-loading')?.classList.remove('hidden');
      const res = await fetch(API_LIST, { credentials: "same-origin" });
      if (!res.ok) throw new Error("Gagal memuat data");
      const json = await res.json();
      const items = json.data || json;
      // apply current sort
      const sorted = sortItems(items, currentSort.key, currentSort.dir);
      renderTable(sorted);
    } catch (err) {
      showToast("Gagal memuat daftar mitra", 'error');
      console.error(err);
    } finally {
      document.getElementById('table-loading')?.classList.add('hidden');
    }
  }

  function renderTable(items) {
    const tbody = document.getElementById("mitra-tbody");
    tbody.innerHTML = "";
    if (!items || items.length === 0) {
      tbody.innerHTML = `<tr><td class="px-4 py-6 text-center text-neutral-500" colspan="7">Belum ada mitra.</td></tr>`;
      return;
    }
    items.forEach(m => {
      const tr = document.createElement("tr");
      const tanggal = m.tanggal_daftar ? new Date(m.tanggal_daftar).toLocaleString('id-ID') : '-';
      tr.innerHTML = `
        <td class="px-4 py-3 align-top">${escapeHtml(m.nama)}</td>
        <td class="px-4 py-3 align-top">${escapeHtml(m.email)}</td>
        <td class="px-4 py-3 align-top">${escapeHtml(m.deskripsi || '')}</td>
        <td class="px-4 py-3 align-top">${m.gambar_url ? `<img src="${m.gambar_url}" class="w-20 h-20 rounded-lg object-cover border" alt="gambar mitra"/>` : '-'}</td>
        <td class="px-4 py-3 align-top">${statusBadge(m.status)}</td>
        <td class="px-4 py-3 align-top">${escapeHtml(tanggal)}</td>
        <td class="px-4 py-3 align-top">${actionButtons(m.id)}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  // render helpers (reused from template style)
  function statusBadge(status) {
    if (status === 'approved') return '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">✔ Approved</span>';
    if (status === 'rejected') return '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">✖ Rejected</span>';
    return '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">● Pending</span>';
  }

  function actionButtons(id) {
    return `
      <button data-id="${id}" data-action="approve" class="acc-btn inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-all">
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
        <span>ACC</span>
      </button>
      <button data-id="${id}" data-action="reject" class="reject-btn inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-red-500 text-white hover:bg-red-600 transition-all ml-2">
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        <span>Tolak</span>
      </button>
    `;
  }

  async function updateStatus(id, status, btn) {
    try {
      const row = btn ? btn.closest('tr') : null;
      const buttons = row ? row.querySelectorAll('button') : [];
      buttons.forEach(b => b.setAttribute('disabled', 'disabled'));
      const body = { status };
      // if there's a reject reason stored on modal, include it
      const modal = document.getElementById('rejectModal');
      if (modal && modal.dataset && modal.dataset.pendingReasonFor == String(id)) {
        body.reason = modal.dataset.pendingReason || '';
      }
      const res = await fetch(API_DETAIL(id), {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        credentials: "same-origin",
      });
      const data = await res.json().catch(()=>({status:"error", message:"Invalid response"}));
      if (!res.ok || data.status !== "ok") {
        showToast(data.message || "Gagal mengubah status", 'error');
        return;
      }
      // update badge cell
      if (row) {
        const badgeCell = row.querySelector('td:nth-child(3)');
        if (badgeCell) badgeCell.innerHTML = statusBadge(data.data.status);
      }
      showToast(data.message || "Berhasil", 'success');
    } catch (err) {
      console.error(err);
      showToast("Gagal mengubah status", 'error');
    }
    finally {
      // re-enable
      try { buttons.forEach(b => b.removeAttribute('disabled')); } catch(e){}
    }
  }

  // delegate clicks for action buttons
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    const action = btn.getAttribute('data-action');
    const id = btn.getAttribute('data-id');
    if (!action || !id) return;
      if (action === 'approve') {
        // approve directly
        updateStatus(id, 'approved', btn);
      } else if (action === 'reject') {
        // open reject modal and store id
        const modal = document.getElementById('rejectModal');
        if (!modal) {
          showToast('Modal penolakan tidak ditemukan', 'error');
          return;
        }
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        modal.dataset.currentId = id;
      }
  });

  // refresh button
  document.getElementById('refresh-btn')?.addEventListener('click', ()=> fetchMitra());

  // Modal handlers
  document.getElementById('cancelReject')?.addEventListener('click', ()=>{
    const modal = document.getElementById('rejectModal');
    if (!modal) return;
    modal.classList.add('hidden'); modal.classList.remove('flex');
    document.getElementById('rejectReason').value = '';
    delete modal.dataset.currentId;
    delete modal.dataset.pendingReason;
    delete modal.dataset.pendingReasonFor;
  });

  document.getElementById('confirmReject')?.addEventListener('click', async ()=>{
    const modal = document.getElementById('rejectModal');
    if (!modal) return;
    const id = modal.dataset.currentId;
    const reason = document.getElementById('rejectReason').value || '';
    if (!id) {
      showToast('ID mitra tidak ditemukan', 'error');
      return;
    }
    // store the pending reason on modal to be read by updateStatus
    modal.dataset.pendingReason = reason;
    modal.dataset.pendingReasonFor = id;
    // call updateStatus which will pick up the reason
    // find a button in the row to pass for disabled toggling
    const btn = document.querySelector(`button[data-id="${id}"]`);
    await updateStatus(id, 'rejected', btn);
    // hide modal and clear
    modal.classList.add('hidden'); modal.classList.remove('flex');
    document.getElementById('rejectReason').value = '';
    delete modal.dataset.currentId;
    delete modal.dataset.pendingReason;
    delete modal.dataset.pendingReasonFor;
    // refresh list
    fetchMitra();
  });

  // sorting
  function sortItems(items, key, dir) {
    if (!items) return [];
    const copy = items.slice();
    copy.sort((a,b)=>{
      let va = a[key]; let vb = b[key];
      if (key === 'tanggal_daftar') { va = new Date(va||0); vb = new Date(vb||0); }
      if (va < vb) return dir === 'asc' ? -1 : 1;
      if (va > vb) return dir === 'asc' ? 1 : -1;
      return 0;
    });
    return copy;
  }

  // header click sorting
  document.querySelectorAll('th[data-sort-key]').forEach(th=>{
    th.addEventListener('click', ()=>{
      const key = th.getAttribute('data-sort-key');
      if (currentSort.key === key) currentSort.dir = currentSort.dir === 'asc' ? 'desc' : 'asc';
      else { currentSort.key = key; currentSort.dir = 'asc'; }
      fetchMitra();
    });
  });

  document.addEventListener("DOMContentLoaded", fetchMitra);
})();
