// Current venue ID from URL
const venueId = window.location.pathname.split('/').filter(Boolean).pop();

// If server injected `window.venueData`, use it. Otherwise fall back to dummy data below.
const serverVenue = window.venueData ? window.venueData : null;

// Dummy venue data (used only if server data is not present)
const dummyVenue = {
  id: venueId,
  name: "GOR Soemantri",
  description: "GOR Soemantri adalah salah satu venue olahraga terbaik di Jakarta Selatan. Dilengkapi dengan berbagai fasilitas modern dan lapangan berstandar internasional.",
  category: "Badminton",
  rating: 4.5,
  reviewCount: 128,
  location: "Jakarta Selatan",
  address: "Jl. HR Rasuna Said, Kuningan, Jakarta Selatan",
  contact: "+62 812-3456-7890",
  courts: 6,
  price: 150000,
  images: [
    `${window.staticUrl}images/dummy/venue1.jpg`,
    `${window.staticUrl}images/dummy/venue2.jpg`,
    `${window.staticUrl}images/dummy/venue3.jpg`,
    `${window.staticUrl}images/dummy/venue4.jpg`,
  ],
  facilities: [
    { name: "Parkir Luas", icon: "parking" },
    { name: "Toilet", icon: "toilet" },
    { name: "Ruang Ganti", icon: "changing-room" },
    { name: "Wifi", icon: "wifi" },
    { name: "Kantin", icon: "food" },
    { name: "Musholla", icon: "prayer" }
  ]
};

// Dummy reviews data (fallback)
const dummyReviews = [
  {
    id: 1,
    user: "John Doe",
    rating: 5,
    date: "2023-10-15",
    comment: "Lapangan bagus, fasilitas lengkap, pelayanan ramah. Recommended!",
    ratings: {
      cleanliness: 5,
      courtCondition: 5,
      communication: 5
    }
  },
  {
    id: 2,
    user: "Jane Smith",
    rating: 4,
    date: "2023-10-10",
    comment: "Overall bagus, cuma parkiran agak sempit kalau weekend.",
    ratings: {
      cleanliness: 4,
      courtCondition: 4,
      communication: 5
    }
  }
];

// Helper function to format currency
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('id-ID').format(amount);
};

// Helper function to create star rating display
const createStarRating = (rating) => {
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  const stars = [];

  for (let i = 0; i < 5; i++) {
    if (i < fullStars) {
      stars.push('<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.974a1 1 0 00.95.69h4.178c.969 0 1.371 1.24.588 1.81l-3.38 2.455a1 1 0 00-.364 1.118l1.287 3.974c.3.921-.755 1.688-1.54 1.118l-3.38-2.455a1 1 0 00-1.175 0l-3.38 2.455c-.784.57-1.839-.197-1.54-1.118l1.286-3.974a1 1 0 00-.364-1.118L2.046 9.4c-.783-.57-.38-1.81.588-1.81h4.178a1 1 0 00.95-.69l1.287-3.974z"/></svg>');
    } else if (i === fullStars && hasHalfStar) {
      stars.push('<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.974a1 1 0 00.95.69h4.178c.969 0 1.371 1.24.588 1.81l-3.38 2.455a1 1 0 00-.364 1.118l1.287 3.974c.3.921-.755 1.688-1.54 1.118l-3.38-2.455a1 1 0 00-1.175 0l-3.38 2.455c-.784.57-1.839-.197-1.54-1.118l1.286-3.974a1 1 0 00-.364-1.118L2.046 9.4c-.783-.57-.38-1.81.588-1.81h4.178a1 1 0 00.95-.69l1.287-3.974z" style="clip-path: inset(0 50% 0 0);"/></svg>');
    } else {
      stars.push('<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" style="color: #E5E7EB;"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.974a1 1 0 00.95.69h4.178c.969 0 1.371 1.24.588 1.81l-3.38 2.455a1 1 0 00-.364 1.118l1.287 3.974c.3.921-.755 1.688-1.54 1.118l-3.38-2.455a1 1 0 00-1.175 0l-3.38 2.455c-.784.57-1.839-.197-1.54-1.118l1.286-3.974a1 1 0 00-.364-1.118L2.046 9.4c-.783-.57-.38-1.81.588-1.81h4.178a1 1 0 00.95-.69l1.287-3.974z"/></svg>');
    }
  }

  return stars.join('');
};

