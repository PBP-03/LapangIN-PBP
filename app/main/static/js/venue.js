// venue.js - consolidated
const staticBase = window.staticUrl || "/static/";

// Pagination settings
const ITEMS_PER_PAGE = 9;
let currentPage = 1;
let allVenues = [];

function renderVenueList(venues) {
  const container = document.getElementById('venue-list');
  const countEl = document.getElementById('venue-count-number');
  let list = venues;
  
    // If no venues provided, try server-provided data
  if (!list) {
    list = window.venuesData || [];
  }

  // Always filter and sort the list
  if (window.lastAppliedParams) {
    list = applyFilters(list, window.lastAppliedParams);
  }
  if (window.lastSortBy) {
    list = sortVenues(list, window.lastSortBy);
  }

  // Show "no results" message if no venues match filters
  if (!list || !list.length) {
    container.innerHTML =
      '<div class="col-span-full text-center py-12 text-neutral-600">Tidak ada venue yang sesuai dengan pencarian.</div>';
    if (countEl) countEl.textContent = "0";
    return;
  }

  // Store all venues for pagination
  allVenues = list;

  if (countEl) countEl.textContent = list.length;

  // Calculate pagination
  const totalPages = Math.ceil(list.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = startIndex + ITEMS_PER_PAGE;
  const paginatedList = list.slice(startIndex, endIndex);

  container.innerHTML = "";
  paginatedList.forEach((v) => {
    renderVenueCard(container, v);
  });

  // Render pagination
  renderPagination(totalPages);
}

function renderVenueListFromServer(venues) {
  const container = document.getElementById("venue-list");

  // Show "no results" message if no venues
  if (!venues || !venues.length) {
    container.innerHTML =
      '<div class="col-span-full text-center py-12 text-neutral-600">Tidak ada venue yang sesuai dengan pencarian.</div>';
    return;
  }

  container.innerHTML = "";
  venues.forEach((v) => {
    renderVenueCard(container, v);
  });
}

function renderVenueCard(container, v) {
  const imgSrc =
    v.images && v.images.length ? v.images[0] : staticBase + "img/no-image.png";
  const cardWrap = document.createElement("div");
  cardWrap.className = "rounded-2xl bg-white shadow-soft overflow-hidden";
  // Prefer using the venue's UUID-like id when available (safe and unambiguous).
  // Otherwise fall back to the URL-encoded venue name (for dummy/test data).
  let detailId = "";
  if (
    v.id &&
    typeof v.id === "string" &&
    v.id.indexOf("-") !== -1 &&
    v.id.length > 20
  ) {
    // Probably a UUID
    detailId = v.id;
  } else {
    detailId = encodeURIComponent(v.name || v.id || "");
  }
  const detailHref = `/lapangan/${detailId}/`;

  cardWrap.innerHTML = `
      <a href="${detailHref}" class="block hover:shadow-medium transition-shadow">
        <div class="relative h-48 bg-neutral-50">
          <img src="${imgSrc}" alt="${
    v.name
  }" class="w-full h-full object-cover" />
          ${
            v.category
              ? `<div class="absolute top-3 left-3 bg-white/95 backdrop-blur-sm text-xs px-3 py-1.5 rounded-full font-semibold text-neutral-700 shadow-soft">${v.category}</div>`
              : ""
          }
        </div>
        <div class="p-5">
          <h3 class="text-lg font-display font-semibold mb-2 text-neutral-900 line-clamp-1">${
            v.name
          }</h3>
          
          <!-- Rating -->
          <div class="flex items-center gap-1 mb-3">
            <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.974a1 1 0 00.95.69h4.178c.969 0 1.371 1.24.588 1.81l-3.38 2.455a1 1 0 00-.364 1.118l1.287 3.974c.3.921-.755 1.688-1.54 1.118l-3.38-2.455a1 1 0 00-1.175 0l-3.38 2.455c-.784.57-1.839-.197-1.54-1.118l1.286-3.974a1 1 0 00-.364-1.118l-3.38-2.455c-.783-.57-.38-1.81.588-1.81h4.178a1 1 0 00.95-.69l1.287-3.974z"/>
            </svg>
            <span class="text-sm font-semibold text-neutral-900">${(
              v.avg_rating || 0
            ).toFixed(1)}</span>
            <span class="text-sm text-neutral-500">(${
              v.rating_count || 0
            } reviews)</span>
          </div>
          
          <!-- Address -->
          <div class="flex items-start gap-2 text-sm text-neutral-600 mb-4">
            <svg class="w-4 h-4 mt-0.5 flex-shrink-0 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            <span class="line-clamp-2">${
              v.address || "Alamat tidak tersedia"
            }</span>
          </div>
          
          <!-- Price and Action -->
          <div class="flex items-center justify-between pt-3 border-t border-neutral-100">
            <div>
              <div class="text-xs text-neutral-500 mb-0.5">Mulai dari</div>
              <div class="text-lg font-bold text-primary-600">Rp ${(
                v.price_per_hour ||
                v.price ||
                0
              ).toLocaleString("id-ID")}</div>
              <div class="text-xs text-neutral-500">/ jam</div>
            </div>
            <div class="gradient-primary text-white px-5 py-2.5 rounded-xl text-sm font-medium hover:shadow-medium transition-all">
              Lihat Detail
            </div>
          </div>
        </div>
      </a>
    `;
  container.appendChild(cardWrap);
}

function renderServerPagination(pagination) {
  const paginationContainer = document.getElementById("pagination-container");

  if (!paginationContainer || !pagination || pagination.total_pages <= 1) {
    if (paginationContainer) paginationContainer.innerHTML = "";
    return;
  }

  const currentPage = pagination.page;
  const totalPages = pagination.total_pages;

  let paginationHTML = "";

  // First Page Button
  paginationHTML += `
    <button onclick="goToPage(1)" 
            class="px-4 py-2 rounded-lg border ${
              currentPage === 1
                ? "bg-neutral-100 text-neutral-400 cursor-not-allowed"
                : "bg-white text-neutral-700 hover:bg-neutral-50 border-neutral-300"
            } transition-all"
            ${currentPage === 1 ? "disabled" : ""}>
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"/>
      </svg>
    </button>
  `;

  // Previous Button
  paginationHTML += `
    <button onclick="goToPage(${currentPage - 1})" 
            class="px-4 py-2 rounded-lg border ${
              currentPage === 1
                ? "bg-neutral-100 text-neutral-400 cursor-not-allowed"
                : "bg-white text-neutral-700 hover:bg-neutral-50 border-neutral-300"
            } transition-all"
            ${currentPage === 1 ? "disabled" : ""}>
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
      </svg>
    </button>
  `;

  // Page Numbers
  const maxVisiblePages = 5;
  let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
  let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

  // Adjust start if we're near the end
  if (endPage - startPage < maxVisiblePages - 1) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1);
  }

  // Show first page and ellipsis if needed
  if (startPage > 1) {
    paginationHTML += `
      <button onclick="goToPage(1)" 
              class="px-4 py-2 rounded-lg border bg-white text-neutral-700 hover:bg-neutral-50 border-neutral-300 transition-all">
        1
      </button>
    `;
    if (startPage > 2) {
      paginationHTML += `<span class="px-2 text-neutral-500">...</span>`;
    }
  }

  // Page number buttons
  for (let i = startPage; i <= endPage; i++) {
    paginationHTML += `
      <button onclick="goToPage(${i})" 
              class="px-4 py-2 rounded-lg border ${
                i === currentPage
                  ? "gradient-primary text-white font-semibold"
                  : "bg-white text-neutral-700 hover:bg-neutral-50 border-neutral-300"
              } transition-all">
        ${i}
      </button>
    `;
  }

  // Show last page and ellipsis if needed
  if (endPage < totalPages) {
    if (endPage < totalPages - 1) {
      paginationHTML += `<span class="px-2 text-neutral-500">...</span>`;
    }
    paginationHTML += `
      <button onclick="goToPage(${totalPages})" 
              class="px-4 py-2 rounded-lg border bg-white text-neutral-700 hover:bg-neutral-50 border-neutral-300 transition-all">
        ${totalPages}
      </button>
    `;
  }

  // Next Button
  paginationHTML += `
    <button onclick="goToPage(${currentPage + 1})" 
            class="px-4 py-2 rounded-lg border ${
              currentPage === totalPages
                ? "bg-neutral-100 text-neutral-400 cursor-not-allowed"
                : "bg-white text-neutral-700 hover:bg-neutral-50 border-neutral-300"
            } transition-all"
            ${currentPage === totalPages ? "disabled" : ""}>
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
      </svg>
    </button>
  `;

  // Last Page Button
  paginationHTML += `
    <button onclick="goToPage(${totalPages})" 
            class="px-4 py-2 rounded-lg border ${
              currentPage === totalPages
                ? "bg-neutral-100 text-neutral-400 cursor-not-allowed"
                : "bg-white text-neutral-700 hover:bg-neutral-50 border-neutral-300"
            } transition-all"
            ${currentPage === totalPages ? "disabled" : ""}>
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"/>
      </svg>
    </button>
  `;

  paginationContainer.innerHTML = paginationHTML;
}

