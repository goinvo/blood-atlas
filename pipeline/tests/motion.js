/* Motion explains a change; it never changes the result. The same clicks are
 * made under every Motion setting and the page must end in the same place.
 * Beyond that:
 *   off      nothing animates, and transitions are switched off in CSS
 *   reduced  fades only: no keyframe moves, scales or draws a line
 *   auto     follows the system's reduce-motion setting
 *   full     lines draw, the picked concern's name travels, and the copy that
 *            travels is gone once it lands
 * And the first frame: the concern column is calm until something is marked,
 * then it is not. */
const fs = require('fs'), path = require('path'), { JSDOM } = require('jsdom');
const html = fs.readFileSync(path.join(__dirname, '..', '..', 'index.html'), 'utf8');
const fail = [];

function run(pref, systemReduces){
 return new Promise(done => {
  const calls = [];
  const dom = new JSDOM(html, { url: 'http://localhost/', runScripts: 'dangerously', pretendToBeVisual: true,
   beforeParse(w){
    w.matchMedia = q => ({ matches: !!systemReduces && /reduce/.test(q), addEventListener(){}, addListener(){} });
    Object.defineProperty(w.HTMLElement.prototype, 'clientWidth',  { get(){ return 1440; } });
    Object.defineProperty(w.HTMLElement.prototype, 'clientHeight', { get(){ return 900; } });
    if (pref) w.localStorage.setItem('atlas.motion', pref);
    // Web Animations is not in jsdom: record every call, and finish each one.
    w.Element.prototype.animate = function(frames, opts){
     const a = { onfinish: null, oncancel: null, cancel(){} };
     calls.push({ el: this, frames: frames, opts: opts });
     setTimeout(() => a.onfinish && a.onfinish(), 0);
     return a;
    };
    w.SVGElement.prototype.getTotalLength = function(){ return 100; };
   }});
  setTimeout(() => {
   const w = dom.window, d = w.document;
   const click = el => el && el.dispatchEvent(new w.MouseEvent('click', { bubbles:true, cancelable:true }));
   const out = { pref: pref || 'auto', calls: calls, motionAttr: d.documentElement.dataset.motion };
   out.calmAtStart = d.getElementById('map').classList.contains('calm');
   click(d.querySelector('#why [data-edit-toggle]'));
   const before = calls.length;
   click(d.querySelector('[data-set="wbc"][data-v="-1"]'));
   out.markCalls = calls.slice(before);
   out.calmAfter = d.getElementById('map').classList.contains('calm');
   const ci = Object.keys(w.eval('D').concerns).find(k => w.eval('D').concerns[k].id === 'immunodef');
   click(d.querySelector('#map .row.cnc[data-cn="' + ci + '"]'));
   setTimeout(() => {
    out.map = d.getElementById('map').innerHTML;
    out.why = d.getElementById('why').innerHTML;
    out.head = d.getElementById('dHead').textContent;
    out.ghosts = d.querySelectorAll('.ghostlab').length;
    out.offCss = /html\[data-motion="off"\][^{]*\{transition:none!important/.test(html);
    done(out);
   }, 60);
  }, 900);
 });
}

const moves = c => c.frames.some(f => f.transform || f.strokeDashoffset != null);

Promise.all([run('off'), run('reduced'), run(null, true), run('full'), run(null, false)]).then(([off, red, autoRed, full, autoFull]) => {
 [off, red, autoRed, full, autoFull].forEach(r => console.log((r.pref + (r === autoRed ? ' (system reduces)' : r === autoFull ? ' (system does not)' : '')).padEnd(28),
   'data-motion', r.motionAttr, '| animations', r.calls.length, '| moving', r.calls.filter(moves).length,
   '| calm', r.calmAtStart, '->', r.calmAfter, '| head', JSON.stringify(r.head)));

 if (off.calls.length) fail.push('off: ' + off.calls.length + ' animations ran');
 if (off.motionAttr !== 'off' || !off.offCss) fail.push('off: CSS transitions are not switched off');
 [red, autoRed].forEach(r => { const m = r.calls.filter(moves).length;
  if (m) fail.push(r.pref + ': ' + m + ' animations move or draw under reduced motion');
  if (!r.calls.length) fail.push(r.pref + ': reduced should still fade'); });
 if (autoRed.motionAttr !== 'reduced') fail.push('auto did not follow the system reduce-motion setting');
 if (autoFull.motionAttr !== 'full') fail.push('auto did not fall back to full when the system does not reduce');
 if (!full.markCalls.some(c => c.frames.some(f => f.strokeDashoffset != null))) fail.push('full: marking a result drew no line');
 if (!full.calls.some(c => c.el.className === 'ghostlab')) fail.push('full: the picked concern did not travel to the panel');
 if (full.ghosts) fail.push('full: ' + full.ghosts + ' travelling copies left on the page');
 [off, red, autoRed, full, autoFull].forEach(r => {
  if (!r.calmAtStart) fail.push(r.pref + ': the first frame is not calm');
  if (r.calmAfter) fail.push(r.pref + ': still calm after a result was marked');
  if (r.map !== off.map) fail.push(r.pref + ': the map ends differently from motion off');
  if (r.why !== off.why) fail.push(r.pref + ': the panel ends differently from motion off');
 });
 console.log(fail.length ? '\nFAIL:\n - ' + fail.join('\n - ') : '\nALL PASS');
 if (fail.length) process.exitCode = 1;
});
