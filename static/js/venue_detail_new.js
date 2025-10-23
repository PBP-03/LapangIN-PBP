// Current venue ID from URL
const venueId = window.location.pathname.split('/').filter(Boolean).pop();

// Function to get CSRF token
const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

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

// Load venue data using AJAX
const loadVenueData = async () => {
    try {
        console.log('Loading venue data for ID:', venueId);
        const response = await fetch(`/backend/public/venues/${venueId}/`);
        console.log('Response:', response);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const { status, data } = await response.json();
        console.log('Response data:', { status, data });
        
        if (status !== 'ok' || !data) {
            throw new Error('Invalid data received from server');
        }
        
        // Update venue details
        document.getElementById('venue-name').textContent = data.name;
        document.getElementById('venue-category').textContent = data.category;
        document.getElementById('venue-rating').textContent = data.avg_rating.toFixed(1);
        document.getElementById('rating-count').textContent = data.rating_count;
        document.getElementById('venue-address').textContent = data.address;
        document.getElementById('venue-description').textContent = data.description;
        document.getElementById('venue-contact').textContent = data.contact;
        document.getElementById('venue-courts').textContent = data.courts.length;
        document.getElementById('venue-price').textContent = formatCurrency(data.price_per_hour);

        // Update image gallery
        const mainImage = document.getElementById('main-venue-image');
        const thumbsContainer = document.getElementById('venue-image-thumbs');
        
        if (data.images && data.images.length > 0) {
            mainImage.src = data.images[0];
            mainImage.alt = data.name;

            thumbsContainer.innerHTML = '';
            data.images.forEach((image, index) => {
                const thumb = document.createElement('div');
                thumb.className = 'aspect-w-4 aspect-h-3 rounded-xl overflow-hidden bg-neutral-100 cursor-pointer';
                thumb.innerHTML = `<img src="${image}" alt="${data.name} ${index + 1}" class="w-full h-full object-cover">`;
                thumb.onclick = () => {
                    mainImage.src = image;
                };
                thumbsContainer.appendChild(thumb);
            });
        }

        // Update facilities
        const facilitiesContainer = document.getElementById('venue-facilities');
        facilitiesContainer.innerHTML = '';
        if (data.facilities && data.facilities.length > 0) {
            data.facilities.forEach(facility => {
                const facilityDiv = document.createElement('div');
                facilityDiv.className = 'flex items-center gap-2';
                facilityDiv.innerHTML = `
                    <svg class="w-5 h-5 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7"/>
                    </svg>
                    <span>${facility.name}</span>
                `;
                facilitiesContainer.appendChild(facilityDiv);
            });
        }

        // Update courts list
        const courtsList = document.getElementById('courts-list');
        courtsList.innerHTML = '';
        if (data.courts && data.courts.length > 0) {
            data.courts.forEach(court => {
                const courtElement = document.createElement('div');
                courtElement.className = 'flex items-center justify-between p-3 rounded-lg border border-neutral-200';
                courtElement.innerHTML = `
                    <div>
                        <div class="font-medium">${court.name}</div>
                        <div class="text-sm text-neutral-500">${court.is_active ? 'Tersedia' : 'Tidak Tersedia'}</div>
                    </div>
                    <button 
                        class="px-4 py-2 rounded-lg ${court.is_active ? 'bg-gradient-to-r from-[#3f07a3] to-[#4E71FF] text-white' : 'bg-neutral-100 text-neutral-400 cursor-not-allowed'}"
                        ${!court.is_active ? 'disabled' : ''}
                        onclick="selectCourt('${court.id}', '${court.name}')"
                    >
                        Pilih
                    </button>
                `;
                courtsList.appendChild(courtElement);
            });
        }

        // Update reviews
        if (data.reviews && data.reviews.length > 0) {
            document.getElementById('avg-rating').textContent = data.avg_rating.toFixed(1);
            document.getElementById('overall-stars').innerHTML = createStarRating(data.avg_rating);
            document.getElementById('total-reviews').textContent = data.reviews.length;

            const reviewsList = document.getElementById('review-list');
            reviewsList.innerHTML = '';
            data.reviews.forEach(review => {
                const reviewElement = document.createElement('div');
                reviewElement.className = 'bg-white rounded-2xl shadow-soft p-6';
                reviewElement.innerHTML = `
                    <div class="flex items-center justify-between mb-3">
                        <div>
                            <div class="font-medium mb-1">${review.user}</div>
                            <div class="text-sm text-neutral-500">${new Date(review.created_at).toLocaleDateString('id-ID', { year: 'numeric', month: 'long', day: 'numeric' })}</div>
                        </div>
                        <div class="flex text-yellow-400">
                            ${createStarRating(review.rating)}
                        </div>
                    </div>
                    <p class="text-neutral-600">${review.comment}</p>
                `;
                reviewsList.appendChild(reviewElement);
            });
        }

        // Initialize calendar for date selection
        initCalendar();
    } catch (error) {
        console.error('Error loading venue data:', error);
    }
};

// Handle court selection
let selectedCourtId = null;
let selectedCourtName = null;

const selectCourt = (courtId, courtName) => {
    selectedCourtId = courtId;
    selectedCourtName = courtName;
    
    // Highlight selected court
    document.querySelectorAll('#courts-list button').forEach(btn => {
        if (btn.parentElement.querySelector('.font-medium').textContent === courtName) {
            btn.textContent = 'Dipilih';
            btn.classList.add('bg-green-500');
        } else {
            btn.textContent = 'Pilih';
            btn.classList.remove('bg-green-500');
        }
    });

    // If date is already selected, load time slots
    if (selectedDate) {
        loadTimeSlots(courtId, selectedDate);
    }
    
    // Update book button visibility
    updateBookButton();
};

