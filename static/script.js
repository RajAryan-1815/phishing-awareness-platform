/* script.js – PhishGuard
   Minimal vanilla JS for UI interactions. No external libraries. */

// ── Mobile navigation toggle ─────────────────────────────────────────────
const hamburger = document.getElementById('hamburger');
const navLinks  = document.querySelector('.nav-links');

if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });

  // Close menu when any nav link is clicked
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => navLinks.classList.remove('open'));
  });
}

// ── Quiz: highlight selected option ─────────────────────────────────────
document.querySelectorAll('.quiz-option input[type="radio"]').forEach(radio => {
  radio.addEventListener('change', () => {
    // Remove highlight from all options in the same question group
    const name = radio.getAttribute('name');
    document.querySelectorAll(`input[name="${name}"]`).forEach(r => {
      r.closest('.quiz-option').style.background = '';
      r.closest('.quiz-option').style.borderColor = '';
    });
    // Highlight the selected option
    const option = radio.closest('.quiz-option');
    option.style.background    = 'rgba(56,139,253,0.1)';
    option.style.borderColor   = 'var(--clr-primary)';
  });
});

// ── Quiz: prevent double-submission ─────────────────────────────────────
const quizForm   = document.getElementById('quiz-form');
const submitBtn  = document.getElementById('submit-btn');

if (quizForm && submitBtn) {
  quizForm.addEventListener('submit', () => {
    submitBtn.textContent  = 'Submitting…';
    submitBtn.disabled     = true;
  });
}

// ── Smooth scroll for TOC links on the Learn page ─────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', e => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
