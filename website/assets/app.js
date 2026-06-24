(() => {
  const base = '/terafab-decision-twin/website/';
  const sections = Array.from(document.querySelectorAll('main section[id]'));
  const navLinks = Array.from(document.querySelectorAll('[data-nav] a[href^="#"]'));
  const installButton = document.querySelector('[data-install]');
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let deferredPrompt = null;

  function findHashTarget(hash) {
    if (!hash || hash === '#') return null;
    try {
      return document.getElementById(decodeURIComponent(hash.slice(1)));
    } catch (error) {
      return null;
    }
  }

  function getTarget(link) {
    return findHashTarget(link.hash);
  }

  function setActive(id) {
    navLinks.forEach(link => {
      const isActive = link.hash === `#${id}`;
      link.classList.toggle('active', isActive);
      if (isActive) {
        link.setAttribute('aria-current', 'location');
      } else {
        link.removeAttribute('aria-current');
      }
    });
  }

  function scrollToSection(target) {
    target.scrollIntoView({
      behavior: prefersReducedMotion.matches ? 'auto' : 'smooth',
      block: 'start',
    });
    history.replaceState(null, '', `#${target.id}`);
    setActive(target.id);
  }

  if ('IntersectionObserver' in window && sections.length) {
    const observer = new IntersectionObserver(entries => {
      const visible = entries
        .filter(entry => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (visible) setActive(visible.target.id);
    }, { rootMargin: '-25% 0px -55% 0px', threshold: [0.15, 0.35, 0.6] });
    sections.forEach(section => observer.observe(section));
  } else if (sections[0]) {
    setActive(sections[0].id);
  }

  navLinks.forEach(link => link.addEventListener('click', event => {
    const target = getTarget(link);
    if (!target) return;
    event.preventDefault();
    scrollToSection(target);
  }));

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
      window.setTimeout(() => { installButton.textContent = 'Save site'; }, 3600);
    });
  }

  if (location.hash) {
    const target = findHashTarget(location.hash);
    if (target) window.setTimeout(() => scrollToSection(target), 80);
  } else if (sections[0]) {
    setActive(sections[0].id);
  }
})();
