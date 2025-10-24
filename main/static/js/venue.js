// venue.js - consolidated
const staticBase = window.staticUrl || '/static/';

function renderVenueList(venues) {
  const container = document.getElementById('venue-list');
  const countEl = document.getElementById('venue-count-number');
  let list = venues;
  
    // If no venues provided, try dummy data
  if (!list) {
    list = DUMMY_VENUES;
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
    container.innerHTML = '<div class="col-span-full text-center py-12 text-neutral-600">Tidak ada venue yang sesuai dengan pencarian.</div>';
    if (countEl) countEl.textContent = '0';
    return;
  }

  if (countEl) countEl.textContent = list.length;
  container.innerHTML = '';
  list.forEach(v => {
    const imgSrc = (v.images && v.images.length) ? v.images[0] : (staticBase + 'img/no-image.png');
    const cardWrap = document.createElement('div');
    cardWrap.className = 'rounded-2xl bg-white shadow-soft overflow-hidden';
    // Prefer using the venue's UUID-like id when available (safe and unambiguous).
    // Otherwise fall back to the URL-encoded venue name (for dummy/test data).
    let detailId = '';
    if (v.id && typeof v.id === 'string' && v.id.indexOf('-') !== -1 && v.id.length > 20) {
      // Probably a UUID
      detailId = v.id;
    } else {
      detailId = encodeURIComponent(v.name || v.id || '');
    }
    const detailHref = `/lapangan/${detailId}/`;

  cardWrap.innerHTML = `
      <a href="${detailHref}" class="block hover:shadow-medium transition-shadow">
        <div class="relative h-48 bg-neutral-50">
          <img src="${imgSrc}" alt="${v.name}" class="w-full h-full object-cover" />
          ${v.category ? `<div class="absolute top-3 left-3 bg-white/95 backdrop-blur-sm text-xs px-3 py-1.5 rounded-full font-semibold text-neutral-700 shadow-soft">${v.category}</div>` : ''}
        </div>
        <div class="p-5">
          <h3 class="text-lg font-display font-semibold mb-2 text-neutral-900 line-clamp-1">${v.name}</h3>
          
          <!-- Rating -->
          <div class="flex items-center gap-1 mb-3">
            <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.974a1 1 0 00.95.69h4.178c.969 0 1.371 1.24.588 1.81l-3.38 2.455a1 1 0 00-.364 1.118l1.287 3.974c.3.921-.755 1.688-1.54 1.118l-3.38-2.455a1 1 0 00-1.175 0l-3.38 2.455c-.784.57-1.839-.197-1.54-1.118l1.286-3.974a1 1 0 00-.364-1.118l-3.38-2.455c-.783-.57-.38-1.81.588-1.81h4.178a1 1 0 00.95-.69l1.287-3.974z"/>
            </svg>
            <span class="text-sm font-semibold text-neutral-900">${(v.avg_rating || 0).toFixed(1)}</span>
            <span class="text-sm text-neutral-500">(${v.rating_count || 0} reviews)</span>
          </div>
          
          <!-- Address -->
          <div class="flex items-start gap-2 text-sm text-neutral-600 mb-4">
            <svg class="w-4 h-4 mt-0.5 flex-shrink-0 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            <span class="line-clamp-2">${v.address || 'Alamat tidak tersedia'}</span>
          </div>
          
          <!-- Price and Action -->
          <div class="flex items-center justify-between pt-3 border-t border-neutral-100">
            <div>
              <div class="text-xs text-neutral-500 mb-0.5">Mulai dari</div>
              <div class="text-lg font-bold text-primary-600">Rp ${(v.price_per_hour||v.price||0).toLocaleString('id-ID')}</div>
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
  });
}

// expose render function globally
window._renderVenueList = renderVenueList;

function sortVenues(venues, sortBy) {
  if (!venues) return venues;
  const list = venues.slice(); // Create copy for sorting

  if (sortBy === 'price_low') {
    return list.sort((a,b) => {
      const priceA = Number(a.price_per_hour || 0);
      const priceB = Number(b.price_per_hour || 0);
      return priceA - priceB;
    });
  }
  if (sortBy === 'price_high') {
    return list.sort((a,b) => {
      const priceA = Number(a.price_per_hour || 0);
      const priceB = Number(b.price_per_hour || 0);
      return priceB - priceA;
    });
  }
  if (sortBy === 'rating') {
    return list.sort((a,b) => {
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
  return venues.filter(v => {
    // name
    if (params.name && params.name.trim() !== '') {
      if (!v.name || !v.name.toLowerCase().includes(params.name.trim().toLowerCase())) return false;
    }
    // category exact match (case-insensitive)
    if (params.category && params.category !== '') {
      // Exact match case-insensitive (both should be uppercase per seed data)
      const searchCat = params.category.trim().toUpperCase();
      const venueCat = (v.category || '').toUpperCase();
      if (venueCat !== searchCat) return false;
    }
    // location (address contains)
    if (params.location && params.location.trim() !== '') {
      if (!v.address || !v.address.toLowerCase().includes(params.location.trim().toLowerCase())) return false;
    }
    // price range
    const minp = (params.min_price !== undefined && params.min_price !== '') ? Number(params.min_price) : null;
    const maxp = (params.max_price !== undefined && params.max_price !== '') ? Number(params.max_price) : null;
    const price = Number(v.price_per_hour || v.price || 0);
    if (minp !== null && !isNaN(minp) && price < minp) return false;
    if (maxp !== null && !isNaN(maxp) && price > maxp) return false;
    // min rating (treat as threshold)
    const minr = (params.min_rating !== undefined && params.min_rating !== '') ? Number(params.min_rating) : null;
    const rating = Number(v.avg_rating || 0);
    if (minr !== null && !isNaN(minr) && rating < minr) return false;
    return true;
  });
}

function fetchAndRenderVenueList(params = {}) {
  // params is an object of form values
  const url = new URL('/api/venues/', window.location.origin);
  Object.keys(params).forEach(k => {
    if (params[k]) url.searchParams.append(k, params[k]);
  });
  fetch(url)
    .then(res => res.json())
    .then(json => {
      let venues = json.data;
      // If API returns empty, prefer server snapshot injected into the page
      if ((!venues || venues.length === 0) && Array.isArray(window.venuesData) && window.venuesData.length > 0) {
        venues = window.venuesData;
      }
      // If still empty, fallback to dummy dataset
      if (!venues || venues.length === 0) {
        venues = applyFilters(DUMMY_VENUES, params);
      } else {
        // apply rating filter on API or server data too if client requested
        venues = applyFilters(venues, params);
      }

      // Ensure we prefer UUID-style ids from server data (they're strings)
      venues = venues.map(v => {
        // if the server snapshot uses string ids (UUID), keep them; otherwise
        // prefer to keep existing id (dummy) which will be encoded as name-based url
        if (v.id && typeof v.id === 'string') return v;
        return v;
      });

      const sortSelect = document.getElementById('venue-sort');
      const sortBy = sortSelect ? sortSelect.value : '';
      venues = sortVenues(venues, sortBy);
      renderVenueList(venues);
    })
    .catch(err => {
      // On error, prefer server-injected snapshot if present, otherwise dummy
      const venues = (Array.isArray(window.venuesData) && window.venuesData.length > 0)
        ? applyFilters(window.venuesData, params)
        : applyFilters(DUMMY_VENUES, params);
      renderVenueList(venues);
    });
}

// bootstrap: wire up form and sort
document.addEventListener('DOMContentLoaded', function() {
  const searchForm = document.getElementById('venue-search-form');
  const sortSelect = document.getElementById('venue-sort');
  let lastParams = {};
  // If the server injected a snapshot of venues, render it immediately so
  // links point to real IDs (UUIDs) instead of client-only dummy ids.
  if (Array.isArray(window.venuesData) && window.venuesData.length > 0) {
    // Apply any initial filters (none) and render
    renderVenueList(window.venuesData);
  }
  if (searchForm) {
    searchForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const params = Object.fromEntries(new FormData(searchForm));
      window.lastAppliedParams = params; // Store for re-use
      fetchAndRenderVenueList(params);
    });
    
    // Update search as you type
    searchForm.querySelectorAll('input[type="text"], input[type="number"]').forEach(input => {
      input.addEventListener('input', function() {
        const params = Object.fromEntries(new FormData(searchForm));
        window.lastAppliedParams = params;
        fetchAndRenderVenueList(params);
      });
    });
    
    // Update on category change
    const categorySelect = searchForm.querySelector('select[name="category"]');
    if (categorySelect) {
      categorySelect.addEventListener('change', function() {
        const params = Object.fromEntries(new FormData(searchForm));
        window.lastAppliedParams = params;
        fetchAndRenderVenueList(params);
      });
    }
    
    // initial load uses empty params
    fetchAndRenderVenueList({});
  } else {
    fetchAndRenderVenueList({});
  }
  
  if (sortSelect) {
    sortSelect.addEventListener('change', function() {
      window.lastSortBy = sortSelect.value; // Store current sort
      // re-fetch using last params (or current form values)
      const params = searchForm ? Object.fromEntries(new FormData(searchForm)) : {};
      window.lastAppliedParams = params;
      fetchAndRenderVenueList(params);
    });
  }
});