function goToPage(page) {
  const pagination = window.currentPagination || {};
  const totalPages = pagination.total_pages || 1;

  if (page < 1 || page > totalPages) return;

  // Fetch new page from server
  const searchForm = document.getElementById("venue-search-form");
  const params = searchForm ? Object.fromEntries(new FormData(searchForm)) : {};
  fetchAndRenderVenueList(params, page);

  // Scroll to top of venue list
  document
    .getElementById("venue-list")
    .scrollIntoView({ behavior: "smooth", block: "start" });
}

// Keep old client-side pagination function for fallback
function renderPagination(totalPages) {
  const paginationContainer = document.getElementById("pagination-container");

  if (!paginationContainer || totalPages <= 1) {
    if (paginationContainer) paginationContainer.innerHTML = "";
    return;
  }

  let paginationHTML = "";

  // First Page Button
  paginationHTML += `
    <button onclick="goToPage(1)" 
            class="px-4 py-2 rounded-lg border ${
              currentPage === 1
                ? "bg-neutral-100 text-neutral-400 cursor-not-allowed"
                : "bg-white text-neutral-700 hover:bg-neutral-50 border-neutral-300"
            } transition-all"
            ${currentPage === 1 ? "disabled" : ""}>
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"/>
      </svg>
    </button>
  `;

  // Previous Button
  paginationHTML += `
    <button onclick="goToPage(${currentPage - 1})" 
            class="px-4 py-2 rounded-lg border ${
              currentPage === 1
                ? "bg-neutral-100 text-neutral-400 cursor-not-allowed"
                : "bg-white text-neutral-700 hover:bg-neutral-50 border-neutral-300"
            } transition-all"
            ${currentPage === 1 ? "disabled" : ""}>
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
      </svg>
    </button>
  `;

  // Page Numbers
  const maxVisiblePages = 5;
  let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
  let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

  if (endPage - startPage < maxVisiblePages - 1) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1);
  }

  if (startPage > 1) {
    paginationHTML += `
      <button onclick="goToPage(1)" 
              class="px-4 py-2 rounded-lg border bg-white text-neutral-700 hover:bg-neutral-50 border-neutral-300 transition-all">
        1
      </button>
    `;
    if (startPage > 2) {
      paginationHTML += `<span class="px-2 text-neutral-500">...</span>`;
    }
  }

  for (let i = startPage; i <= endPage; i++) {
    paginationHTML += `
      <button onclick="goToPage(${i})" 
              class="px-4 py-2 rounded-lg border ${
                i === currentPage
                  ? "gradient-primary text-white font-semibold"
                  : "bg-white text-neutral-700 hover:bg-neutral-50 border-neutral-300"
              } transition-all">
        ${i}
      </button>
    `;
  }

  if (endPage < totalPages) {
    if (endPage < totalPages - 1) {
      paginationHTML += `<span class="px-2 text-neutral-500">...</span>`;
    }
    paginationHTML += `
      <button onclick="goToPage(${totalPages})" 
              class="px-4 py-2 rounded-lg border bg-white text-neutral-700 hover:bg-neutral-50 border-neutral-300 transition-all">
        ${totalPages}
      </button>
    `;
  }

  // Next Button
  paginationHTML += `
    <button onclick="goToPage(${currentPage + 1})" 
            class="px-4 py-2 rounded-lg border ${
              currentPage === totalPages
                ? "bg-neutral-100 text-neutral-400 cursor-not-allowed"
                : "bg-white text-neutral-700 hover:bg-neutral-50 border-neutral-300"
            } transition-all"
            ${currentPage === totalPages ? "disabled" : ""}>
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
      </svg>
    </button>
  `;

  // Last Page Button
  paginationHTML += `
    <button onclick="goToPage(${totalPages})" 
            class="px-4 py-2 rounded-lg border ${
              currentPage === totalPages
                ? "bg-neutral-100 text-neutral-400 cursor-not-allowed"
                : "bg-white text-neutral-700 hover:bg-neutral-50 border-neutral-300"
            } transition-all"
            ${currentPage === totalPages ? "disabled" : ""}>
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"/>
      </svg>
    </button>
  `;

  paginationContainer.innerHTML = paginationHTML;
}

