// Per-artist page interactions: URL copy + header scroll state + mobile nav.

(function () {
  'use strict';

  function initHeader() {
    const header = document.getElementById('siteHeader');
    if (!header) return;
    const onScroll = () => {
      header.classList.toggle('is-scrolled', window.scrollY > 40);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  function initNavToggle() {
    const btn = document.getElementById('navToggle');
    const nav = document.querySelector('.nav');
    if (!btn || !nav) return;
    const close = () => {
      btn.classList.remove('is-open');
      nav.classList.remove('is-open');
      btn.setAttribute('aria-expanded', 'false');
    };
    btn.addEventListener('click', () => {
      const open = !btn.classList.contains('is-open');
      btn.classList.toggle('is-open', open);
      nav.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.querySelectorAll('a').forEach((a) => a.addEventListener('click', close));
  }

  async function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (_) {
        // fall through to legacy path
      }
    }
    // fallback for non-secure contexts
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.top = '-1000px';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      return true;
    } catch (_) {
      return false;
    } finally {
      document.body.removeChild(ta);
    }
  }

  function initCopyButtons() {
    document.querySelectorAll('.share-btn--copy').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const url = btn.dataset.copyUrl || location.href;
        const ok = await copyToClipboard(url);
        if (ok) {
          btn.classList.add('is-copied');
          setTimeout(() => btn.classList.remove('is-copied'), 2200);
        }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    initHeader();
    initNavToggle();
    initCopyButtons();
  });
})();
