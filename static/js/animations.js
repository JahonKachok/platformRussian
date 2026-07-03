/* ============ ANIMATIONS.JS ============ */
'use strict';

// ============ SCROLL REVEAL ============
const ScrollReveal = {
  init() {
    const elements = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');
    if (!elements.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });

    elements.forEach(el => observer.observe(el));
  }
};

// ============ COUNTER ANIMATION ============
const Counter = {
  animate(el) {
    const target = parseInt(el.dataset.target) || 0;
    const duration = 1800;
    const start = performance.now();

    const update = (now) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(eased * target).toLocaleString();
      if (progress < 1) requestAnimationFrame(update);
    };

    requestAnimationFrame(update);
  },

  init() {
    const counters = document.querySelectorAll('.counter[data-target]');
    if (!counters.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          this.animate(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    counters.forEach(c => observer.observe(c));
  }
};

// ============ PROGRESS BAR ANIMATION ============
const ProgressBars = {
  init() {
    const bars = document.querySelectorAll('.progress-bar[style*="width"]');
    if (!bars.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const bar = entry.target;
          const targetWidth = bar.style.width;
          bar.style.width = '0%';
          requestAnimationFrame(() => {
            bar.style.transition = 'width 1s cubic-bezier(0.4, 0, 0.2, 1)';
            bar.style.width = targetWidth;
          });
          observer.unobserve(bar);
        }
      });
    }, { threshold: 0.2 });

    bars.forEach(b => observer.observe(b));
  }
};

// ============ TYPING EFFECT ============
const TypeWriter = {
  write(el, words, speed = 80, pause = 2000) {
    let wordIdx = 0;
    let charIdx = 0;
    let deleting = false;

    const tick = () => {
      const word = words[wordIdx];
      if (deleting) {
        el.textContent = word.substring(0, --charIdx);
      } else {
        el.textContent = word.substring(0, ++charIdx);
      }

      let delay = deleting ? speed / 2 : speed;
      if (!deleting && charIdx === word.length) {
        delay = pause;
        deleting = true;
      } else if (deleting && charIdx === 0) {
        deleting = false;
        wordIdx = (wordIdx + 1) % words.length;
      }

      setTimeout(tick, delay);
    };

    tick();
  },

  init() {
    document.querySelectorAll('[data-typewriter]').forEach(el => {
      const words = el.dataset.typewriter.split('|');
      this.write(el, words);
    });
  }
};

// ============ CONFETTI ============
const Confetti = {
  colors: ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#3b82f6', '#ec4899'],

  burst(count = 80) {
    for (let i = 0; i < count; i++) {
      const piece = document.createElement('div');
      piece.className = 'confetti-piece';
      piece.style.cssText = `
        left: ${Math.random() * 100}vw;
        background: ${this.colors[Math.floor(Math.random() * this.colors.length)]};
        width: ${4 + Math.random() * 8}px;
        height: ${4 + Math.random() * 8}px;
        border-radius: ${Math.random() > 0.5 ? '50%' : '2px'};
        --duration: ${1.5 + Math.random() * 2}s;
        --delay: ${Math.random() * 0.5}s;
      `;
      document.body.appendChild(piece);
      const dur = (parseFloat(piece.style.getPropertyValue('--duration')) +
                   parseFloat(piece.style.getPropertyValue('--delay'))) * 1000;
      setTimeout(() => piece.remove(), dur);
    }
  }
};

// ============ HERO PARTICLES ============
const HeroParticles = {
  init() {
    const hero = document.querySelector('.hero');
    if (!hero) return;

    const colors = ['rgba(99,102,241,0.4)', 'rgba(139,92,246,0.3)', 'rgba(16,185,129,0.3)', 'rgba(59,130,246,0.3)'];

    for (let i = 0; i < 12; i++) {
      const p = document.createElement('div');
      p.className = 'particle';
      const size = 4 + Math.random() * 12;
      p.style.cssText = `
        width: ${size}px;
        height: ${size}px;
        background: ${colors[Math.floor(Math.random() * colors.length)]};
        left: ${Math.random() * 100}%;
        top: ${Math.random() * 100}%;
        --duration: ${5 + Math.random() * 8}s;
        --delay: ${-Math.random() * 5}s;
      `;
      hero.querySelector('.hero-bg-orbs')?.appendChild(p);
    }
  }
};

// ============ STAGGER CHILDREN ============
const StaggerChildren = {
  init() {
    document.querySelectorAll('[data-stagger]').forEach(container => {
      const delay = parseInt(container.dataset.stagger) || 100;
      Array.from(container.children).forEach((child, i) => {
        child.style.animationDelay = `${i * delay}ms`;
        child.classList.add('animate-fade-in-up');
      });
    });
  }
};

// ============ SMOOTH ANCHOR SCROLL ============
const SmoothScroll = {
  init() {
    document.querySelectorAll('a[href^="#"]').forEach(a => {
      a.addEventListener('click', (e) => {
        const id = a.getAttribute('href').slice(1);
        const target = document.getElementById(id);
        if (target) {
          e.preventDefault();
          const offset = document.querySelector('.navbar')?.offsetHeight || 70;
          window.scrollTo({
            top: target.offsetTop - offset - 16,
            behavior: 'smooth'
          });
        }
      });
    });
  }
};

// ============ FORM ENHANCEMENTS ============
const Forms = {
  init() {
    // Float label effect
    document.querySelectorAll('.form-control').forEach(input => {
      const checkValue = () => {
        input.parentElement?.classList.toggle('has-value', input.value.length > 0);
      };
      input.addEventListener('input', checkValue);
      checkValue();
    });

    // Auto-resize textarea
    document.querySelectorAll('textarea.form-control').forEach(ta => {
      ta.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
      });
    });
  }
};

// ============ LAZY IMAGES ============
const LazyImages = {
  init() {
    if (!('IntersectionObserver' in window)) {
      document.querySelectorAll('img[data-src]').forEach(img => {
        img.src = img.dataset.src;
      });
      return;
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
          img.classList.add('loaded');
          observer.unobserve(img);
        }
      });
    }, { rootMargin: '200px' });

    document.querySelectorAll('img[data-src]').forEach(img => observer.observe(img));
  }
};

// ============ INIT ALL ============
document.addEventListener('DOMContentLoaded', () => {
  ScrollReveal.init();
  Counter.init();
  ProgressBars.init();
  TypeWriter.init();
  HeroParticles.init();
  StaggerChildren.init();
  SmoothScroll.init();
  Forms.init();
  LazyImages.init();
});

// Export
window.LingvoAnimations = { Confetti, TypeWriter, Counter };