// expose render function globally
window._renderVenueList = renderVenueList;
window.goToPage = goToPage;

function sortVenues(venues, sortBy) {
  if (!venues) return venues;
  const list = venues.slice(); // Create copy for sorting

  if (sortBy === "price_low") {
    return list.sort((a, b) => {
      const priceA = Number(a.price_per_hour || 0);
      const priceB = Number(b.price_per_hour || 0);
      return priceA - priceB;
    });
  }
  if (sortBy === "price_high") {
    return list.sort((a, b) => {
      const priceA = Number(a.price_per_hour || 0);
      const priceB = Number(b.price_per_hour || 0);
      return priceB - priceA;
    });
  }
  if (sortBy === "rating") {
    return list.sort((a, b) => {
      const ratingA = Number(b.avg_rating || 0);
      const ratingB = Number(a.avg_rating || 0);
      // If ratings equal, sort by number of reviews
      if (ratingA === ratingB) {
        return Number(b.rating_count || 0) - Number(a.rating_count || 0);
      }
      return ratingA - ratingB;
    });
  }
  return list;
}

function applyFilters(venues, params) {
  if (!params) return venues;
  return venues.filter((v) => {
    // name
    if (params.name && params.name.trim() !== "") {
      if (
        !v.name ||
        !v.name.toLowerCase().includes(params.name.trim().toLowerCase())
      )
        return false;
    }
    // category exact match (case-insensitive)
    if (params.category && params.category !== "") {
      // Exact match case-insensitive (both should be uppercase per seed data)
      const searchCat = params.category.trim().toUpperCase();
      const venueCat = (v.category || "").toUpperCase();
      if (venueCat !== searchCat) return false;
    }
    // location (address contains)
    if (params.location && params.location.trim() !== "") {
      if (
        !v.address ||
        !v.address.toLowerCase().includes(params.location.trim().toLowerCase())
      )
        return false;
    }
    // price range
    const minp =
      params.min_price !== undefined && params.min_price !== ""
        ? Number(params.min_price)
        : null;
    const maxp =
      params.max_price !== undefined && params.max_price !== ""
        ? Number(params.max_price)
        : null;
    const price = Number(v.price_per_hour || v.price || 0);
    if (minp !== null && !isNaN(minp) && price < minp) return false;
    if (maxp !== null && !isNaN(maxp) && price > maxp) return false;
    // min rating (treat as threshold)
    const minr =
      params.min_rating !== undefined && params.min_rating !== ""
        ? Number(params.min_rating)
        : null;
    const rating = Number(v.avg_rating || 0);
    if (minr !== null && !isNaN(minr) && rating < minr) return false;
    return true;
  });
}

