document.addEventListener('DOMContentLoaded', async function () {
  const saveBtn = document.getElementById('saveProfileBtn');
  const deleteBtn = document.getElementById('deleteProfileBtn');
  const bookingsContainer = document.getElementById('myBookings');

  async function loadProfile() {
    try {
      const resp = await makeAjaxRequest('/api/profile/');
      if (resp.success) {
        const d = resp.data;
        document.getElementById('first_name').value = d.first_name || '';
        document.getElementById('last_name').value = d.last_name || '';
        document.getElementById('email').value = d.email || '';
        document.getElementById('phone_number').value = d.phone_number || '';
        document.getElementById('address').value = d.address || '';
      } else {
        showNotification('Gagal memuat profil', 'error');
      }
    } catch (e) {
      showNotification('Gagal memuat profil', 'error');
    }
  }

  async function loadBookings() {
    bookingsContainer.innerHTML = '<div class="text-sm text-neutral-600">Daftar booking ditampilkan jika endpoint tersedia.</div>';
  }

  saveBtn.addEventListener('click', async () => {
    const payload = {
      first_name: document.getElementById('first_name').value,
      last_name: document.getElementById('last_name').value,
      email: document.getElementById('email').value,
      phone_number: document.getElementById('phone_number').value,
      address: document.getElementById('address').value,
    };

    try {
      const resp = await makeAjaxRequest('/api/profile/', {
        method: 'PUT',
        body: JSON.stringify(payload),
      });

      if (resp.success) {
        showNotification(resp.message || 'Profil diperbarui', 'success');

        // If backend returned updated user data, apply it immediately
        if (resp.data && resp.data.user) {
          const u = resp.data.user;
          // update form fields (in case backend normalized values)
          document.getElementById('first_name').value = u.first_name || '';
          document.getElementById('last_name').value = u.last_name || '';
          document.getElementById('email').value = u.email || '';
          document.getElementById('phone_number').value = u.phone_number || '';
          document.getElementById('address').value = u.address || '';

          // update localStorage copy of user if used elsewhere
          try {
            const stored = JSON.parse(localStorage.getItem('user') || '{}');
            const updated = { ...stored, ...u };
            localStorage.setItem('user', JSON.stringify(updated));
          } catch (e) {
            // ignore JSON errors
          }

          // Optionally update visible navbar text if your navbar reads from DOM elements
          const navNameEl = document.querySelector('#navbar .text-neutral-900') || null;
          if (navNameEl && u.first_name) {
            navNameEl.textContent = u.first_name + (u.last_name ? ' ' + u.last_name : '');
          }
        } else {
          // Fallback: re-fetch profile to ensure UI matches server
          await loadProfile();
        }
      } else {
        showNotification(resp.message || 'Gagal menyimpan profil', 'error');
      }
    } catch (e) {
      showNotification('Gagal menyimpan profil', 'error');
    }
  });

  deleteBtn.addEventListener('click', async () => {
    if (!confirm('Yakin ingin menghapus akun Anda? Semua data akan hilang.')) return;
    try {
      const resp = await makeAjaxRequest('/api/profile/', { method: 'DELETE' });
      if (resp.success) {
        showNotification('Akun dihapus. Mengarahkan ke beranda...', 'success');
        setTimeout(() => window.location.href = '/', 1200);
      } else showNotification(resp.message || 'Gagal menghapus akun', 'error');
    } catch (e) {
      showNotification('Gagal menghapus akun', 'error');
    }
  });

  window.cancelBooking = async function (bookingId) {
    if (!confirm('Batalkan booking ini?')) return;
    try {
      const resp = await makeAjaxRequest(`/api/booking/${bookingId}/`, { method: 'DELETE' });
      if (resp.success) {
        showNotification(resp.message || 'Booking dibatalkan', 'success');
        loadBookings();
      } else showNotification(resp.message || 'Gagal membatalkan booking', 'error');
    } catch (e) {
      showNotification('Gagal membatalkan booking', 'error');
    }
  };

  await loadProfile();
  await loadBookings();
});