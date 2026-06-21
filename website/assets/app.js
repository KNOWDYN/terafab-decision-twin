(() => {
  const base = '/terafab-decision-twin/website/';
  const deck = document.querySelector('[data-deck]');
  const slides = deck ? Array.from(deck.querySelectorAll('.slide')) : [];
  const navLinks = Array.from(document.querySelectorAll('[data-nav] a'));
  const prev = document.querySelector('[data-prev]');
  const next = document.querySelector('[data-next]');
  const dots = document.querySelector('[data-dots]');
  const installButton = document.querySelector('[data-install]');
  let deferredPrompt = null;

  function currentIndex() {
    if (!deck || !slides.length) return 0;
    const left = deck.scrollLeft;
    let closest = 0;
    slides.forEach((slide, index) => {
      if (Math.abs(slide.offsetLeft - left) < Math.abs(slides[closest].offsetLeft - left)) closest = index;
    });
    return closest;
  }

  function goTo(index) {
    if (!deck || !slides[index]) return;
    slides[index].scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', inline: 'start', block: 'nearest' });
  }

  function update(index = currentIndex()) {
    navLinks.forEach(link => link.classList.toggle('active', slides[index] && link.hash === `#${slides[index].id}`));
    if (prev) prev.disabled = index === 0;
    if (next) next.disabled = index === slides.length - 1;
    if (dots) Array.from(dots.children).forEach((dot, dotIndex) => dot.setAttribute('aria-current', dotIndex === index ? 'step' : 'false'));
  }

  if (dots && slides.length) {
    dots.innerHTML = slides.map((slide, index) => `<button type="button" aria-label="Go to slide ${index + 1}: ${slide.id}" data-dot="${index}"></button>`).join('');
    dots.addEventListener('click', event => {
      const button = event.target.closest('[data-dot]');
      if (button) goTo(Number(button.dataset.dot));
    });
  }

  if (prev) prev.addEventListener('click', () => goTo(Math.max(0, currentIndex() - 1)));
  if (next) next.addEventListener('click', () => goTo(Math.min(slides.length - 1, currentIndex() + 1)));

  navLinks.forEach(link => link.addEventListener('click', event => {
    const target = slides.findIndex(slide => `#${slide.id}` === link.hash);
    if (target >= 0) {
      event.preventDefault();
      goTo(target);
      history.replaceState(null, '', link.hash);
    }
  }));

  let scrollTimer = null;
  if (deck) deck.addEventListener('scroll', () => {
    window.clearTimeout(scrollTimer);
    scrollTimer = window.setTimeout(() => update(), 80);
  }, { passive: true });

  window.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (event.key === 'ArrowRight') { event.preventDefault(); goTo(Math.min(slides.length - 1, currentIndex() + 1)); }
    if (event.key === 'ArrowLeft') { event.preventDefault(); goTo(Math.max(0, currentIndex() - 1)); }
  });

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register(`${base}service-worker.js`).catch(() => null);
    });
  }

  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault();
    deferredPrompt = event;
    if (installButton) installButton.hidden = false;
  });

  if (installButton) {
    const isiOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
    const standalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;
    if (isiOS && !standalone) installButton.hidden = false;
    installButton.addEventListener('click', async () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        await deferredPrompt.userChoice.catch(() => null);
        deferredPrompt = null;
        installButton.hidden = true;
        return;
      }
      installButton.textContent = 'Share → Add to Home Screen';
      window.setTimeout(() => { installButton.textContent = 'Keep this'; }, 3600);
    });
  }

  if (location.hash) {
    const target = slides.findIndex(slide => `#${slide.id}` === location.hash);
    if (target >= 0) window.setTimeout(() => goTo(target), 80);
  }
  update(0);
})();
