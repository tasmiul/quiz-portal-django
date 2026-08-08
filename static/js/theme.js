(function () {
  'use strict';

  var KEY = 'quizora-theme';
  var root = document.documentElement;
  var btn = document.getElementById('theme-toggle');
  if (!btn) return;

  function current() {
    var saved = null;
    try {
      saved = localStorage.getItem(KEY);
    } catch (e) { /* ignore */ }
    return saved === 'light' || saved === 'dark' ? saved : 'dark';
  }

  function apply(theme) {
    root.setAttribute('data-theme', theme);
    try {
      localStorage.setItem(KEY, theme);
    } catch (e) { /* ignore */ }
    var sun = btn.querySelector('.icon-sun');
    var moon = btn.querySelector('.icon-moon');
    if (sun) sun.style.display = theme === 'light' ? 'none' : 'block';
    if (moon) moon.style.display = theme === 'light' ? 'block' : 'none';
    btn.setAttribute('aria-label', theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode');
  }

  btn.addEventListener('click', function () {
    apply(current() === 'dark' ? 'light' : 'dark');
  });

  apply(current());
})();
