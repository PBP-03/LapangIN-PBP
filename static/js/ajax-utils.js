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

// Show notification/alert
function showNotification(message, type = "error", duration = 5000) {
  // Remove existing notifications
  const existingNotification = document.getElementById("notification");
  if (existingNotification) {
    existingNotification.remove();
  }

  const notification = document.createElement("div");
  notification.id = "notification";
  notification.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-xl shadow-lg border transform transition-all duration-300 translate-x-full opacity-0`;

  if (type === "success") {
    notification.className += " bg-green-50 border-green-200 text-green-800";
  } else if (type === "warning") {
    notification.className += " bg-yellow-50 border-yellow-200 text-yellow-800";
  } else {
    notification.className += " bg-red-50 border-red-200 text-red-800";
  }

  notification.innerHTML = `
    <div class="flex items-center">
      <div class="flex-shrink-0">
        ${
          type === "success"
            ? '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>'
            : '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>'
        }
      </div>
      <div class="ml-3">
        <p class="text-sm font-medium">${message}</p>
      </div>
      <div class="ml-4 flex-shrink-0">
        <button onclick="this.parentElement.parentElement.parentElement.remove()" class="text-current opacity-70 hover:opacity-100">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
          </svg>
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(notification);

  // Animate in
  setTimeout(() => {
    notification.classList.remove("translate-x-full", "opacity-0");
  }, 100);

  // Auto remove
  if (duration > 0) {
    setTimeout(() => {
      notification.classList.add("translate-x-full", "opacity-0");
      setTimeout(() => {
        if (notification.parentNode) {
          notification.remove();
        }
      }, 300);
    }, duration);
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
