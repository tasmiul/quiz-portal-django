(function () {
  'use strict';

  const state = {
    categories: [],
    currentQuiz: null,
    currentIndex: 0,
    answers: {},
    elapsedSeconds: 0,
    timerInterval: null,
    timeLimitSeconds: 0,
  };

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  const views = {
    home: $('#view-home'),
    intro: $('#view-intro'),
    play: $('#view-play'),
    results: $('#view-results'),
  };

  async function api(url, options = {}) {
    const res = await fetch(url, options);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'Something went wrong');
    return data;
  }

  function showView(name) {
    Object.values(views).forEach((v) => v.classList.add('hidden'));
    views[name].classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function goHome() {
    if (state.timerInterval) clearInterval(state.timerInterval);
    stopConfetti();
    showView('home');
    loadHome();
  }

  let toastTimer;
  function toast(message, isError = false) {
    const el = $('#toast');
    el.textContent = message;
    el.classList.toggle('error', isError);
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('show'), 2600);
  }

  async function loadHome() {
    try {
      if (!state.categories.length) {
        const data = await api('/api/categories/');
        state.categories = data.categories;
        populateCategoriesMenu();
      }
      const home = await api('/api/home/');
      renderTrending(home.trending);
      renderFeatured(home.featured_categories);
    } catch (err) {
      toast('Failed to load homepage: ' + err.message, true);
    }
  }

  function populateCategoriesMenu() {
    const menu = $('#categories-menu');
    const allItem = menu.querySelector('.dropdown-item[data-count="all"]');
    if (allItem) allItem.querySelector('[data-count]').textContent = state.categories.reduce((s, c) => s + c.quiz_count, 0);
    state.categories.forEach((cat) => {
      const a = document.createElement('a');
      a.className = 'dropdown-item';
      a.href = '/category/' + cat.slug + '/';
      a.innerHTML =
        '<span class="dropdown-emoji">' + cat.emoji + '</span>' +
        '<span class="dropdown-name">' + escapeHtml(cat.name) + '</span>' +
        '<span class="dropdown-count">' + cat.quiz_count + '</span>';
      menu.appendChild(a);
    });
  }

  function openCategoriesMenu() {
    const menu = $('#categories-menu');
    menu.classList.remove('hidden');
    $('#categories-trigger').setAttribute('aria-expanded', 'true');
    $('#categories-trigger').classList.add('is-open');
  }

  function closeCategoriesMenu() {
    const menu = $('#categories-menu');
    menu.classList.add('hidden');
    $('#categories-trigger').setAttribute('aria-expanded', 'false');
    $('#categories-trigger').classList.remove('is-open');
  }

  function toggleCategoriesMenu() {
    $('#categories-menu').classList.contains('hidden') ? openCategoriesMenu() : closeCategoriesMenu();
  }

  function renderTrending(quizzes) {
    const grid = $('#trending-grid');
    grid.innerHTML = '';
    if (!quizzes.length) {
      grid.innerHTML = '<div class="empty-state"><p>No quizzes yet — check back soon.</p></div>';
      return;
    }
    quizzes.forEach((quiz, i) => {
      const card = document.createElement('article');
      card.className = 'trending-card';
      card.style.setProperty('--card-f', quiz.category.gradient_from);
      card.style.setProperty('--card-t', quiz.category.gradient_to);
      card.style.animationDelay = (i * 0.06) + 's';
      card.innerHTML =
        '<div class="quiz-card-top">' +
          '<div class="quiz-emoji">' + quiz.category.emoji + '</div>' +
          '<span class="difficulty-badge ' + quiz.difficulty + '">' + quiz.difficulty + '</span>' +
        '</div>' +
        '<p class="card-category">' + quiz.category.name + '</p>' +
        '<h3 class="trending-title">' + escapeHtml(quiz.title) + '</h3>' +
        '<div class="quiz-card-meta">' +
          '<span>❓ ' + quiz.questions_count + ' questions</span>' +
          '<span>⏱ ' + quiz.duration_minutes + ' min</span>' +
          '<span>▶ ' + quiz.attempts + ' plays</span>' +
        '</div>' +
        '<button class="btn btn-primary btn-sm"><span>▶</span> Start quiz</button>';
      card.addEventListener('click', () => openQuiz(quiz.id));
      grid.appendChild(card);
    });
  }

  function renderFeatured(categories) {
    const wrap = $('#featured-categories');
    wrap.innerHTML = '';
    categories.forEach((cat, ci) => {
      const section = document.createElement('section');
      section.className = 'featured-cat';
      section.style.animationDelay = (ci * 0.08) + 's';

      const cardsHtml = cat.quizzes.map((quiz, i) => {
        return '<article class="mini-card reveal" data-id="' + quiz.id + '" style="--card-f:' + quiz.category.gradient_from + ';--card-t:' + quiz.category.gradient_to + ';animation-delay:' + (i * 0.05) + 's">' +
          '<div class="mini-top"><span class="difficulty-badge ' + quiz.difficulty + '">' + quiz.difficulty + '</span></div>' +
          '<h3 class="mini-title">' + escapeHtml(quiz.title) + '</h3>' +
          '<div class="mini-meta">' +
            '<span>❓ ' + quiz.questions_count + '</span>' +
            '<span>⏱ ' + quiz.duration_minutes + ' min</span>' +
          '</div>' +
          '<button class="btn btn-primary btn-sm"><span>▶</span> Start quiz</button>' +
        '</article>';
      }).join('');

      const desc = cat.description ? cat.description : 'Take on ' + cat.name + ' quizzes and climb the ranks.';
      section.innerHTML =
        '<div class="featured-head reveal">' +
          '<div class="featured-emoji" style="background:linear-gradient(135deg,' + cat.gradient_from + ',' + cat.gradient_to + ')">' + cat.emoji + '</div>' +
          '<div class="featured-titles">' +
            '<h3 class="featured-name">' + escapeHtml(cat.name) + '</h3>' +
            '<p class="featured-desc">' + escapeHtml(desc) + '</p>' +
          '</div>' +
        '</div>' +
        '<div class="mini-grid">' + cardsHtml + '</div>' +
        '<div class="view-all-wrap">' +
          '<a class="view-all-btn" href="/category/' + cat.slug + '/">View all ' + escapeHtml(cat.name) + ' <span>→</span></a>' +
        '</div>';

      section.querySelectorAll('.mini-card').forEach((card) => {
        card.addEventListener('click', () => openQuiz(parseInt(card.dataset.id, 10)));
      });
      wrap.appendChild(section);
    });
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  async function openQuiz(id) {
    try {
      state.currentQuiz = await api('/api/quizzes/' + id + '/');
      renderIntro();
      showView('intro');
    } catch (err) {
      toast('Failed to load quiz: ' + err.message, true);
    }
  }

  function renderIntro() {
    const quiz = state.currentQuiz;
    const card = $('#intro-card');
    const c = quiz.category;
    card.innerHTML =
      '<div class="intro-banner" style="background:linear-gradient(135deg,' + c.gradient_from + ',' + c.gradient_to + ')">' +
        '<div class="intro-emoji">' + c.emoji + '</div>' +
      '</div>' +
      '<div class="intro-body">' +
        '<h1>' + escapeHtml(quiz.title) + '</h1>' +
        '<p>' + escapeHtml(quiz.description) + '</p>' +
        '<div class="intro-stats">' +
          '<div class="intro-stat"><b>' + quiz.questions_count + '</b><span>Questions</span></div>' +
          '<div class="intro-stat"><b>' + quiz.duration_minutes + '</b><span>Minutes</span></div>' +
          '<div class="intro-stat"><b>' + cap(quiz.difficulty) + '</b><span>Difficulty</span></div>' +
          '<div class="intro-stat"><b>' + quiz.pass_percent + '%</b><span>To pass</span></div>' +
        '</div>' +
        '<div class="intro-rules">⚠️ <b>Heads up:</b> A timer starts as soon as you begin. Score ' + quiz.pass_percent + '% or more to pass. Your answers are only counted once you hit submit.</div>' +
        '<div class="intro-actions">' +
          '<button class="btn btn-primary btn-glow" id="start-btn"><span>▶</span> Start quiz</button>' +
          '<button class="btn btn-ghost" id="intro-back-btn">Go back</button>' +
        '</div>' +
      '</div>';

    $('#start-btn').addEventListener('click', startQuiz);
    $('#intro-back-btn').addEventListener('click', goHome);
  }

  function cap(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  function startQuiz() {
    state.currentIndex = 0;
    state.answers = {};
    state.elapsedSeconds = 0;
    state.timeLimitSeconds = state.currentQuiz.duration_minutes * 60;

    const questions = state.currentQuiz.questions;
    $('#play-category').textContent = state.currentQuiz.category.emoji + ' ' + state.currentQuiz.category.name;
    $('#question-counter').textContent = '';

    if (state.timerInterval) clearInterval(state.timerInterval);
    state.timerInterval = setInterval(tick, 1000);
    tick();

    showView('play');
    renderQuestion(0);
  }

  function tick() {
    state.elapsedSeconds++;
    if (state.elapsedSeconds >= state.timeLimitSeconds) {
      clearInterval(state.timerInterval);
      state.timerInterval = null;
      renderTimer();
      submitQuiz(true);
      return;
    }
    renderTimer();
  }

  function renderTimer() {
    const remaining = Math.max(0, state.timeLimitSeconds - state.elapsedSeconds);
    const mm = String(Math.floor(remaining / 60)).padStart(2, '0');
    const ss = String(remaining % 60).padStart(2, '0');
    const chip = $('.timer-chip');
    $('#timer-text').textContent = mm + ':' + ss;
    chip.classList.toggle('low', remaining <= 30 && remaining > 0);
  }

  function renderQuestion(index) {
    const quiz = state.currentQuiz;
    const question = quiz.questions[index];
    state.currentIndex = index;

    $('#question-counter').textContent = (index + 1) + ' / ' + quiz.questions.length;
    $('#progress-bar span').style.width = (((index + 1) / quiz.questions.length) * 100) + '%';

    const qEl = $('#question-text');
    qEl.style.animation = 'none';
    void qEl.offsetWidth;
    qEl.style.animation = '';
    qEl.textContent = question.text;

    const choicesWrap = $('#choices');
    choicesWrap.innerHTML = '';

    question.choices.forEach((choice, i) => {
      const btn = document.createElement('button');
      btn.className = 'choice';
      btn.style.animationDelay = (i * 0.07) + 's';
      const letter = String.fromCharCode(65 + i);
      btn.innerHTML = '<span class="choice-letter">' + letter + '</span><span>' + escapeHtml(choice.text) + '</span>';
      btn.dataset.choiceId = choice.id;

      if (state.answers[question.id] === choice.id) btn.classList.add('is-selected');

      btn.addEventListener('click', () => selectChoice(question.id, choice.id));
      choicesWrap.appendChild(btn);
    });

    $('#choice-error').classList.add('hidden');

    const isLast = index === quiz.questions.length - 1;
    $('#next-btn').classList.toggle('hidden', isLast);
    $('#submit-btn').classList.toggle('hidden', !isLast);
    $('#prev-btn').disabled = index === 0;
    $('#prev-btn').classList.toggle('hidden', index === 0);
  }

  function selectChoice(questionId, choiceId) {
    state.answers[questionId] = choiceId;
    $$('#choices .choice').forEach((c) => {
      c.classList.toggle('is-selected', c.dataset.choiceId === String(choiceId));
    });
  }

  function nextQuestion() {
    const question = state.currentQuiz.questions[state.currentIndex];
    if (state.answers[question.id] === undefined) {
      $('#choice-error').classList.remove('hidden');
      return;
    }
    if (state.currentIndex < state.currentQuiz.questions.length - 1) {
      renderQuestion(state.currentIndex + 1);
    }
  }

  function prevQuestion() {
    if (state.currentIndex > 0) renderQuestion(state.currentIndex - 1);
  }

  async function submitQuiz(autoTimeout = false) {
    if (state.timerInterval) {
      clearInterval(state.timerInterval);
      state.timerInterval = null;
    }
    if (!autoTimeout) {
      const question = state.currentQuiz.questions[state.currentIndex];
      if (state.answers[question.id] === undefined) {
        $('#choice-error').classList.remove('hidden');
        toast('Answer this question before submitting', true);
        startTimerAgain();
        return;
      }
    }

    $('#submit-btn').disabled = true;
    const payload = {
      answers: Object.entries(state.answers).map(([qid, cid]) => ({
        question_id: parseInt(qid, 10),
        choice_id: cid,
      })),
    };

    try {
      const result = await api('/api/quizzes/' + state.currentQuiz.id + '/submit/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      renderResults(result);
    } catch (err) {
      toast('Failed to submit: ' + err.message, true);
      $('#submit-btn').disabled = false;
      startTimerAgain();
    }
  }

  function startTimerAgain() {
    if (!state.timerInterval) {
      state.timerInterval = setInterval(tick, 1000);
    }
  }

  function renderResults(result) {
    const score = result.score;
    $('#score-value').textContent = score + '%';
    $('#results-title').textContent = result.quiz_title;

    const stats = $('#stat-correct').parentElement;
    $('#stat-correct').textContent = result.correct_count;
    $('#stat-correct').classList.add('green');
    $('#stat-wrong').textContent = result.total - result.correct_count;
    $('#stat-wrong').classList.add('red');
    $('#stat-total').textContent = result.total;

    const mm = String(Math.floor(state.elapsedSeconds / 60)).padStart(2, '0');
    const ss = String(state.elapsedSeconds % 60).padStart(2, '0');
    $('#stat-time').textContent = mm + ':' + ss;

    let msg;
    if (score === 100) msg = '🏆 Flawless! You are a true master of this subject.';
    else if (score >= 80) msg = '🎉 Outstanding! So close to perfection.';
    else if (score >= 60) msg = '👍 Good job! A solid performance.';
    else if (score >= 40) msg = '💪 Not bad — review the answers below and try again.';
    else msg = '📚 Keep learning! Check the review and give it another shot.';
    $('#results-message').textContent = msg;

    renderReview(result.results);

    setTimeout(() => {
      const ring = $('#ring-fg');
      ring.style.strokeDashoffset = 427.3 * (1 - score / 100);
    }, 200);

    if (score >= 60) launchConfetti();

    showView('results');
  }

  function renderReview(results) {
    const list = $('#review-list');
    list.innerHTML = '<h3 class="review-heading">📋 Answer review</h3>';

    results.forEach((item, idx) => {
      const div = document.createElement('div');
      div.className = 'review-item ' + (item.is_correct ? 'correct' : 'wrong');
      const icon = item.is_correct ? '✅' : '❌';
      div.innerHTML =
        '<div class="review-q"><span class="icon">' + icon + '</span><span>' + (idx + 1) + '. ' + escapeHtml(item.question_text) + '</span></div>' +
        '<div class="review-choices"></div>';
      const choicesWrap = div.querySelector('.review-choices');

      item.choices.forEach((choice) => {
        const row = document.createElement('div');
        row.className = 'review-choice';
        if (choice.is_correct) {
          row.classList.add('correct-choice');
          row.innerHTML = '<span class="dot">●</span><span>' + escapeHtml(choice.text) + '</span>';
        } else if (choice.id === item.chosen_id) {
          row.classList.add('wrong-choice');
          row.innerHTML = '<span class="dot">✕</span><span>' + escapeHtml(choice.text) + '</span>';
        } else {
          row.innerHTML = '<span class="dot">·</span><span>' + escapeHtml(choice.text) + '</span>';
        }
        choicesWrap.appendChild(row);
      });

      list.appendChild(div);
    });
  }

  let confettiCtx = null;
  let confettiPieces = [];
  let confettiRaf = null;
  let canvasEl = null;

  function launchConfetti() {
    if (!canvasEl) {
      canvasEl = document.createElement('canvas');
      canvasEl.id = 'confetti-canvas';
      document.body.appendChild(canvasEl);
    }
    canvasEl.width = window.innerWidth;
    canvasEl.height = window.innerHeight;
    confettiCtx = canvasEl.getContext('2d');
    const colors = ['#8b5cf6', '#22d3ee', '#34d399', '#fbbf24', '#f472b6', '#f87171'];
    confettiPieces = [];
    for (let i = 0; i < 160; i++) {
      confettiPieces.push({
        x: Math.random() * canvasEl.width,
        y: -20 - Math.random() * canvasEl.height * 0.4,
        w: 6 + Math.random() * 8,
        h: 8 + Math.random() * 10,
        color: colors[Math.floor(Math.random() * colors.length)],
        vy: 2 + Math.random() * 3.5,
        vx: -1.5 + Math.random() * 3,
        rot: Math.random() * Math.PI,
        vrot: -0.1 + Math.random() * 0.2,
      });
    }
    if (confettiRaf) cancelAnimationFrame(confettiRaf);
    confettiLoop();
  }

  function confettiLoop() {
    confettiCtx.clearRect(0, 0, canvasEl.width, canvasEl.height);
    let alive = false;
    confettiPieces.forEach((p) => {
      p.x += p.vx;
      p.y += p.vy;
      p.rot += p.vrot;
      confettiCtx.save();
      confettiCtx.translate(p.x, p.y);
      confettiCtx.rotate(p.rot);
      confettiCtx.fillStyle = p.color;
      confettiCtx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
      confettiCtx.restore();
      if (p.y < canvasEl.height + 30) alive = true;
    });
    if (alive) {
      confettiRaf = requestAnimationFrame(confettiLoop);
    } else {
      stopConfetti();
    }
  }

  function stopConfetti() {
    if (confettiRaf) {
      cancelAnimationFrame(confettiRaf);
      confettiRaf = null;
    }
    if (canvasEl) {
      canvasEl.remove();
      canvasEl = null;
    }
    confettiCtx = null;
  }

  const contactForm = $('#contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = $('#contact-name').value.trim();
      const email = $('#contact-email').value.trim();
      const subject = $('#contact-subject').value.trim();
      const message = $('#contact-message').value.trim();
      if (!name || !email || !subject || !message) {
        toast('Please fill in all fields.', true);
        return;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        toast('Please enter a valid email address.', true);
        return;
      }
      e.target.reset();
      toast('Thanks, ' + name + '! Your message has been sent.');
    });
  }

  $('#categories-trigger').addEventListener('click', (e) => {
    e.stopPropagation();
    toggleCategoriesMenu();
  });

  $('#categories-menu').addEventListener('click', (e) => {
    if (!e.target.closest('.dropdown-item')) return;
    closeCategoriesMenu();
  });

  document.addEventListener('click', (e) => {
    const dropdown = $('#categories-dropdown');
    if (!dropdown.contains(e.target)) {
      closeCategoriesMenu();
    }
    const btn = e.target.closest('[data-action]');
    if (!btn) return;
    const action = btn.dataset.action;
    if (action === 'scroll-trending') $('#trending').scrollIntoView({ behavior: 'smooth' });
    else if (action === 'go-home') goHome();
    else if (action === 'quit-quiz') {
      if (confirm('Quit this quiz? Your progress will be lost.')) goHome();
    } else if (action === 'next-question') nextQuestion();
    else if (action === 'prev-question') prevQuestion();
    else if (action === 'submit-quiz') submitQuiz();
    else if (action === 'retake') startQuiz();
  });

  $('.logo').addEventListener('click', goHome);

  window.addEventListener('resize', () => {
    if (canvasEl) {
      canvasEl.width = window.innerWidth;
      canvasEl.height = window.innerHeight;
    }
  });

  const deepQuizId = parseInt(new URLSearchParams(location.search).get('quiz'), 10);
  if (deepQuizId) {
    openQuiz(deepQuizId);
  } else {
    loadHome();
  }
})();
