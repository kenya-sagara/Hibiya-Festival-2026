// HIBIYA LIVE FESTIVAL 2026 — main page interactions

(function () {
  'use strict';

  const DATA_URL = 'data/artists.json';

  // ---- Load data ----
  async function loadArtists() {
    try {
      const res = await fetch(DATA_URL, { cache: 'no-cache' });
      if (!res.ok) throw new Error('fetch failed: ' + res.status);
      return await res.json();
    } catch (err) {
      console.error('artists.json load failed', err);
      return null;
    }
  }

  function earliestSlot(artist) {
    return artist.slots.slice().sort((a, b) => {
      return (a.day + ' ' + a.time).localeCompare(b.day + ' ' + b.time);
    })[0];
  }

  function venueLabel(slots) {
    const uniq = Array.from(new Set(slots.map((s) => s.venue)));
    return uniq.join(' / ');
  }

  function slotsLine(slots) {
    // Show up to 2 slots inline; if more, summarise.
    const sorted = slots.slice().sort((a, b) => (a.day + ' ' + a.time).localeCompare(b.day + ' ' + b.time));
    return sorted
      .map((s) => `${s.day} ${s.time}–`)
      .join(' / ');
  }

  // ---- Build artist grid ----
  function buildArtists(data) {
    const grid = document.getElementById('artistsGrid');
    if (!grid || !data) return;

    // Sort in timetable order (earliest slot day+time).
    const list = data.artists.slice().sort((a, b) => {
      const ka = earliestSlot(a);
      const kb = earliestSlot(b);
      return (ka.day + ' ' + ka.time).localeCompare(kb.day + ' ' + kb.time);
    });

    const frag = document.createDocumentFragment();
    for (const a of list) {
      const el = document.createElement('article');
      el.className = 'artist reveal';
      el.id = 'artist-' + a.slug;

      // --- photo (wrapped in a link) ---
      const photoLink = document.createElement('a');
      photoLink.href = `artists/${a.slug}.html`;
      photoLink.className = 'artist__link';
      photoLink.setAttribute('aria-label', `${a.name} の詳細ページを開く`);

      const photo = document.createElement('div');
      if (a.photo) {
        photo.className = 'artist__photo';
        const img = document.createElement('img');
        img.src = `assets/artists/${a.photo}`;
        img.alt = a.name;
        img.loading = 'lazy';
        img.decoding = 'async';
        photo.appendChild(img);
      } else {
        photo.className = 'artist__photo artist__photo--placeholder';
      }
      photoLink.appendChild(photo);

      // --- body ---
      const body = document.createElement('div');
      body.className = 'artist__body';

      const venue = document.createElement('p');
      venue.className = 'artist__venue';
      venue.textContent = venueLabel(a.slots);

      const nameLink = document.createElement('a');
      nameLink.href = `artists/${a.slug}.html`;
      nameLink.className = 'artist__name-link';

      const name = document.createElement('h3');
      name.className = 'artist__name';
      name.textContent = a.name;
      nameLink.appendChild(name);

      const slot = document.createElement('p');
      slot.className = 'artist__slot';
      slot.textContent = slotsLine(a.slots);

      body.appendChild(venue);
      body.appendChild(nameLink);
      if (a.desc) {
        const desc = document.createElement('p');
        desc.className = 'artist__desc';
        desc.textContent = a.desc;
        body.appendChild(desc);
      }
      body.appendChild(slot);

      el.appendChild(photoLink);
      el.appendChild(body);
      frag.appendChild(el);
    }
    grid.appendChild(frag);
  }

  // ---- Header scroll state ----
  function initHeader() {
    const header = document.getElementById('siteHeader');
    if (!header) return;
    const onScroll = () => {
      header.classList.toggle('is-scrolled', window.scrollY > 40);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ---- Mobile nav ----
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

  // ---- Highlight when arriving from timetable ----
  function initArtistHighlight() {
    const highlight = (id) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.classList.remove('is-targeted');
      void el.offsetWidth;
      el.classList.add('is-targeted');
    };
    const highlightFromHash = () => {
      const hash = location.hash;
      if (!hash || !hash.startsWith('#artist-')) return;
      highlight(hash.slice(1));
    };
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a[href^="#artist-"]');
      if (!link) return;
      const id = link.getAttribute('href').slice(1);
      requestAnimationFrame(() => highlight(id));
    });
    window.addEventListener('hashchange', highlightFromHash);
    window.addEventListener('load', highlightFromHash);
  }

  // ---- Reveal on scroll ----
  function initReveal() {
    if (!('IntersectionObserver' in window)) {
      document.querySelectorAll('.reveal').forEach((el) => el.classList.add('is-revealed'));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('is-revealed');
            io.unobserve(e.target);
          }
        });
      },
      { rootMargin: '0px 0px -10% 0px', threshold: 0.05 }
    );
    const attach = () => {
      const targets = document.querySelectorAll(
        '.section__head, .about__body, .stats, .stage, .venue, .access, .reveal'
      );
      targets.forEach((t) => {
        if (t.classList.contains('is-revealed')) return;
        t.classList.add('reveal');
        io.observe(t);
      });
    };
    attach();
    // re-run after artist grid is populated
    const grid = document.getElementById('artistsGrid');
    if (grid) {
      const mo = new MutationObserver(() => attach());
      mo.observe(grid, { childList: true });
    }
  }

  // ---- Access map (Leaflet + CARTO Dark tiles) ----
  function initAccessMap() {
    const el = document.getElementById('accessMap');
    if (!el || typeof L === 'undefined') return;

    const venues = [
      { num: '01', name: '日比谷ステップ広場 特設ステージ', sub: '東京メトロ日比谷駅 A11出口直結', latlng: [35.6740, 139.7589] },
      { num: '02', name: 'HIBIYA FOOD HALL',               sub: '東京ミッドタウン日比谷 B1F',     latlng: [35.6739, 139.7593] },
      { num: '03', name: '日比谷OKUROJI',                   sub: 'JR新橋駅 / 有楽町駅 徒歩約4分',  latlng: [35.6695, 139.7595] },
    ];

    const map = L.map(el, {
      scrollWheelZoom: false,
      zoomControl: true,
      attributionControl: true,
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19,
    }).addTo(map);

    venues.forEach((v) => {
      const icon = L.divIcon({
        className: 'venue-pin',
        html: `<div class="venue-pin__inner"><span>${v.num}</span></div><div class="venue-pin__shadow"></div>`,
        iconSize: [44, 56],
        iconAnchor: [22, 52],
        popupAnchor: [0, -50],
      });
      L.marker(v.latlng, { icon, title: v.name })
        .addTo(map)
        .bindPopup(
          `<strong>${v.name}</strong><br /><span class="venue-popup__sub">${v.sub}</span>`,
          { className: 'venue-popup', closeButton: true }
        );
    });

    const bounds = L.latLngBounds(venues.map((v) => v.latlng));
    map.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
  }

  // ---- Boot ----
  document.addEventListener('DOMContentLoaded', async () => {
    initHeader();
    initNavToggle();
    initReveal();
    initArtistHighlight();
    initAccessMap();
    const data = await loadArtists();
    if (data) buildArtists(data);
  });
})();
