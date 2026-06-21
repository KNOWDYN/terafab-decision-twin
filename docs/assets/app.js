(() => {
  const repoBase = '/terafab-decision-twin/';
  const topbar = document.querySelector('[data-nav]');
  const menu = document.querySelector('[data-menu]');
  const installButton = document.querySelector('[data-install]');
  let deferredPrompt = null;

  if (menu && topbar) {
    menu.addEventListener('click', () => {
      const open = topbar.classList.toggle('open');
      menu.setAttribute('aria-expanded', String(open));
      menu.textContent = open ? '×' : '☰';
    });
  }

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register(`${repoBase}service-worker.js`).catch(() => null);
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
      window.setTimeout(() => { installButton.textContent = 'Install'; }, 3600);
    });
  }
})();
