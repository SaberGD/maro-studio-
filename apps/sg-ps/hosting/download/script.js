'use strict';

const personas = {
  vector: {
    image: 'assets/screens/one-vector-20261117.jpg',
    alt: 'مساحة Vector في HORIX One، بتصميم ONE IDEA وأشكال فيكتور قابلة للتعديل',
    caption: 'ارسم شعارك، وابني هويتك. مسارات وأشكال ونصوص في مساحة Vector.'
  },
  pixel: {
    image: 'assets/screens/one-pixel-20261117.jpg',
    alt: 'نفس تصميم ONE IDEA بعد نقله من Vector إلى Pixel كطبقات أشكال داخل HORIX One',
    caption: 'نفس التصميم، في Pixel. اتنقل من Vector كطبقات أشكال علشان تكمّل شغلك.'
  },
  layout: {
    image: 'assets/screens/one-layout-20261117.jpg',
    alt: 'مثال المجلة المرفق بالبرنامج مفتوح داخل مساحة Layout في HORIX One',
    caption: 'مساحة للأفكار الأطول. مثال مجلة من Layout؛ مستند مستقل عن مثال Vector وPixel.'
  }
};

let currentPersona = 'vector';
const stage = document.querySelector('.product-stage');
const screen = document.querySelector('#hero-screen');
const panel = document.querySelector('#persona-panel');
const dialog = document.querySelector('.preview-dialog');
const mobileButton = document.querySelector('.mobile-menu');
const mobileNav = document.querySelector('.mobile-nav');

function closeMenu() {
  mobileNav.hidden = true;
  mobileButton.setAttribute('aria-expanded', 'false');
  mobileButton.setAttribute('aria-label', 'افتح القائمة');
}
mobileButton.addEventListener('click', () => {
  const expanded = mobileButton.getAttribute('aria-expanded') === 'true';
  mobileNav.hidden = expanded;
  mobileButton.setAttribute('aria-expanded', String(!expanded));
  mobileButton.setAttribute('aria-label', expanded ? 'افتح القائمة' : 'أغلق القائمة');
});
mobileNav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !mobileNav.hidden) {
    closeMenu();
    mobileButton.focus();
  }
});
window.matchMedia('(min-width: 851px)').addEventListener('change', event => {
  if (event.matches) closeMenu();
});

