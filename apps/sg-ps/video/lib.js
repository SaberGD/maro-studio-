// Deterministic motion helpers: every frame is a pure function of time t (seconds).
window.E = {
  lin: (x) => x,
  outCubic: (x) => 1 - Math.pow(1 - x, 3),
  inCubic: (x) => x * x * x,
  inOutCubic: (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
  outExpo: (x) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x)),
  inOutExpo: (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x < 0.5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2),
  outBack: (x) => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); },
  outElastic: (x) => (x <= 0 ? 0 : x >= 1 ? 1 : Math.pow(2, -10 * x) * Math.sin((x * 10 - 0.75) * ((2 * Math.PI) / 3)) + 1),
};
window.clamp = (v, a, b) => Math.min(b, Math.max(a, v));
// Progress of t through [t0, t1], eased.
window.k = (t, t0, t1, ease) => (ease || E.outCubic)(clamp((t - t0) / (t1 - t0), 0, 1));
window.mix = (a, b, x) => a + (b - a) * x;
// In/out envelope: 0 before t0, rises over `inDur`, holds, falls over `outDur` before t1.
window.env = (t, t0, t1, inDur, outDur, eIn, eOut) =>
  Math.min(k(t, t0, t0 + (inDur || 0.4), eIn || E.outCubic), 1 - k(t, t1 - (outDur || 0.4), t1, eOut || E.inCubic));
window.$ = (s) => document.querySelector(s);
window.$$ = (s) => Array.from(document.querySelectorAll(s));
window.set = (el, o) => { if (typeof el === 'string') el = $(el); if (!el) return; for (const key in o) el.style[key] = o[key]; };
// Split an element's text into word spans for staggered reveals (Arabic must stay joined, so words, not letters).
window.splitWords = (el) => {
  // Arabic words animate one by one; a run of Latin words (e.g. "Select Subject") stays one
  // left-to-right unit so the bidi order is right.
  const isLatin = (w) => /^[A-Za-z0-9+.:\u203a&()\-\/·]+$/.test(w) && /[A-Za-z0-9]/.test(w);
  const words = el.textContent.trim().split(/\s+/);
  const units = [];
  for (const w of words) {
    const last = units[units.length - 1];
    if (isLatin(w) && last && last.latin) last.text += ' ' + w; else units.push({ text: w, latin: isLatin(w) });
  }
  el.innerHTML = units.map((u) => `<span class="w"${u.latin ? ' dir="ltr"' : ''}><span>${u.text}</span></span>`).join(' ');
  return Array.from(el.querySelectorAll('.w > span'));
};
window.splitChars = (el) => {
  const chars = Array.from(el.textContent);
  el.innerHTML = chars.map((c) => (c === ' ' ? ' ' : `<span class="c">${c}</span>`)).join('');
  return Array.from(el.querySelectorAll('.c'));
};
// Staggered word reveal: slide up from a mask with slight blur.
window.revealWords = (spans, t, t0, step, dur) => {
  spans.forEach((s, i) => {
    const x = k(t, t0 + i * step, t0 + i * step + (dur || 0.5), E.outExpo);
    s.style.transform = `translateY(${(1 - x) * 110}%)`;
    s.style.opacity = x;
  });
};