// Initialize calendar
let selectedDate = null;

const initCalendar = () => {
    const today = new Date();
    const month = today.getMonth();
    const year = today.getFullYear();

    // Get first day of month and total days
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    const calendarGrid = document.getElementById('calendar-grid');
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
        const date = new Date(year, month, day);
        const isToday = day === today.getDate() && month === today.getMonth() && year === today.getFullYear();
        const isPast = date < today;
        
        cell.className = `aspect-square rounded-lg text-sm font-medium flex items-center justify-center ${
            isPast ? 'text-neutral-300 cursor-not-allowed' :
            isToday ? 'bg-gradient-to-r from-[#3f07a3] to-[#4E71FF] text-white' :
            'hover:bg-neutral-100'
        }`;
        
        cell.textContent = day;
        if (!isPast) {
            cell.onclick = () => selectDate(year, month, day);
        }
        calendarGrid.appendChild(cell);
    }
};

// Handle date selection
const selectDate = async (year, month, day) => {
    const date = new Date(year, month, day);
    selectedDate = date.toISOString().split('T')[0];
    
    // Highlight selected date
    document.querySelectorAll('#calendar-grid button').forEach(btn => {
        if (btn.textContent === String(day)) {
            btn.classList.add('bg-gradient-to-r', 'from-[#3f07a3]', 'to-[#4E71FF]', 'text-white');
        } else {
            btn.classList.remove('bg-gradient-to-r', 'from-[#3f07a3]', 'to-[#4E71FF]', 'text-white');
        }
    });

    // If court is already selected, load time slots
    if (selectedCourtId) {
        await loadTimeSlots(selectedCourtId, selectedDate);
    }
    
    // Update book button visibility
    updateBookButton();
};

// Load time slots using AJAX
const loadTimeSlots = async (courtId, date) => {
    try {
        const response = await fetch(`/backend/courts/${courtId}/sessions/?date=${date}`);
        if (!response.ok) throw new Error('Failed to fetch time slots');
        const { sessions } = await response.json();
        
        const slotsContainer = document.getElementById('time-slots');
        slotsContainer.innerHTML = '';

        sessions.forEach(session => {
            const slot = document.createElement('button');
            slot.className = `py-2 rounded-lg text-sm font-medium ${
                session.is_booked ? 'text-neutral-300 cursor-not-allowed' : 'hover:bg-neutral-100'
            }`;
            slot.textContent = `${session.start_time} - ${session.end_time}`;
            slot.disabled = session.is_booked;
            
            if (!session.is_booked) {
                slot.onclick = () => selectTimeSlot(session.id, `${session.start_time} - ${session.end_time}`);
            }
            
            slotsContainer.appendChild(slot);
        });
    } catch (error) {
        console.error('Error loading time slots:', error);
    }
};

// Handle time slot selection
let selectedTimeSlot = null;

const selectTimeSlot = (sessionId, timeRange) => {
    selectedTimeSlot = { id: sessionId, timeRange };
    
    // Highlight selected time slot
    document.querySelectorAll('#time-slots button').forEach(btn => {
        if (btn.textContent === timeRange) {
            btn.classList.add('bg-gradient-to-r', 'from-[#3f07a3]', 'to-[#4E71FF]', 'text-white');
        } else {
            btn.classList.remove('bg-gradient-to-r', 'from-[#3f07a3]', 'to-[#4E71FF]', 'text-white');
        }
    });

    // Update book button visibility
    updateBookButton();
};

// Update book button visibility
const updateBookButton = () => {
    const bookButton = document.getElementById('book-button');
    if (selectedCourtId && selectedDate && selectedTimeSlot) {
        bookButton.classList.remove('hidden');
        bookButton.onclick = handleBooking;
    } else {
        bookButton.classList.add('hidden');
    }
};

// Handle booking submission
const handleBooking = () => {
    // Redirect to login if not authenticated
    if (!window.isAuthenticated) {
        window.location.href = '/login?next=' + window.location.pathname;
        return;
    }
    
    // TODO: Implement booking submission
    console.log('Booking details:', {
        courtId: selectedCourtId,
        courtName: selectedCourtName,
        date: selectedDate,
        sessionId: selectedTimeSlot.id,
        timeRange: selectedTimeSlot.timeRange
    });
};

// Handle reviews
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

// Handle review form submission
document.getElementById('review-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!window.isAuthenticated) {
        window.location.href = '/login?next=' + window.location.pathname;
        return;
    }

    const comment = e.target.querySelector('textarea').value;
    if (selectedRating === 0) {
        alert('Silakan pilih rating terlebih dahulu');
        return;
    }
    if (!comment.trim()) {
        alert('Silakan tulis ulasan terlebih dahulu');
        return;
    }

    try {
        const response = await fetch(`/backend/venues/${venueId}/reviews/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                rating: selectedRating,
                comment: comment.trim()
            })
        });

        if (!response.ok) throw new Error('Failed to submit review');
        
        // Close modal and reload venue data to show new review
        reviewModal.classList.add('hidden');
        loadVenueData();
    } catch (error) {
        console.error('Error submitting review:', error);
        alert('Gagal mengirim ulasan. Silakan coba lagi.');
    }
});

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded, initializing venue detail...');
    loadVenueData();
});