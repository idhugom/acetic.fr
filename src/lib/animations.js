import Lenis from 'lenis';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

let lenis = null;
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- Smooth scroll (Lenis) ---------- */
function initLenis() {
  if (reduced || lenis) return;
  lenis = new Lenis({ duration: 1.1, easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), smoothWheel: true });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((time) => lenis && lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);
  document.documentElement.classList.add('lenis');
}

/* ---------- Reveal on scroll ---------- */
function initReveals() {
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -8% 0px' }
  );
  document.querySelectorAll('[data-reveal]:not(.is-in)').forEach((el) => io.observe(el));

  document.querySelectorAll('[data-reveal-stagger]:not(.is-in)').forEach((group) => {
    const kids = group.children;
    const gio = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            group.classList.add('is-in');
            [...kids].forEach((k, i) => (k.style.transitionDelay = `${i * 0.07}s`));
            gio.unobserve(group);
          }
        });
      },
      { threshold: 0.1 }
    );
    gio.observe(group);
  });
}

/* ---------- Header show/hide + scrolled ---------- */
function initHeader() {
  const header = document.querySelector('.site-header');
  if (!header) return;
  let last = 0;
  const onScroll = () => {
    const y = window.scrollY;
    header.classList.toggle('scrolled', y > 30);
    if (y > last && y > 300) header.classList.add('hide');
    else header.classList.remove('hide');
    last = y;
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* ---------- Counters ---------- */
function initCounters() {
  document.querySelectorAll('[data-count]').forEach((el) => {
    const target = parseFloat(el.dataset.count);
    if (reduced) { el.textContent = el.dataset.suffix ? target + el.dataset.suffix : target; return; }
    ScrollTrigger.create({
      trigger: el, start: 'top 90%', once: true,
      onEnter: () => {
        gsap.fromTo(el, { innerText: 0 }, {
          innerText: target, duration: 1.6, ease: 'power2.out', snap: { innerText: 1 },
          onUpdate: function () { el.textContent = Math.ceil(el.innerText ? this.targets()[0].innerText : 0) + (el.dataset.suffix || ''); },
          onComplete: () => { el.textContent = target + (el.dataset.suffix || ''); },
        });
      },
    });
  });
}

/* ---------- Hero intro ---------- */
function initHero() {
  const hero = document.querySelector('[data-hero]');
  if (!hero || reduced) return;
  const lines = hero.querySelectorAll('.hero-title .line > span');
  gsap.set(lines, { yPercent: 110 });
  gsap.to(lines, { yPercent: 0, duration: 1.1, ease: 'power4.out', stagger: 0.09, delay: 0.15 });
  const rest = hero.querySelectorAll('[data-hero-fade]');
  gsap.fromTo(rest, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.9, ease: 'power3.out', stagger: 0.1, delay: 0.6 });
}

/* ---------- Parallax on [data-parallax] ---------- */
function initParallax() {
  if (reduced) return;
  document.querySelectorAll('[data-parallax]').forEach((el) => {
    const speed = parseFloat(el.dataset.parallax) || 0.15;
    gsap.to(el, {
      yPercent: -speed * 100, ease: 'none',
      scrollTrigger: { trigger: el.closest('[data-parallax-root]') || el, start: 'top bottom', end: 'bottom top', scrub: true },
    });
  });
}

/* ---------- Magnetic buttons ---------- */
function initMagnetic() {
  if (reduced || window.matchMedia('(hover: none)').matches) return;
  document.querySelectorAll('[data-magnetic]').forEach((el) => {
    const strength = 0.35;
    el.addEventListener('mousemove', (e) => {
      const r = el.getBoundingClientRect();
      gsap.to(el, { x: (e.clientX - r.left - r.width / 2) * strength, y: (e.clientY - r.top - r.height / 2) * strength, duration: 0.5, ease: 'power3.out' });
    });
    el.addEventListener('mouseleave', () => gsap.to(el, { x: 0, y: 0, duration: 0.6, ease: 'elastic.out(1,0.4)' }));
  });
}

/* ---------- Read progress + TOC scrollspy ---------- */
function initReadProgress() {
  const bar = document.querySelector('.read-progress');
  const article = document.querySelector('[data-article-body]');
  if (!bar || !article) return;
  const onScroll = () => {
    const rect = article.getBoundingClientRect();
    const total = article.offsetHeight - window.innerHeight;
    const scrolled = Math.min(1, Math.max(0, -rect.top / total));
    bar.style.width = scrolled * 100 + '%';
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  const links = document.querySelectorAll('.toc-rail a[data-toc]');
  const sections = [...links].map((l) => document.querySelector(l.getAttribute('href'))).filter(Boolean);
  if (!sections.length) return;
  const spy = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          links.forEach((l) => l.classList.toggle('active', l.getAttribute('href') === '#' + e.target.id));
        }
      });
    },
    { rootMargin: '-30% 0px -60% 0px' }
  );
  sections.forEach((s) => spy.observe(s));
}

/* ---------- Mobile menu ---------- */
function initMobileMenu() {
  const burger = document.querySelector('.burger');
  const menu = document.querySelector('.mobile-nav');
  if (!burger || !menu) return;
  const toggle = () => {
    const open = menu.classList.toggle('open');
    burger.classList.toggle('open', open);
    document.body.style.overflow = open ? 'hidden' : '';
    if (lenis) open ? lenis.stop() : lenis.start();
  };
  burger.addEventListener('click', toggle);
  menu.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => { menu.classList.remove('open'); burger.classList.remove('open'); document.body.style.overflow = ''; if (lenis) lenis.start(); }));
}

/* ---------- rating fill ---------- */
function initRatings() {
  document.querySelectorAll('.rating .stars').forEach((el) => {
    const v = parseFloat(el.dataset.rating || '0');
    el.style.setProperty('--pct', (v / 5) * 100 + '%');
  });
}

function initAll() {
  initLenis();
  initHeader();
  initMobileMenu();
  initReveals();
  initCounters();
  initHero();
  initParallax();
  initMagnetic();
  initRatings();
  initReadProgress();
  ScrollTrigger.refresh();
}

/* Run on first load and after every Astro view transition */
document.addEventListener('astro:page-load', initAll);
