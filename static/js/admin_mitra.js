// Toast component
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    
    const bgColor = type === 'success' ? 'bg-green-500' : 'bg-red-500';
    toast.className = `${bgColor} text-white px-4 py-3 rounded-lg shadow-lg mb-3 flex items-center animate-fade-in`;
    
    const icon = type === 'success' 
        ? '<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>'
        : '<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>';
    
    toast.innerHTML = `${icon}<span>${message}</span>`;
    container.appendChild(toast);

    // Remove toast after 3 seconds
    setTimeout(() => {
        toast.classList.add('animate-fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Modal handling
const rejectModal = document.getElementById('reject-modal');
const rejectReason = document.getElementById('reject-reason');
let pendingMitraId = null;

function showRejectModal(mitraId) {
    pendingMitraId = mitraId;
    rejectModal.classList.remove('hidden');
    rejectReason.value = '';
    rejectReason.focus();
}

function hideRejectModal() {
    rejectModal.classList.add('hidden');
    pendingMitraId = null;
    rejectReason.value = '';
}

document.getElementById('reject-cancel').addEventListener('click', hideRejectModal);
document.getElementById('reject-confirm').addEventListener('click', async () => {
    if (!pendingMitraId) return;
    const reason = rejectReason.value.trim();
    if (!reason) {
        showToast('Mohon isi alasan penolakan', 'error');
        rejectReason.focus();
        return;
    }
    await rejectMitra(pendingMitraId, reason);
    hideRejectModal();
});

// Main functionality
const apiListUrl = '/api/mitra/';

const state = {
    mitras: [],
    loading: false,
};

const bodyEl = document.getElementById('mitra-body');
const searchInput = document.getElementById('search-input');
const refreshBtn = document.getElementById('refresh-btn');

function setLoading(loading) {
    state.loading = loading;
    if (loading) {
        bodyEl.innerHTML = `
            <tr>
                <td colspan="5" class="py-8 text-center text-neutral-500">
                    <div class="inline-flex items-center gap-2">
                        <svg class="w-5 h-5 animate-spin text-primary-600" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                        </svg>
                        Memuat data...
                    </div>
                </td>
            </tr>`;
    }
}

async function fetchMitras() {
    setLoading(true);
    try {
        const res = await fetch(apiListUrl, { credentials: 'same-origin' });
        const json = await res.json();
        if (json.status !== 'ok') throw new Error(json.message || 'Failed to load');

        state.mitras = json.data || [];
        renderMitras();
    } catch (err) {
        bodyEl.innerHTML = `
            <tr>
                <td colspan="5" class="py-8 text-center text-red-600">
                    ${escapeHtml(err.message)}
                </td>
            </tr>`;
        console.error(err);
    } finally {
        setLoading(false);
    }
}

function renderMitras() {
    const filter = searchInput?.value.toLowerCase().trim() || '';
    const data = state.mitras.filter(m => {
        if (!filter) return true;
        return (m.nama || '').toLowerCase().includes(filter) || 
               (m.email || '').toLowerCase().includes(filter);
    });

    if (data.length === 0) {
        bodyEl.innerHTML = `
            <tr>
                <td colspan="5" class="py-8 text-center text-neutral-500">
                    ${filter ? 'Tidak ada hasil pencarian' : 'Tidak ada mitra'}
                </td>
            </tr>`;
        return;
    }

    bodyEl.innerHTML = '';
    data.forEach(m => {
        const row = document.createElement('tr');
        row.className = 'border-b hover:bg-neutral-50/50 transition-colors';

        const statusBadge = m.status === 'approved'
            ? '<span class="px-2 py-1 text-xs rounded-full text-green-700 bg-green-100 font-medium">Approved</span>'
            : m.status === 'rejected'
                ? '<span class="px-2 py-1 text-xs rounded-full text-red-700 bg-red-100 font-medium">Rejected</span>'
                : '<span class="px-2 py-1 text-xs rounded-full text-yellow-700 bg-yellow-100 font-medium">Pending</span>';

        row.innerHTML = `
            <td class="py-4 px-4">
                <div class="font-medium text-sm">${escapeHtml(m.nama)}</div>
                <div class="text-xs text-neutral-500 mt-1">${escapeHtml(m.deskripsi || '-')}</div>
            </td>
            <td class="py-4 px-4 text-sm">${escapeHtml(m.email)}</td>
            <td class="py-4 px-4" id="status-${m.id}">${statusBadge}</td>
            <td class="py-4 px-4 text-sm whitespace-nowrap">
                ${formatDate(m.tanggal_daftar)}
            </td>
            <td class="py-4 px-4">
                <div class="flex items-center gap-2" id="actions-${m.id}">
                    ${m.status === 'pending' ? `
                        <button
                            onclick="approveMitra('${m.id}')"
                            class="inline-flex items-center px-3 py-1.5 text-xs font-medium text-white bg-green-500 hover:bg-green-600 rounded-lg transition-colors"
                        >
                            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                            Approve
                        </button>
                        <button
                            onclick="showRejectModal('${m.id}')"
                            class="inline-flex items-center px-3 py-1.5 text-xs font-medium text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors"
                        >
                            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                            Reject
                        </button>
                    ` : ''}
                </div>
            </td>
        `;
        bodyEl.appendChild(row);
    });
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('id-ID', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(unsafe) {
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

async function approveMitra(id) {
    if (!confirm('Setujui mitra ini?')) return;
    // ...existing code...
}

async function rejectMitra(id, reason) {
    // Disable actions
    const actionsEl = document.getElementById(`actions-${id}`);
    if (actionsEl) actionsEl.innerHTML = `
        <div class="inline-flex items-center gap-2 text-neutral-500">
            <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
            </svg>
            Memproses...
        </div>`;

    try {
        const res = await fetch(`/api/mitra/${id}/`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'rejected', alasan_penolakan: reason }),
            credentials: 'same-origin'
        });

        const json = await res.json();
        if (json.status !== 'ok') throw new Error(json.message || 'Update failed');

        // Update status badge
        const statusCell = document.getElementById(`status-${id}`);
        if (statusCell) {
            statusCell.innerHTML = '<span class="px-2 py-1 text-xs rounded-full text-red-700 bg-red-100 font-medium">Rejected</span>';
        }

        // Hide actions
        if (actionsEl) actionsEl.innerHTML = '';

        // Update local state
        const idx = state.mitras.findIndex(x => x.id === id);
        if (idx !== -1) state.mitras[idx].status = 'rejected';

        // Show success message
        showToast('Mitra berhasil ditolak', 'success');

    } catch (err) {
        showToast(err.message || 'Gagal memproses penolakan', 'error');
        console.error(err);
        renderMitras(); // Re-render to restore buttons
    }
}

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    .animate-fade-in {
        animation: fadeIn 0.3s ease-out;
    }
    .animate-fade-out {
        animation: fadeOut 0.3s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(1rem); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeOut {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(1rem); }
    }
`;
document.head.appendChild(style);

// Initialize
if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
        showToast('Memuat ulang data...', 'success');
        fetchMitras();
    });
}
if (searchInput) searchInput.addEventListener('input', () => renderMitras());

// Close modal on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') hideRejectModal();
});

// Close modal on outside click
rejectModal.addEventListener('click', (e) => {
    if (e.target === rejectModal) hideRejectModal();
});

// Load initial data
fetchMitras();