(() => {
  const repoBase = '/terafab-decision-twin/';
  const repoUrl = 'https://github.com/KNOWDYN/terafab-decision-twin';
  const currentPage = document.body.dataset.page || 'index.html';
  const navItems = [
    ['index.html', 'Home'],
    ['model.html', 'Model'],
    ['scenarios.html', 'Scenarios'],
    ['policy.html', 'Policy'],
    ['evidence.html', 'Evidence'],
    ['researchers.html', 'Researchers'],
    ['getting-started.html', 'Deploy']
  ];

  const githubIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 .7a11.3 11.3 0 0 0-3.6 22c.6.1.8-.2.8-.6v-2c-3.3.7-4-1.5-4-1.5-.5-1.3-1.2-1.7-1.2-1.7-1-.7.1-.7.1-.7 1.1.1 1.7 1.2 1.7 1.2 1 1.7 2.7 1.2 3.4.9.1-.7.4-1.2.7-1.5-2.7-.3-5.5-1.3-5.5-5.9 0-1.3.5-2.4 1.2-3.2-.1-.3-.5-1.6.1-3.2 0 0 1-.3 3.3 1.2a11.4 11.4 0 0 1 6 0c2.3-1.5 3.3-1.2 3.3-1.2.6 1.6.2 2.9.1 3.2.8.9 1.2 1.9 1.2 3.2 0 4.6-2.8 5.6-5.5 5.9.4.4.8 1.1.8 2.2V22c0 .4.2.7.8.6A11.3 11.3 0 0 0 12 .7Z"/></svg>';

  function renderHeader() {
    const slot = document.querySelector('[data-site-header]');
    if (!slot) return;
    const navLinks = navItems.map(([href, label]) => {
      const active = href === currentPage ? ' class="active"' : '';
      return `<a${active} href="${href}">${label}</a>`;
    }).join('');

    slot.outerHTML = `<header class="topbar" data-nav>
  <a class="brand" href="index.html" aria-label="Terafab Decision Twin home"><span class="mark">TΔ</span><span><b>Terafab Decision Twin</b><small>Evidence-gated strategic model</small></span></a>
  <nav class="nav" aria-label="Primary navigation">${navLinks}</nav>
  <a class="repo-link" href="${repoUrl}" rel="noopener" aria-label="Open GitHub repository">${githubIcon} GitHub</a>
  <button class="menu" type="button" data-menu aria-label="Open menu" aria-expanded="false">☰</button>
</header>`;
  }

  function renderFooter() {
    const slot = document.querySelector('[data-site-footer]');
    if (!slot) return;
    slot.outerHTML = `<footer class="footer"><div class="shell footer-grid"><div><b>KNOWDYN public model</b><p>© 2026 KNOWDYN. All rights reserved except where repository license files expressly state otherwise.</p></div><div><b>Disclaimer</b><p>This site is independent and does not claim Terafab endorsement, authorization, private data access, or verified operating status.</p></div><div><b>Repository</b><p><a href="${repoUrl}">Source-available repository</a><br><a href="llms.txt">LLM guidance</a><br><a href="sitemap.xml">Sitemap</a></p></div></div></footer>`;
  }

  function bindMenu() {
    const topbar = document.querySelector('[data-nav]');
    const menu = document.querySelector('[data-menu]');
    if (!menu || !topbar) return;
    menu.addEventListener('click', () => {
      const open = topbar.classList.toggle('open');
      menu.setAttribute('aria-expanded', String(open));
      menu.textContent = open ? '×' : '☰';
    });
  }

  renderHeader();
  renderFooter();
  bindMenu();

  const installButton = document.querySelector('[data-install]');
  let deferredPrompt = null;

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
      window.setTimeout(() => { installButton.textContent = 'Keep this'; }, 3600);
    });
  }
})();
