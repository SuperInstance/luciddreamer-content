// LucidDreamer.ai — Ambient audio + player logic

const AMBIENT_URL = '/audio/ambient-bar.mp3';
let ambientAudio = null;
let ambientOn = false;

function toggleAmbient() {
  const btn = document.getElementById('ambient-toggle');
  if (!ambientAudio) {
    ambientAudio = new Audio(AMBIENT_URL);
    ambientAudio.loop = true;
    ambientAudio.volume = 0.15;
  }
  if (ambientOn) {
    ambientAudio.pause();
    btn.classList.remove('playing');
    btn.innerHTML = '🔇';
    ambientOn = false;
  } else {
    ambientAudio.play().catch(() => {});
    btn.classList.add('playing');
    btn.innerHTML = '🔊';
    ambientOn = true;
  }
}

// Episode player
let currentAudio = null;
let currentCoaster = null;

function playEpisode(epNum, audioUrl, title, character, coasterEl) {
  // Pause ambient if playing
  if (ambientOn && ambientAudio) {
    ambientAudio.volume = 0.05;
  }

  // Stop current
  if (currentAudio) {
    currentAudio.pause();
    if (currentCoaster) currentCoaster.classList.remove('playing');
  }

  // If clicking the same one, just pause
  if (currentCoaster === coasterEl) {
    currentAudio = null;
    currentCoaster = null;
    hidePlayerBar();
    if (ambientOn && ambientAudio) ambientAudio.volume = 0.15;
    return;
  }

  currentAudio = new Audio(audioUrl);
  currentAudio.play().catch(() => {
    // If audio doesn't exist yet, show a message
    alert('This episode is still being poured. Check back soon.');
    return;
  });

  currentCoaster = coasterEl;
  coasterEl.classList.add('playing');

  // Show player bar
  const bar = document.getElementById('player-bar');
  document.getElementById('player-title').textContent = `Ep ${epNum}: ${title}`;
  document.getElementById('player-character').textContent = character;
  bar.classList.add('active');

  currentAudio.addEventListener('ended', () => {
    coasterEl.classList.remove('playing');
    hidePlayerBar();
    currentAudio = null;
    currentCoaster = null;
    if (ambientOn && ambientAudio) ambientAudio.volume = 0.15;
  });

  currentAudio.addEventListener('timeupdate', () => {
    const pct = (currentAudio.currentTime / currentAudio.duration) * 100;
    const progress = document.getElementById('player-progress');
    if (progress) progress.style.width = pct + '%';
    const timeEl = document.getElementById('player-time');
    if (timeEl && currentAudio.duration) {
      timeEl.textContent = formatTime(currentAudio.currentTime) + ' / ' + formatTime(currentAudio.duration);
    }
  });

  currentAudio.addEventListener('error', () => {
    coasterEl.classList.remove('playing');
    hidePlayerBar();
    currentAudio = null;
    currentCoaster = null;
    if (ambientOn && ambientAudio) ambientAudio.volume = 0.15;
  });
}

function hidePlayerBar() {
  const bar = document.getElementById('player-bar');
  if (bar) bar.classList.remove('active');
}

function formatTime(s) {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return m + ':' + (sec < 10 ? '0' : '') + sec;
}

function stopPlayback() {
  if (currentAudio) {
    currentAudio.pause();
    if (currentCoaster) currentCoaster.classList.remove('playing');
    currentAudio = null;
    currentCoaster = null;
  }
  hidePlayerBar();
  if (ambientOn && ambientAudio) ambientAudio.volume = 0.15;
}

// Mobile nav toggle
function toggleNav() {
  const links = document.querySelector('.nav-links');
  links.classList.toggle('mobile-open');
}