function fetchAndRenderVenueList(params = {}, page = 1) {
  // Store current page
  currentPage = page;

  // params is an object of form values
  const url = new URL("/api/public/venues/", window.location.origin);
  Object.keys(params).forEach((k) => {
    if (params[k]) url.searchParams.append(k, params[k]);
  });

  // Add pagination params
  url.searchParams.append("page", page);
  url.searchParams.append("page_size", ITEMS_PER_PAGE);

  fetch(url)
    .then((res) => res.json())
    .then((json) => {
      let venues = json.data;
      const pagination = json.pagination || {};
      // If API returns empty, prefer server snapshot injected into the page
      if (
        (!venues || venues.length === 0) &&
        Array.isArray(window.venuesData) &&
        window.venuesData.length > 0
      ) {
        venues = window.venuesData;
      }
      // If still empty, show empty state
      if (!venues || venues.length === 0) {
        venues = [];
      } else {
        // apply rating filter on API or server data too if client requested
        venues = applyFilters(venues, params);
      }

      // Ensure we prefer UUID-style ids from server data (they're strings)
      venues = venues.map((v) => {
        // if the server snapshot uses string ids (UUID), keep them; otherwise
        // prefer to keep existing id (dummy) which will be encoded as name-based url
        if (v.id && typeof v.id === "string") return v;
        return v;
      });

      // Store pagination info globally
      window.currentPagination = pagination;

      // Update total count
      const countEl = document.getElementById("venue-count-number");
      if (countEl)
        countEl.textContent = pagination.total_count || venues.length;

      const sortSelect = document.getElementById("venue-sort");
      const sortBy = sortSelect ? sortSelect.value : "";
      venues = sortVenues(venues, sortBy);

      // Store venues for rendering
      allVenues = venues;

      // Render venues (already paginated from server)
      renderVenueListFromServer(venues);

      // Render pagination controls
      renderServerPagination(pagination);
    })
    .catch((err) => {
      console.error("Error fetching venues:", err);
      // On error, show empty state
      const container = document.getElementById("venue-list");
      container.innerHTML =
        '<div class="col-span-full text-center py-12 text-neutral-600">Gagal memuat data venue.</div>';
    });
}

