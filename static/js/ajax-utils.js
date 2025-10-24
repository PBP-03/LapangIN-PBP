// AJAX Utility Functions for LapangIN

// CSRF Token helper
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Show notification/alert using toaster component
function showNotification(message, type = "error", duration = 5000) {
  // Use toaster utility if available
  if (typeof toasterUtils !== 'undefined') {
    toasterUtils.show({
      message: message,
      type: type,
      duration: duration
    });
  } else {
    // Fallback to console if toaster not loaded
    console.warn('Toaster not available:', message);
  }
}

// Generic AJAX request function
async function makeAjaxRequest(url, options = {}) {
  const defaultOptions = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
  };

  const finalOptions = { ...defaultOptions, ...options };

  try {
    const response = await fetch(url, finalOptions);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || `HTTP error! status: ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error("AJAX request failed:", error);
    throw error;
  }
}

// User authentication status check
async function checkUserStatus() {
  try {
    const data = await makeAjaxRequest("/api/user-status/");
    return data;
  } catch (error) {
    console.error("Failed to check user status:", error);
    return { authenticated: false };
  }
}

// Logout function
async function logoutUser() {
  try {
    const data = await makeAjaxRequest("/api/logout/", {
      method: "POST",
    });

    if (data.success) {
      showNotification(data.message, "success", 2000);

      // Clear localStorage
      localStorage.removeItem("user");

      // Redirect to home
      setTimeout(() => {
        window.location.href = "/";
      }, 1000);
    }
  } catch (error) {
    showNotification("Gagal logout. Silakan coba lagi.", "error");
  }
}

// Loading state helpers
function setLoadingState(element, loading = true, originalText = "") {
  if (loading) {
    element.disabled = true;
    element.dataset.originalText = element.textContent;
    element.innerHTML = `
      <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
      Loading...
    `;
  } else {
    element.disabled = false;
    element.textContent =
      originalText || element.dataset.originalText || "Submit";
  }
}

// Format datetime string
function formatDateTime(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("id-ID", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Format currency
function formatCurrency(amount) {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
  }).format(amount);
}

// Debounce function for search inputs
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
