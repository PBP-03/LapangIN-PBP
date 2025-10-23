// venue_detail.js
// Fetch & render venue detail
function fetchVenueDetail(venueId) {
  // Try fetching detail by UUID endpoint first
  fetch(`/venue/${venueId}/`)
    .then(res => {
      if (res.status === 404) {
        // Fallback: the URL may be a name-based path (not a UUID). Query list by name.
        const decoded = decodeURIComponent(venueId);
        return fetch(`/venue/?name=${encodeURIComponent(decoded)}`)
          .then(r => r.json())
          .then(listJson => {
            const first = (listJson.data && listJson.data.length) ? listJson.data[0] : null;
            if (first) {
              renderVenueDetail(first);
              fetchVenueReviews(first.id);
            } else {
              // Nothing found
              console.warn('Venue not found via API by UUID or name:', venueId);
            }
          });
      }
      return res.json().then(json => {
        if (json && json.data) {
          renderVenueDetail(json.data);
          fetchVenueReviews(json.data.id);
        }
      });
    })
    .catch(err => {
      console.error('Error fetching venue detail:', err);
    });
}

function renderVenueDetail(v) {
  // Validate venue data
  if (!v) {
    console.error('No venue data provided');
    return;
  }

  console.log('Rendering venue detail:', v); // Debug log

  // Update venue name
  const nameEl = document.getElementById('venue-name');
  if (nameEl) nameEl.textContent = v.name || 'Unnamed Venue';

  // Update rating
  const ratingEl = document.getElementById('venue-rating');
  const ratingCountEl = document.getElementById('rating-count');
  if (ratingEl) ratingEl.textContent = v.avg_rating?.toFixed(1) || '-';
  if (ratingCountEl) ratingCountEl.textContent = v.rating_count || 0;

  // Update address/location (2 lines + button)
  const addressEl = document.getElementById('venue-address');
  if (addressEl) {
    const [street, city] = (v.address || '').split(',').map(s => s.trim());
    const locationUrl = v.location_url || `https://www.google.com/maps/search/${encodeURIComponent(v.address || v.name)}`;
    addressEl.innerHTML = `
      <div class="flex items-center justify-between w-full">
        <div class="flex flex-col">
          <div class="text-neutral-900">${street || ''}</div>
          <div class="text-neutral-600">${city || ''}</div>
        </div>
        <a href="${locationUrl}" target="_blank" class="inline-flex items-center gap-2 ml-auto px-3 py-1 rounded-lg border border-red-500 text-red-500 text-sm font-medium hover:bg-red-50 transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          Buka Peta
        </a>
      </div>
    `;
  }

  // Update description (full text with proper formatting)
  const descEl = document.getElementById('venue-description');
  if (descEl) {
    const desc = v.description || '';
    descEl.innerHTML = desc
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0)
      .map(line => `<p class="mb-2 text-neutral-600">${line}</p>`)
      .join('');
  }

  // Update contact
  const contactEl = document.getElementById('venue-contact');
  if (contactEl) contactEl.textContent = v.contact || '-';

  // Update courts count
  const courtsEl = document.getElementById('venue-courts');
  if (courtsEl) courtsEl.textContent = v.courts?.length || 0;

  // Update price
  const priceEl = document.getElementById('venue-price');
  if (priceEl && v.price_per_hour) priceEl.textContent = `Rp${v.price_per_hour.toLocaleString('id-ID')}`;

  // Update category badge
  const categoryEl = document.getElementById('venue-category');
  if (categoryEl) {
    categoryEl.innerHTML = `
      ${v.category_icon ? `<img src="${window.staticUrl}${v.category_icon}" class="w-4 h-4 mr-1 inline-block">` : ''}
      ${v.category || ''}
    `;
  }

  // Update gallery/images
  const mainImageEl = document.getElementById('main-venue-image');
  const thumbsEl = document.getElementById('venue-image-thumbs');
  if (mainImageEl && v.images && v.images.length > 0) {
    mainImageEl.src = v.images[0];
    mainImageEl.alt = v.name;
  }
  if (thumbsEl && v.images) {
    thumbsEl.innerHTML = v.images.slice(0,4).map(img => `
      <div class="rounded-2xl overflow-hidden h-[110px] bg-neutral-100">
        <img src="${img}" alt="" class="w-full h-full object-cover">
      </div>
    `).join('');
  }

  // Update facilities with proper icons and badges
  const facilitiesEl = document.getElementById('venue-facilities');
  if (facilitiesEl) {
    if (v.facilities && v.facilities.length > 0) {
      facilitiesEl.innerHTML = v.facilities.map(f => `
        <span class="px-3 py-1.5 rounded-full bg-neutral-100 text-neutral-800 text-sm font-medium inline-flex items-center gap-2">
          ${f.icon ? `
            <img src="${window.staticUrl}${f.icon}" alt="" class="w-4 h-4 flex-none">
          ` : `
            <svg class="w-4 h-4 text-neutral-400 flex-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7"/>
            </svg>
          `}
          <span>${f.name}</span>
        </span>
      `).join('');
    } else {
      facilitiesEl.innerHTML = `
        <span class="text-neutral-500">Tidak ada fasilitas tersedia</span>
      `;
    }
  }

  // Update court list
  const courtListEl = document.getElementById('court-list');
  if (courtListEl) {
    courtListEl.innerHTML = (v.courts || []).map(c => `
      <div class="flex items-center justify-between p-4 bg-white rounded-2xl shadow-soft">
        <div>
          <h4 class="font-semibold mb-1">${c.name}</h4>
          <div class="text-sm ${c.is_active ? 'text-green-600' : 'text-red-600'}">
            ${c.is_active ? 'Tersedia' : 'Tidak Aktif'}
          </div>
        </div>
        ${c.is_active ? `
          <button class="px-4 py-2 rounded-full text-white text-sm font-medium" style="background: linear-gradient(90deg,#3f07a3,#4E71FF);">
            Booking
          </button>
        ` : ''}
      </div>
    `).join('');
  }
}