// bootstrap: wire up form and sort
document.addEventListener("DOMContentLoaded", function () {
  const searchForm = document.getElementById("venue-search-form");
  const sortSelect = document.getElementById("venue-sort");
  let lastParams = {};
  // If the server injected a snapshot of venues, render it immediately so
  // links point to real IDs (UUIDs) instead of client-only dummy ids.
  if (Array.isArray(window.venuesData) && window.venuesData.length > 0) {
    // Apply any initial filters (none) and render
    renderVenueList(window.venuesData);
  }
  if (searchForm) {
    searchForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const params = Object.fromEntries(new FormData(searchForm));
      window.lastAppliedParams = params; // Store for re-use
      fetchAndRenderVenueList(params, 1); // Reset to page 1 on new search
    });

    // Update search as you type
    searchForm
      .querySelectorAll('input[type="text"], input[type="number"]')
      .forEach((input) => {
        input.addEventListener("input", function () {
          const params = Object.fromEntries(new FormData(searchForm));
          window.lastAppliedParams = params;
          fetchAndRenderVenueList(params, 1);
        });
      });

    // Update on category change
    const categorySelect = searchForm.querySelector('select[name="category"]');
    if (categorySelect) {
      categorySelect.addEventListener("change", function () {
        const params = Object.fromEntries(new FormData(searchForm));
        window.lastAppliedParams = params;
        fetchAndRenderVenueList(params, 1);
      });
    }

    // initial load uses empty params
    fetchAndRenderVenueList({}, 1);
  } else {
    fetchAndRenderVenueList({}, 1);
  }

  if (sortSelect) {
    sortSelect.addEventListener("change", function () {
      window.lastSortBy = sortSelect.value; // Store current sort
      // re-fetch using last params (or current form values)
      const params = searchForm
        ? Object.fromEntries(new FormData(searchForm))
        : {};
      window.lastAppliedParams = params;
      fetchAndRenderVenueList(params, 1);
    });
  }
});