function selectPersona(id) {
  const persona = personas[id];
  if (!persona) return;
  currentPersona = id;
  screen.src = persona.image;
  screen.alt = persona.alt;
  document.querySelector('#persona-caption').textContent = persona.caption;
  panel.setAttribute('aria-labelledby', 'tab-' + id);
  document.querySelectorAll('[data-persona]').forEach(button => {
    const selected = button.dataset.persona === id;
    button.setAttribute('aria-selected', String(selected));
    button.tabIndex = selected ? 0 : -1;
  });
}
document.querySelectorAll('[data-persona]').forEach(button => {
  button.addEventListener('click', () => selectPersona(button.dataset.persona));
});
document.querySelectorAll('[data-show-persona]').forEach(button => {
  button.addEventListener('click', () => {
    selectPersona(button.dataset.showPersona);
    stage.scrollIntoView({ block: 'start', behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
    document.querySelector('#tab-' + currentPersona).focus({ preventScroll: true });
  });
});
document.querySelector('.expand-preview').addEventListener('click', () => {
  const persona = personas[currentPersona];
  const image = document.querySelector('#full-preview');
  image.src = persona.image;
  image.alt = persona.alt;
  document.querySelector('#full-preview-caption').textContent = persona.caption;
  dialog.showModal();
});
document.querySelector('.close-dialog').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => {
  if (event.target !== dialog) return;
  const rect = dialog.getBoundingClientRect();
  if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
});

function selectPlatform(id) {
  if (id !== 'windows' && id !== 'mac') return;
  document.querySelectorAll('[data-platform]').forEach(button => {
    const selected = button.dataset.platform === id;
    button.setAttribute('aria-selected', String(selected));
    button.tabIndex = selected ? 0 : -1;
  });
  document.querySelector('#panel-windows').hidden = id !== 'windows';
  document.querySelector('#panel-mac').hidden = id !== 'mac';
}
document.querySelectorAll('[data-platform]').forEach(button => {
  button.addEventListener('click', () => selectPlatform(button.dataset.platform));
});
document.querySelectorAll('[data-select-platform]').forEach(link => {
  link.addEventListener('click', () => selectPlatform(link.dataset.selectPlatform));
});
for (const selector of ['.persona-tabs', '.platform-tabs']) {
  const list = document.querySelector(selector);
  list.addEventListener('keydown', event => {
    const buttons = [...list.querySelectorAll('[role=tab]')];
    const current = buttons.indexOf(document.activeElement);
    if (current < 0) return;
    let next;
    if (event.key === 'ArrowRight') next = (current + 1) % buttons.length;
    else if (event.key === 'ArrowLeft') next = (current - 1 + buttons.length) % buttons.length;
    else if (event.key === 'Home') next = 0;
    else if (event.key === 'End') next = buttons.length - 1;
    else return;
    event.preventDefault();
    buttons[next].focus();
    buttons[next].click();
  });
}
const ua = navigator.userAgent || '';
if (/Macintosh/.test(ua) && !/Mobile/.test(ua) && !(navigator.maxTouchPoints > 1)) selectPlatform('mac');

// Keep release feeds and their static download fallbacks: the site never pins today's build.
const megabytes = bytes => (bytes / 1048576).toFixed(bytes < 10485760 ? 1 : 0) + ' MB';
fetch('launcher/release_info.json', { cache: 'no-store' })
  .then(response => response.ok ? response.json() : null)
  .then(data => {
    const release = data?.release_info?.apps?.['horix-launcher']?.latest_release;
    const asset = release?.assets?.find(item => item.name.endsWith('-windows-x64-portable.zip'));
    if (!asset) return;
    const url = new URL(asset.download_url, location.href);
    if (url.protocol !== 'https:') return;
    document.querySelector('#windows-download').href = url.href;
    document.querySelector('[data-windows-version]').textContent = 'Launcher v' + release.version + (asset.size_bytes ? ' · ' + megabytes(asset.size_bytes) : '');
  }).catch(() => {});
fetch('mac/latest.json', { cache: 'no-store' })
  .then(response => response.ok ? response.json() : null)
  .then(data => {
    if (!data) return;
    document.querySelectorAll('[data-mac-id]').forEach(link => {
      const file = data[link.dataset.macId];
      if (!file || !/^[-\w.]+\.dmg$/.test(file.file || '')) return;
      link.href = 'mac/' + encodeURIComponent(file.file) + '?v=' + encodeURIComponent(file.version);
      link.querySelector('[data-mac-size]').textContent = 'v' + file.version + (file.size ? ' · ' + megabytes(file.size) : '');
    });
  }).catch(() => {});

// The existing server-side waitlist endpoint and consent remain unchanged.
const form = document.querySelector('#waitlist-form');
const error = document.querySelector('#form-error');
const result = document.querySelector('.form-result');
form.addEventListener('submit', async event => {
  event.preventDefault();
  error.textContent = '';
  result.hidden = true;
  const name = form.elements.name.value.trim();
  const phone = form.elements.phone.value.trim();
  const digits = phone.replace(/\D/g, '');
  const products = [...form.querySelectorAll('[name=products]:checked')].map(box => box.value);
  if (!name) { error.textContent = 'اكتب اسمك الأول.'; form.elements.name.focus(); return; }
  if (digits.length < 8 || digits.length > 15) { error.textContent = 'اكتب رقم واتساب صحيح.'; form.elements.phone.focus(); return; }
  if (!products.length) { error.textContent = 'اختار مجال واحد على الأقل.'; form.querySelector('[name=products]').focus(); return; }
  if (!form.elements.consent.checked) { error.textContent = 'محتاجين موافقتك قبل التواصل على واتساب.'; form.elements.consent.focus(); return; }
  const button = form.querySelector('button[type=submit]');
  const label = button.innerHTML;
  button.disabled = true;
  button.textContent = 'جاري التسجيل…';
  try {
    const response = await fetch('waitlist.php', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, phone, products, interests: [], consent: true, page: location.pathname })
    });
    const body = await response.json().catch(() => null);
    if (response.ok && body?.ok) {
      [...form.children].forEach(child => {
        if (child !== result && !child.classList.contains('form-heading')) child.hidden = true;
      });
      result.hidden = false;
      result.tabIndex = -1;
      result.focus();
    } else if (response.status === 429) error.textContent = 'طلبات كتير من نفس الجهاز، جرّب كمان شوية.';
    else error.textContent = 'حصلت مشكلة في الإرسال، جرّب تاني.';
  } catch {
    error.textContent = 'مفيش اتصال بالإنترنت، جرّب تاني.';
  } finally {
    button.disabled = false;
    button.innerHTML = label;
  }
});
