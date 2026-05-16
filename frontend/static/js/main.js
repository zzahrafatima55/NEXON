// ── Navbar User Data ─────────────────────────────────────────
const userData = document.getElementById('currentUserData');
if (userData) {
  const user = JSON.parse(userData.textContent);
  const btn  = document.querySelector('.nav-avatar-btn');
  if (btn) {
    btn.innerHTML = user.avatar
      ? `<img src="${user.avatar}" class="nav-avatar-img" alt="">`
      : `<div class="nav-avatar-initial">${user.name[0].toUpperCase()}</div>`;
  }
  const nameEl  = document.getElementById('dropdownName');
  const emailEl = document.getElementById('dropdownEmail');
  if (nameEl)  nameEl.textContent  = user.name;
  if (emailEl) emailEl.textContent = user.email;
}

function toggleProfileDropdown() {
  document.getElementById('profileDropdown')?.classList.toggle('show');
}

document.addEventListener('click', e => {
  const wrap = document.querySelector('.nav-avatar-wrap');
  if (wrap && !wrap.contains(e.target)) {
    document.getElementById('profileDropdown')?.classList.remove('show');
  }
});


// ── Search ───────────────────────────────────────────────────
const searchInput   = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
let searchTimer;

if (searchInput) {
  searchInput.addEventListener('input', () => {
    clearTimeout(searchTimer);
    const q = searchInput.value.trim();
    if (!q) { searchResults.classList.remove('show'); return; }
    searchTimer = setTimeout(() => doSearch(q), 400);
  });

  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
      searchResults.classList.remove('show');
    }
  });
}

async function doSearch(q) {
  const res  = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
  const data = await res.json();

  if (!data.length) {
    searchResults.innerHTML = `<div style="padding:16px;color:var(--text-muted);font-size:13px;">No results found</div>`;
  } else {
    searchResults.innerHTML = data.map((m, i) => `
      <div class="search-result-item" data-index="${i}">
        ${m.poster
          ? `<img src="${m.poster}" alt="">`
          : `<div style="width:40px;height:56px;background:var(--surface2);border-radius:4px;display:flex;align-items:center;justify-content:center;">🎬</div>`
        }
        <div class="search-result-info">
          <h4>${m.title}</h4>
          <span>${m.year} &nbsp;★ ${m.rating}</span>
        </div>
      </div>
    `).join('');

    searchResults.querySelectorAll('.search-result-item').forEach((el, i) => {
      el.addEventListener('click', () => {
        openModal(data[i]);
        searchResults.classList.remove('show');
        if (searchInput) searchInput.value = '';
      });
    });
  }
  searchResults.classList.add('show');
}


// ── Grid Helpers ─────────────────────────────────────────────
function renderGrid(grid, movies) {
  grid.innerHTML = movies.map(m => `
    <div class="movie-card" data-movie='${JSON.stringify(m).replace(/'/g, "&#39;")}'>
      ${m.poster
        ? `<img class="movie-poster" src="${m.poster}" alt="${m.title}" loading="lazy">`
        : `<div class="movie-poster-placeholder">🎬</div>`
      }
      <div class="movie-overlay">
        <div class="overlay-title">${m.title}</div>
        <div class="overlay-overview">${m.overview || ''}</div>
        <div class="overlay-actions">
          <button class="btn-icon wl-btn">+ Watchlist</button>
          <button class="btn-icon wt-btn">✓ Watched</button>
        </div>
      </div>
      <div class="movie-info">
        <div class="movie-title">${m.title}</div>
        <div class="movie-meta">
          <span>${m.year}</span>
          <span class="movie-rating">★ ${m.rating}</span>
        </div>
      </div>
    </div>
  `).join('');

  grid.querySelectorAll('.movie-card').forEach(card => {
    const movie = JSON.parse(card.dataset.movie);
    card.addEventListener('click', () => openModal(movie));
    card.querySelector('.wl-btn')?.addEventListener('click', e => { e.stopPropagation(); addToWatchlist(movie); });
    card.querySelector('.wt-btn')?.addEventListener('click', e => { e.stopPropagation(); markWatched(movie); });
  });
}

function skeletons(n) {
  return Array(n).fill(0).map(() => `
    <div class="skeleton-card">
      <div class="skeleton-poster"></div>
      <div class="skeleton-info">
        <div class="skeleton-line"></div>
        <div class="skeleton-line short"></div>
      </div>
    </div>
  `).join('');
}


