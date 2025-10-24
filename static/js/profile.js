document.addEventListener('DOMContentLoaded', async function () {
  const saveBtn = document.getElementById('saveProfileBtn');
  const deleteBtn = document.getElementById('deleteProfileBtn');
  const bookingsContainer = document.getElementById('myBookings');

  async function loadProfile() {
    try {
      const resp = await makeAjaxRequest('/api/profile/');
      if (resp.success) {
        // Expect server to return { success: true, data: { user: { ... } } }
        const u = resp.data && resp.data.user ? resp.data.user : null;
        if (!u) {
          showNotification('Format response profil tidak dikenali', 'error');
          return;
        }
        document.getElementById('first_name').value = u.first_name || '';
        document.getElementById('last_name').value = u.last_name || '';
        document.getElementById('email').value = u.email || '';
        document.getElementById('phone_number').value = u.phone_number || '';
        document.getElementById('address').value = u.address || '';
      } else {
        showNotification('Gagal memuat profil', 'error');
      }
    } catch (e) {
      showNotification('Gagal memuat profil', 'error');
    }
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
        const u = resp.data && resp.data.user ? resp.data.user : null;
        if (u) {
          document.getElementById('first_name').value = u.first_name || '';
          document.getElementById('last_name').value = u.last_name || '';
          document.getElementById('email').value = u.email || '';
          document.getElementById('phone_number').value = u.phone_number || '';
          document.getElementById('address').value = u.address || '';

          try {
            const stored = JSON.parse(localStorage.getItem('user') || '{}');
            const updated = { ...stored, ...u };
            localStorage.setItem('user', JSON.stringify(updated));
          } catch (e) {
            // ignore
          }
        } else {
          // fallback: reload profile from server
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
      } else {
        showNotification(resp.message || 'Gagal menghapus akun', 'error');
      }
    } catch (e) {
      showNotification('Gagal menghapus akun', 'error');
    }
  });

  await loadProfile();
  await loadBookings();
});

// Profile helpers
async function getProfile() {
  try {
    const data = await makeAjaxRequest("/api/profile/");
    return data; // { success: true, user: {...} }
  } catch (err) {
    console.error("Failed to load profile:", err);
    throw err;
  }
}

async function updateProfile(payload) {
  try {
    const data = await makeAjaxRequest("/api/profile/", {
      method: "PUT",
      body: JSON.stringify(payload),
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
        Accept: "application/json",
      },
    });
    return data;
  } catch (err) {
    console.error("Failed to update profile:", err);
    throw err;
  }
}

async function deleteProfile() {
  try {
    const data = await makeAjaxRequest("/api/profile/", {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
        Accept: "application/json",
      },
    });
    return data;
  } catch (err) {
    console.error("Failed to delete profile:", err);
    throw err;
  }
}