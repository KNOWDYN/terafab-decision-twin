(() => {
  const repoBase = '/terafab-decision-twin/';
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register(`${repoBase}service-worker.js`).catch(() => {});
    });
  }

  const button = document.querySelector('.keep-site');
  let deferredPrompt = null;

  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    deferredPrompt = event;
    if (button) button.hidden = false;
  });

  if (button) {
    const isiOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
    const standalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;
    if (isiOS && !standalone) button.hidden = false;

    button.addEventListener('click', async () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        await deferredPrompt.userChoice.catch(() => null);
        deferredPrompt = null;
        button.hidden = true;
        return;
      }
      button.textContent = 'Share → Add to Home Screen';
      window.setTimeout(() => { button.textContent = 'Keep this site'; }, 3600);
    });
  }
})();