// ── Modal ─────────────────────────────────────────────────────
function openModal(movie) {
  const poster = movie.poster || '';
  window._modalMovie = movie;

  document.getElementById('modalContent').innerHTML = `
    ${poster ? `<img class="modal-poster" src="${poster}" alt="${movie.title}">` : ''}
    <div class="modal-body">
      <div class="modal-title">${movie.title}</div>
      <div class="modal-meta">
        ${movie.year || ''} ${movie.rating ? `· ★ ${movie.rating}` : ''}
      </div>
      <div class="modal-overview">${movie.overview || 'No description available.'}</div>
     <div class="modal-actions" style="display:flex;flex-direction:column;gap:8px;">
  <button class="btn-primary" id="modalTrailer" style="width:100%;font-size:15px;padding:14px;letter-spacing:1px;">▶ Watch Trailer</button>
  <div style="display:flex;gap:8px;">
    <button class="btn-outline" id="modalWatched" style="flex:1;">✓ Watched</button>
    <button class="btn-outline" id="modalWatchlist" style="flex:1;">+ Watchlist</button>
  </div>
</div>
    </div>
  `;

  document.getElementById('modalWatchlist').addEventListener('click', () => addToWatchlist(window._modalMovie));
  document.getElementById('modalWatched').addEventListener('click', () => markWatched(window._modalMovie));
document.getElementById('modalTrailer').addEventListener('click', () => {
  const tmdbId = movie.movie_id || movie.id;
  playTrailer(tmdbId);
});  document.getElementById('movieModal').classList.add('show');
}

function closeModal() {
  const modal = document.getElementById('movieModal');
  
  // find and nuke all iframes
  document.querySelectorAll('#modalContent iframe').forEach(f => {
    f.contentWindow.postMessage('{"event":"command","func":"stopVideo","args":""}', '*');
    f.src = 'about:blank';
    f.remove();
  });

  modal.classList.remove('show');
  
  setTimeout(() => {
    document.getElementById('modalContent').innerHTML = '';
  }, 50);
}

document.getElementById('movieModal')?.addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
});


// ── Trailer ───────────────────────────────────────────────────
async function playTrailer(movieId) {
  const res  = await fetch(`/api/trailer/${movieId}`);
  const data = await res.json();

  if (!data.url) {
    showToast('No trailer available for this movie.');
    return;
  }

  const url = data.url + '&enablejsapi=1';

  document.getElementById('modalContent').innerHTML = `
    <div style="width:100%;background:#000;border-radius:16px;overflow:hidden;">
      <iframe
        id="trailerFrame"
        src="${url}"
        width="100%"
        height="300"
        frameborder="0"
        allow="autoplay; fullscreen"
        allowfullscreen
        style="display:block;">
      </iframe>
      <div style="padding:16px 20px;display:flex;gap:10px;">
        <button class="btn-primary" id="trailerWatchlist" style="flex:1;">+ Watchlist</button>
        <button class="btn-outline" id="trailerWatched" style="flex:1;">✓ Watched</button>
      </div>
    </div>
  `;

  document.getElementById('trailerWatchlist')?.addEventListener('click', () => addToWatchlist(window._modalMovie));
  document.getElementById('trailerWatched')?.addEventListener('click', () => markWatched(window._modalMovie));
}

// ── Watchlist ─────────────────────────────────────────────────
async function addToWatchlist(movie) {
  const id = movie.id || movie.movie_id;
  await fetch('/api/watchlist/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      id:       id,
      title:    movie.title,
      poster:   movie.poster,
      rating:   movie.rating,
      year:     movie.year,
      overview: movie.overview || ''
    })
  });
  showToast(`🔖 Added "${movie.title}" to watchlist`);
  closeModal();
}


// ── History ───────────────────────────────────────────────────
async function markWatched(movie) {
  const id = movie.id || movie.movie_id;
  await fetch('/api/history/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      id:       id,
      title:    movie.title,
      poster:   movie.poster,
      rating:   movie.rating,
      overview: movie.overview || ''
    })
  });
  showToast(`✓ Marked "${movie.title}" as watched`);
  closeModal();
}


// ── Toast ─────────────────────────────────────────────────────
function showToast(message) {
  const container = document.getElementById('toastContainer');
  const toast     = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3200);
}


// ── Mobile Search ─────────────────────────────────────────────
const mobileBar   = document.getElementById('mobileSearchBar');
const mobileInput = document.getElementById('mobileSearchInput');
const searchIconEl = document.querySelector('.search-icon');

if (searchIconEl && mobileBar) {
  searchIconEl.addEventListener('click', () => {
    if (window.innerWidth <= 768) {
      mobileBar.classList.toggle('show');
      if (mobileBar.classList.contains('show')) mobileInput?.focus();
    }
  });

  mobileInput?.addEventListener('input', () => {
    const q = mobileInput.value.trim();
    if (!q) { searchResults?.classList.remove('show'); return; }
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => doSearch(q), 400);
  });
}