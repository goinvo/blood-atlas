/* A concern seen as a system answers five questions, and every sentence it
 * shows is a quote with a source. The bugs this catches: a question that
 * renders with nothing under it, a quote that loses its source link, a test
 * row that does not open, a reader's own marks reported wrongly, and the
 * infection concern no longer leading to the immune view.
 *
 * What is expected comes from the build's payload (D.systems), not from
 * constants, so adding a system needs no change here. */
const fs = require('fs'), path = require('path'), { JSDOM } = require('jsdom');
const html = fs.readFileSync(path.join(__dirname, '..', '..', 'index.html'), 'utf8');
const fail = [];

const dom = new JSDOM(html, { url: 'http://localhost/', runScripts: 'dangerously', pretendToBeVisual: true,
 beforeParse(w){
  w.matchMedia = q => ({ matches: false, addEventListener(){}, addListener(){} });
  Object.defineProperty(w.HTMLElement.prototype, 'clientWidth',  { get(){ return 1440; } });
  Object.defineProperty(w.HTMLElement.prototype, 'clientHeight', { get(){ return 900; } });
 }});

setTimeout(() => {
 const w = dom.window, d = w.document, D = w.eval('D');
 const click = el => el.dispatchEvent(new w.MouseEvent('click', { bubbles:true, cancelable:true }));
 const pick = ci => { w.eval('st.sel = {t:"c", v:"' + ci + '"}; render();'); };
 const why = () => d.getElementById('why');
 const systems = Object.keys(D.systems || {});
 if (!systems.length) fail.push('the build carried no system view');

 systems.forEach(ci => {
  const sys = D.systems[ci], label = D.concerns[ci].label;
  pick(ci);
  const asks = [...why().querySelectorAll('.sys-q')].map(e => e.textContent.trim().toLowerCase());
  console.log(label + ':', asks.join(' / '));
  sys.questions.forEach(q => {
   if (asks.indexOf(q.ask.toLowerCase()) < 0) fail.push(label + ': question missing: ' + q.ask);
   const n = q.cite.length + (q.steps || []).reduce((a, s) => a + s.cite.length, 0);
   if (!n && !q.markers) fail.push(label + ': "' + q.ask + '" has neither a quote nor your markers under it');
  });
  // every quote carries its source link, and only quotes are set as quotes
  const quotes = why().querySelectorAll('q.sq');
  const sources = why().querySelectorAll('.sc a[href^="http"]');
  const want = sys.signs.length + sys.questions.reduce((a, q) => a + q.cite.length
              + (q.steps || []).reduce((b, s) => b + s.cite.length, 0), 0);
  console.log('  quotes', quotes.length, '/', want, '| source links', sources.length);
  if (quotes.length !== want) fail.push(label + ': ' + quotes.length + ' quotes drawn, ' + want + ' carried');
  if (sources.length !== quotes.length) fail.push(label + ': a quote is missing its source link');

  // your own markers: unmarked reads "not marked", a mark reads as marked
  const mk = sys.questions.find(q => q.markers);
  if (mk) {
   const sl = mk.markers[0];
   const row = () => why().querySelector('[data-mk="' + sl + '"] em');
   if (!row() || row().textContent !== 'not marked') fail.push(label + ': ' + sl + ' unmarked reads "' + (row() && row().textContent) + '"');
   w.eval('st.val["' + sl + '"] = -1; render();');
   if (!row() || row().textContent !== 'marked low') fail.push(label + ': ' + sl + ' marked low reads "' + (row() && row().textContent) + '"');
   w.eval('st.val["' + sl + '"] = 0; render();');
  }

  // a test in the view opens like any row of the follow-up list
  const t = why().querySelector('[data-test]');
  if (!t) fail.push(label + ': no test rows in the system view');
  else {
   const name = t.textContent.trim();
   click(t);
   const sel = w.eval('st.sel');
   const head = d.getElementById('dHead').textContent.trim();
   console.log('  opened', JSON.stringify(sel), '|', head);
   if (!sel || sel.t !== 't' || head !== name) fail.push(label + ': clicking "' + name + '" opened ' + head);
  }
 });

 // the concerns that lead to a system view do lead there
 Object.keys(D.sysFrom || {}).forEach(ci => {
  pick(ci);
  const b = why().querySelector('button[data-cn]');
  if (!b) { fail.push(D.concerns[ci].label + ': no way through to its system view'); return; }
  click(b);
  const now = w.eval('st.sel');
  console.log(D.concerns[ci].label, '->', D.concerns[now && now.v] && D.concerns[now.v].label);
  if (!now || String(now.v) !== String(D.sysFrom[ci].to)) fail.push(D.concerns[ci].label + ': the button did not open the system view');
 });

 console.log(fail.length ? '\nFAIL:\n - ' + fail.join('\n - ') : '\nALL PASS');
 if (fail.length) process.exitCode = 1;
}, 900);
