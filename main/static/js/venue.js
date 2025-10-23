// venue.js - consolidated
const staticBase = window.staticUrl || '/static/';

// Dummy dataset for local testing and filters
const DUMMY_VENUES = [
  {
    id: 'dummy-1',
    name: 'Futsal Arena Jakarta',
    category: 'FUTSAL',
    address: 'Jl. Sudirman No. 123, Jakarta Selatan, DKI Jakarta',
    location_url: 'https://maps.google.com',
    contact: '+628121111111',
    number_of_courts: 3,
    price_per_hour: 150000,
    images: [staticBase + 'img/no-image.png'],
    avg_rating: 4.5,
    rating_count: 10
  },
  {
    id: 'dummy-2',
    name: 'Shuttle Court Bandung',
    category: 'BADMINTON',
    address: 'Jl. Dago No. 67, Bandung, Jawa Barat',
    location_url: 'https://maps.google.com',
    contact: '+628122222222',
    number_of_courts: 8,
    price_per_hour: 80000,
    images: [staticBase + 'img/no-image.png'],
    avg_rating: 4.2,
    rating_count: 8
  },
  {
    id: 'dummy-3',
    name: 'Surabaya Basketball Complex',
    category: 'BASKET',
    address: 'Jl. Ahmad Yani No. 234, Surabaya, Jawa Timur',
    location_url: 'https://maps.google.com',
    contact: '+628133333333',
    number_of_courts: 2,
    price_per_hour: 200000,
    images: [staticBase + 'img/no-image.png'],
    avg_rating: 4.2,
    rating_count: 24
  }
];

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
    const detailHref = `/venue/${detailId}/`;

  cardWrap.innerHTML = `
      <div class="relative h-44 bg-neutral-50">
        <img src="${imgSrc}" alt="${v.name}" class="w-full h-full object-cover" />
        <div class="absolute top-3 left-3 bg-white/90 text-xs px-2 py-1 rounded-full font-medium">${v.category || ''}</div>
      </div>
      <div class="p-4">
        <h3 class="text-lg font-display font-semibold mb-1">${v.name}</h3>
        <div class="flex items-center gap-3 text-sm text-neutral-600 mb-2">
          <div class="flex items-center gap-1">
            <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.974a1 1 0 00.95.69h4.178c.969 0 1.371 1.24.588 1.81l-3.38 2.455a1 1 0 00-.364 1.118l1.287 3.974c.3.921-.755 1.688-1.54 1.118l-3.38-2.455a1 1 0 00-1.175 0l-3.38 2.455c-.784.57-1.839-.197-1.54-1.118l1.286-3.974a1 1 0 00-.364-1.118L2.046 9.4c-.783-.57-.38-1.81.588-1.81h4.178a1 1 0 00.95-.69l1.287-3.974z"/></svg>
            <span class="text-sm font-medium">${v.avg_rating || '-'} </span>
            <span class="text-neutral-500">(${v.rating_count || 0} ulasan)</span>
          </div>
        </div>
        <div class="text-sm text-neutral-600 mb-3"><svg class="inline w-4 h-4 mr-1 align-text-bottom text-neutral-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 10c0 5 4 9 9 9s9-4 9-9a9 9 0 10-18 0z"/></svg>${v.address || ''}</div>
        <div class="flex items-center justify-between">
          <div class="text-sm font-medium">Rp${(v.price_per_hour||v.price||0).toLocaleString()} / jam</div>
          <a href="${detailHref}" class="inline-block px-4 py-2 rounded-full text-white" style="background: linear-gradient(90deg,#3f07a3,#4E71FF);">Lihat Detail</a>
        </div>
      </div>
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
  const url = new URL('/backend/venues/', window.location.origin);
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