// Initialize venue detail page
const initVenueDetail = () => {
  const data = serverVenue || dummyVenue;

  // Use server-provided reviews if available, otherwise fallback to dummyReviews
  const reviews = (serverVenue && serverVenue.reviews && serverVenue.reviews.length) ? serverVenue.reviews : dummyReviews;

  // Set venue details
  document.getElementById('venue-name').textContent = data.name || '';
  document.getElementById('venue-category').textContent = data.category || '';
  document.getElementById('venue-rating').textContent = (data.rating || 0).toFixed(1);
  document.getElementById('rating-count').textContent = data.reviewCount || reviews.length || 0;
  document.getElementById('venue-address').textContent = data.address || '';
  document.getElementById('venue-description').textContent = data.description || '';
  document.getElementById('venue-contact').textContent = data.contact || '';
  document.getElementById('venue-courts').textContent = data.courts || (data.courts_list ? data.courts_list.length : 0);
  document.getElementById('venue-price').textContent = formatCurrency(data.price || 0);

  // Setup image gallery
  const mainImage = document.getElementById('main-venue-image');
  const thumbsContainer = document.getElementById('venue-image-thumbs');
  
  const images = data.images && data.images.length ? data.images : [ `${window.staticUrl}images/dummy/venue1.jpg` ];
  mainImage.src = images[0];
  mainImage.alt = data.name || '';

  images.forEach((image, index) => {
    const thumb = document.createElement('div');
    thumb.className = 'aspect-w-4 aspect-h-3 rounded-xl overflow-hidden bg-neutral-100 cursor-pointer';
    thumb.innerHTML = `<img src="${image}" alt="${data.name} ${index + 1}" class="w-full h-full object-cover">`;
    thumb.onclick = () => {
      mainImage.src = image;
    };
    thumbsContainer.appendChild(thumb);
  });

  // Setup facilities
  const facilitiesContainer = document.getElementById('venue-facilities');
  const facilityList = data.facilities && data.facilities.length ? data.facilities : [];
  facilityList.forEach(facility => {
    const name = facility.name || facility;
    const facilityDiv = document.createElement('div');
    facilityDiv.className = 'flex items-center gap-2';
    facilityDiv.innerHTML = `
      <svg class="w-5 h-5 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7"/>
      </svg>
      <span>${name}</span>
    `;
    facilitiesContainer.appendChild(facilityDiv);
  });

  // Setup reviews section
  const avgRating = reviews.length ? (reviews.reduce((acc, review) => acc + (review.rating || 0), 0) / reviews.length) : 0;
  document.getElementById('avg-rating').textContent = avgRating.toFixed(1);
  document.getElementById('overall-stars').innerHTML = createStarRating(avgRating);
  document.getElementById('total-reviews').textContent = reviews.length;

  // Calculate average category ratings (fallback values if server doesn't provide)
  const categoryRatings = reviews.reduce((acc, review) => {
    acc.cleanliness += (review.ratings && review.ratings.cleanliness) ? review.ratings.cleanliness : 4;
    acc.courtCondition += (review.ratings && review.ratings.courtCondition) ? review.ratings.courtCondition : 4;
    acc.communication += (review.ratings && review.ratings.communication) ? review.ratings.communication : 4;
    return acc;
  }, { cleanliness: 0, courtCondition: 0, communication: 0 });

  const reviewCount = reviews.length || 1;
  document.getElementById('cleanliness-rating').style.width = `${(categoryRatings.cleanliness / reviewCount / 5) * 100}%`;
  document.getElementById('court-condition-rating').style.width = `${(categoryRatings.courtCondition / reviewCount / 5) * 100}%`;
  document.getElementById('communication-rating').style.width = `${(categoryRatings.communication / reviewCount / 5) * 100}%`;

  document.getElementById('cleanliness-score').textContent = (categoryRatings.cleanliness / reviewCount).toFixed(1);
  document.getElementById('court-condition-score').textContent = (categoryRatings.courtCondition / reviewCount).toFixed(1);
  document.getElementById('communication-score').textContent = (categoryRatings.communication / reviewCount).toFixed(1);

  // Render reviews
  const reviewsList = document.getElementById('review-list');
  reviews.forEach(review => {
    const reviewElement = document.createElement('div');
    reviewElement.className = 'bg-white rounded-2xl shadow-soft p-6';
    reviewElement.innerHTML = `
      <div class="flex items-center justify-between mb-3">
        <div>
          <div class="font-medium mb-1">${review.user || 'Pengguna'}</div>
          <div class="text-sm text-neutral-500">${review.date ? new Date(review.date).toLocaleDateString('id-ID', { year: 'numeric', month: 'long', day: 'numeric' }) : ''}</div>
        </div>
        <div class="flex text-yellow-400">
          ${createStarRating(review.rating || 0)}
        </div>
      </div>
      <p class="text-neutral-600">${review.comment || ''}</p>
    `;
    reviewsList.appendChild(reviewElement);
  });
};