function renderStars(rating) {
  return Array.from({length: 5}, (_, i) => `
    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.974a1 1 0 00.95.69h4.178c.969 0 1.371 1.24.588 1.81l-3.38 2.455a1 1 0 00-.364 1.118l1.287 3.974c.3.921-.755 1.688-1.54 1.118l-3.38-2.455a1 1 0 00-1.175 0l-3.38 2.455c-.784.57-1.839-.197-1.54-1.118l1.286-3.974a1 1 0 00-.364-1.118L2.046 9.4c-.783-.57-.38-1.81.588-1.81h4.178a1 1 0 00.95-.69l1.287-3.974z" fill="${i < Math.round(rating) ? 'currentColor' : 'none'}" stroke="${i < Math.round(rating) ? 'none' : 'currentColor'}"/>
    </svg>
  `).join('');
}

// Fetch & render reviews
function fetchVenueReviews(venueId) {
  fetch(`/venue/${venueId}/reviews/`)
    .then(res => res.json())
    .then(json => renderVenueReviews(json.data));
}

function renderVenueReviews(reviews) {
  // Update review list
  const listEl = document.getElementById('review-list');
  if (!listEl) return;

  listEl.innerHTML = (reviews || []).map(r => `
    <div class="p-4 bg-white rounded-2xl shadow-soft">
      <div class="flex items-start justify-between mb-3">
        <div>
          <div class="font-semibold mb-1">${r.user}</div>
          <div class="flex gap-1 text-sm text-yellow-400">
            ${Array.from({length: 5}, (_, i) => `
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.974a1 1 0 00.95.69h4.178c.969 0 1.371 1.24.588 1.81l-3.38 2.455a1 1 0 00-.364 1.118l1.287 3.974c.3.921-.755 1.688-1.54 1.118l-3.38-2.455a1 1 0 00-1.175 0l-3.38 2.455c-.784.57-1.839-.197-1.54-1.118l1.286-3.974a1 1 0 00-.364-1.118L2.046 9.4c-.783-.57-.38-1.81.588-1.81h4.178a1 1 0 00.95-.69l1.287-3.974z" fill="${i < r.rating ? 'currentColor' : 'none'}" stroke="${i < r.rating ? 'none' : 'currentColor'}"/>
              </svg>
            `).join('')}
          </div>
        </div>
        <div class="text-sm text-neutral-500">
          ${new Date(r.created_at).toLocaleDateString('id-ID', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}
        </div>
      </div>
      <p class="text-neutral-600">${r.comment || ''}</p>
    </div>
  `).join('');

  // Update review stats
  const totalEl = document.getElementById('total-reviews');
  const avgEl = document.getElementById('avg-rating');
  const starsEl = document.getElementById('overall-stars');
  
  if (reviews && reviews.length) {
    const avgRating = reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length;
    if (totalEl) totalEl.textContent = reviews.length;
    if (avgEl) avgEl.textContent = avgRating.toFixed(1);
    if (starsEl) {
      starsEl.innerHTML = Array.from({length: 5}, (_, i) => `
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.974a1 1 0 00.95.69h4.178c.969 0 1.371 1.24.588 1.81l-3.38 2.455a1 1 0 00-.364 1.118l1.287 3.974c.3.921-.755 1.688-1.54 1.118l-3.38-2.455a1 1 0 00-1.175 0l-3.38 2.455c-.784.57-1.839-.197-1.54-1.118l1.286-3.974a1 1 0 00-.364-1.118L2.046 9.4c-.783-.57-.38-1.81.588-1.81h4.178a1 1 0 00.95-.69l1.287-3.974z" fill="${i < Math.round(avgRating) ? 'currentColor' : 'none'}" stroke="${i < Math.round(avgRating) ? 'none' : 'currentColor'}"/>
        </svg>
      `).join('');
    }
    
    // Update category ratings
    const ratings = {
      cleanliness: reviews.reduce((sum, r) => sum + (r.cleanliness || 0), 0) / reviews.length,
      courtCondition: reviews.reduce((sum, r) => sum + (r.court_condition || 0), 0) / reviews.length,
      communication: reviews.reduce((sum, r) => sum + (r.communication || 0), 0) / reviews.length
    };

    // Update score displays
    const cleanScore = document.getElementById('cleanliness-score');
    const courtScore = document.getElementById('court-condition-score');
    const commScore = document.getElementById('communication-score');
    if (cleanScore) cleanScore.textContent = ratings.cleanliness.toFixed(1);
    if (courtScore) courtScore.textContent = ratings.courtCondition.toFixed(1);
    if (commScore) commScore.textContent = ratings.communication.toFixed(1);

    // Update rating bars
    const cleanBar = document.getElementById('cleanliness-rating');
    const courtBar = document.getElementById('court-condition-rating');
    const commBar = document.getElementById('communication-rating');
    if (cleanBar) cleanBar.style.width = `${(ratings.cleanliness / 5) * 100}%`;
    if (courtBar) courtBar.style.width = `${(ratings.courtCondition / 5) * 100}%`;
    if (commBar) commBar.style.width = `${(ratings.communication / 5) * 100}%`;
  }
}

