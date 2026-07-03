/* ============ RUSTILI MAIN.JS ============ */
'use strict';

// ============ THEME ============
const ThemeManager = {
  init() {
    const saved = localStorage.getItem('rustili-theme') || 'light';
    this.set(saved);
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.addEventListener('click', () => this.toggle());
  },
  set(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('rustili-theme', theme);
    const icon = document.getElementById('theme-icon');
    if (icon) icon.textContent = theme === 'dark' ? '☀️' : '🌙';
  },
  toggle() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    this.set(current === 'dark' ? 'light' : 'dark');
  }
};

// ============ NAVBAR ============
const Navbar = {
  init() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    // Scroll effect
    const onScroll = () => {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    // Mobile menu
    const menuBtn = document.getElementById('mobile-menu-btn');
    const drawer = document.getElementById('mobile-drawer');
    const overlay = document.getElementById('mobile-overlay');

    if (menuBtn && drawer) {
      menuBtn.addEventListener('click', () => {
        menuBtn.classList.toggle('active');
        drawer.classList.toggle('open');
        document.body.style.overflow = drawer.classList.contains('open') ? 'hidden' : '';
      });

      if (overlay) {
        overlay.addEventListener('click', () => {
          menuBtn.classList.remove('active');
          drawer.classList.remove('open');
          document.body.style.overflow = '';
        });
      }
    }

    // Language switcher
    const langSwitcher = document.getElementById('lang-switcher');
    const langBtn = document.getElementById('lang-btn');
    if (langSwitcher && langBtn) {
      langBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        langSwitcher.classList.toggle('open');
      });
      document.addEventListener('click', (e) => {
        if (!langSwitcher.contains(e.target)) langSwitcher.classList.remove('open');
      });
    }

    // User menu
    const userMenu = document.getElementById('user-menu');
    const userTrigger = document.getElementById('user-menu-trigger');
    if (userMenu && userTrigger) {
      userTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        userMenu.classList.toggle('open');
      });
      document.addEventListener('click', (e) => {
        if (!userMenu.contains(e.target)) userMenu.classList.remove('open');
      });
    }
  }
};

// ============ TOAST ============
const Toast = {
  show(message, type = 'info', duration = 4000) {
    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || icons.info}</span>
      <span class="toast-message">${message}</span>
      <button onclick="this.closest('.toast').remove()" style="margin-left:auto;background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1rem;">×</button>
    `;

    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    container.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('removing');
      setTimeout(() => toast.remove(), 300);
    }, duration);

    return toast;
  }
};

// ============ MODAL ============
const Modal = {
  open(id) {
    document.getElementById(id)?.classList.add('active');
    document.body.style.overflow = 'hidden';
  },
  close(id) {
    document.getElementById(id)?.classList.remove('active');
    document.body.style.overflow = '';
  },
  closeAll() {
    document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
    document.body.style.overflow = '';
  }
};

// ============ API ============
const API = {
  async request(url, method = 'GET', data = null) {
    const options = {
      method,
      headers: {
        'X-CSRFToken': window.CSRF_TOKEN || document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    };
    if (data) options.body = JSON.stringify(data);
    const res = await fetch(url, options);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
  get: (url) => API.request(url),
  post: (url, data) => API.request(url, 'POST', data),
};

// ============ RIPPLE ============
const Ripple = {
  init() {
    document.querySelectorAll('.btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const rect = btn.getBoundingClientRect();
        const ripple = document.createElement('span');
        ripple.className = 'ripple-effect';
        ripple.style.cssText = `
          width: ${Math.max(rect.width, rect.height)}px;
          height: ${Math.max(rect.width, rect.height)}px;
          left: ${e.clientX - rect.left - rect.width / 2}px;
          top: ${e.clientY - rect.top - rect.height / 2}px;
        `;
        btn.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
      });
    });
  }
};

// ============ UTILS ============
const Utils = {
  debounce(fn, ms = 300) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), ms);
    };
  },

  formatNumber(n) {
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return n.toString();
  },

  getCookie(name) {
    return document.cookie.match(`(^|;)\\s*${name}\\s*=\\s*([^;]+)`)?.[2] || '';
  }
};

// ============ CLOSE MODAL ON OVERLAY CLICK ============
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) Modal.closeAll();
});

// ============ ESCAPE KEY ============
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    Modal.closeAll();
    document.getElementById('mobile-drawer')?.classList.remove('open');
    document.getElementById('mobile-menu-btn')?.classList.remove('active');
    document.body.style.overflow = '';
  }
});

// ============ INIT ============
document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();
  Navbar.init();
  Ripple.init();
});

// Export for templates
window.Rustili = { Toast, Modal, API, Utils, ThemeManager };