// Handle review modal
const reviewModal = document.getElementById('review-modal');
const writeReviewBtn = document.getElementById('write-review');
const cancelReviewBtn = document.getElementById('cancel-review');
const ratingInput = document.getElementById('rating-input');
let selectedRating = 0;

if (writeReviewBtn) {
  writeReviewBtn.onclick = () => {
    reviewModal.classList.remove('hidden');
  };
}

if (cancelReviewBtn) {
  cancelReviewBtn.onclick = () => {
    reviewModal.classList.add('hidden');
    selectedRating = 0;
    updateRatingDisplay();
  };
}

const updateRatingDisplay = () => {
  const stars = ratingInput.querySelectorAll('button');
  stars.forEach((star, index) => {
    star.classList.toggle('text-yellow-400', index < selectedRating);
    star.classList.toggle('text-neutral-200', index >= selectedRating);
  });
};

if (ratingInput) {
  const stars = ratingInput.querySelectorAll('button');
  stars.forEach((star, index) => {
    star.onclick = () => {
      selectedRating = index + 1;
      updateRatingDisplay();
    };
  });
}

document.getElementById('review-form')?.addEventListener('submit', (e) => {
  e.preventDefault();
  const comment = e.target.querySelector('textarea').value;
  if (selectedRating === 0) {
    alert('Silakan pilih rating terlebih dahulu');
    return;
  }
  if (!comment.trim()) {
    alert('Silakan tulis ulasan terlebih dahulu');
    return;
  }
  // TODO: Submit review to backend
  console.log({ rating: selectedRating, comment });
  reviewModal.classList.add('hidden');
});

// Initialize calendar
const initCalendar = () => {
  const today = new Date();
  const month = today.getMonth();
  const year = today.getFullYear();

  // Get first day of month and total days
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  const calendarGrid = document.getElementById('calendar-grid');
  // Clear existing calendar
  calendarGrid.innerHTML = '';

  // Add empty cells for days before first of month
  for (let i = 0; i < firstDay; i++) {
    const emptyCell = document.createElement('div');
    emptyCell.className = 'aspect-square';
    calendarGrid.appendChild(emptyCell);
  }

  // Add days of month
  for (let day = 1; day <= daysInMonth; day++) {
    const cell = document.createElement('button');
    cell.className = 'aspect-square rounded-lg text-sm font-medium flex items-center justify-center';
    
    // Style current day
    if (day === today.getDate()) {
      cell.className += ' bg-gradient-to-r from-[#3f07a3] to-[#4E71FF] text-white';
    } else {
      cell.className += ' hover:bg-neutral-100';
    }
    
    cell.textContent = day;
    cell.onclick = () => selectDate(year, month, day);
    calendarGrid.appendChild(cell);
  }
};

// Handle date selection
const selectDate = (year, month, day) => {
  const date = new Date(year, month, day);
  console.log('Selected date:', date.toISOString().split('T')[0]);
  
  // Dummy time slots (replace with API data)
  const timeSlots = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00'];
  const slotsContainer = document.getElementById('time-slots');
  slotsContainer.innerHTML = '';

  timeSlots.forEach(time => {
    const available = Math.random() > 0.3; // Randomly set availability
    const slot = document.createElement('button');
    slot.className = `py-2 rounded-lg text-sm font-medium ${available ? 'hover:bg-neutral-100' : 'text-neutral-300 cursor-not-allowed'}`;
    slot.textContent = time;
    slot.disabled = !available;
    slot.onclick = () => selectTimeSlot(date, time);
    slotsContainer.appendChild(slot);
  });
};

// Handle time slot selection
const selectTimeSlot = (date, time) => {
  console.log('Selected time slot:', date.toISOString().split('T')[0], time);
  // TODO: Handle booking process
};

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
  initVenueDetail();
  initCalendar();
});