// Review form (only for logged in user)
function renderReviewForm(venueId, user) {
  const container = document.getElementById('venue-review-form-container');
  if (!container) return;
  container.innerHTML = `
    <form id="venue-review-form" class="mb-3">
      <div class="mb-2">
        <label for="review-rating" class="form-label">Rating</label>
        <select id="review-rating" name="rating" class="form-select" required>
          <option value="">Pilih rating</option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
          <option value="4">4</option>
          <option value="5">5</option>
        </select>
      </div>
      <div class="mb-2">
        <label for="review-comment" class="form-label">Ulasan</label>
        <textarea id="review-comment" name="comment" class="form-control" rows="2" required></textarea>
      </div>
      <button type="submit" class="btn btn-success">Kirim Review</button>
    </form>
  `;
  const form = document.getElementById('venue-review-form');
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form));
    // TODO: Tambahkan court_id dan booking_date sesuai booking user
    fetch(`/backend/venues/${venueId}/reviews/`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(json => {
      if (json.status === 'ok') {
        fetchVenueReviews(venueId);
        form.reset();
      } else {
        alert(json.message || 'Gagal kirim review');
      }
    });
  });
}

// Cek user login dan render form
function checkUserLogin(venueId) {
  fetch('/backend/user-status/')
    .then(res => res.json())
    .then(json => {
      if (json.authenticated) {
        renderReviewForm(venueId, json.user);
      }
    });
}

// Inisialisasi halaman detail
// Handle venue data initialization
function initVenueDetail() {
  console.log('Initializing venue detail page...');
  
  // Debug logs
  console.log('window.staticUrl:', window.staticUrl);
  console.log('window.venueData:', window.venueData);

  // Ensure we have staticUrl
  if (!window.staticUrl) {
    console.error('staticUrl not found! Please check template configuration.');
    return;
  }

  try {
    // Check for server-provided venue data
    if (window.venueData) {
      console.log('Found server-provided venue data:', window.venueData);
      renderVenueDetail(window.venueData);
      if (window.venueData.id) {
        fetchVenueReviews(window.venueData.id);
        checkUserLogin(window.venueData.id);
      }
    } else {
      // Fallback to API fetch
      console.log('No server data, fetching from API...');
      const venueId = window.location.pathname.split('/').filter(Boolean).pop();
      if (venueId) {
        fetchVenueDetail(venueId);
        checkUserLogin(venueId);
      } else {
        console.error('No venue ID found in URL!');
      }
    }
  } catch (error) {
    console.error('Error initializing venue detail:', error);
  }
}

// Call initialization when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initVenueDetail);
} else {
  initVenueDetail();
}
