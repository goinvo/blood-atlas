/* The full catalogue as a view of the atlas.
 *
 * The full catalogue is not in index.html — the table fetches
 * data/catalogue.json on first open. This check feeds it the real file, then
 * asserts the tab switches views in place, the counts are the true totals, the
 * paging control states how much it is not showing, the filters work, and the
 * map comes back intact. */
const fs = require('fs'), path = require('path'), { JSDOM } = require('jsdom');
const ROOT = path.join(__dirname, '..', '..');
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const CAT = fs.readFileSync(path.join(ROOT, 'data', 'catalogue.json'), 'utf8');
let fetched = 0;

const dom = new JSDOM(html, { url: 'http://localhost/', runScripts: 'dangerously', pretendToBeVisual: true,
 beforeParse(w){
  w.matchMedia = q => ({ matches: false, addEventListener(){}, addListener(){} });
  Object.defineProperty(w.HTMLElement.prototype, 'clientWidth',  { get(){ return 1600; } });
  Object.defineProperty(w.HTMLElement.prototype, 'clientHeight', { get(){ return 900; } });
  w.fetch = u => { fetched++;
   return Promise.resolve({ ok:true, status:200, json:() => Promise.resolve(JSON.parse(CAT)) }); };
 }});

setTimeout(() => {
 const w = dom.window, d = w.document, fail = [];
 const click = el => el.dispatchEvent(new w.MouseEvent('click', { bubbles:true, cancelable:true }));
 const J = JSON.parse(CAT);
 // The true total is whatever the catalogue holds, so adding rows to it never
 // reads as a lie in this check.
 const TOTAL = J.tests.length.toLocaleString('en-US');

 // the atlas must not be carrying the catalogue
 const kb = Buffer.byteLength(html) / 1024;
 console.log('index.html', kb.toFixed(0) + 'KB', '| catalogue', (Buffer.byteLength(CAT)/1024).toFixed(0) + 'KB');
 if (kb > 1200) fail.push('index.html has grown past 1.2MB — is the catalogue embedded?');
 if (fetched) fail.push('the catalogue was fetched before the table was opened');

 const tab = d.querySelector('.sitehd [data-view2="table"]');
 console.log('tab present:', !!tab, '| in-page:', tab && tab.getAttribute('href') === '#table');
 if (!tab) fail.push('no All tests tab on the atlas');

 click(tab);
 setTimeout(() => {
  console.log('fetches:', fetched, '| body:', d.body.className, '| hash:', w.location.hash);
  if (fetched !== 1) fail.push('expected exactly one fetch, got ' + fetched);
  if (!d.body.classList.contains('view-table')) fail.push('the tab did not switch to the table');

  // Each catalogue row now carries a second, hidden <tr> beside it — the
  // nested sourcing detail toggled open by clicking the row. Only the
  // visible `.trow` rows count as "drawn"; the paired `.tdet` rows are not
  // a second page of results.
  const rows = () => d.querySelectorAll('#tbody tbody tr.trow').length;
  const count = () => d.getElementById('tcount').textContent;
  console.log('count:', count(), '| rows drawn:', rows());
  if (count() !== TOTAL + ' tests') fail.push('the count is not the true total: ' + count());
  if (rows() !== 200) fail.push(rows() + ' rows drawn, expected the first 200');
  const more = d.getElementById('tmore');
  console.log('paging:', more && more.textContent);
  if (!more || more.textContent.indexOf('of ' + TOTAL + ' shown') < 0)
   fail.push('the paging control does not state the true total');
  click(more);
  console.log('after Show more:', rows());
  if (rows() !== 400) fail.push('Show more did not add a page');

  // every column carries something
  const cells = [...d.querySelector('#tbody tbody tr').children].map(td => td.textContent.trim());
  console.log('columns:', cells.map(c => c.slice(0, 24)).join(' | '));
  if (cells.length !== 5) fail.push('expected five columns');
  if (!/quoted|ai-written/.test(cells[2])) fail.push('the description does not say where it came from');

  // filters
  const f = d.getElementById('tqf');
  f.value = 'ferritin'; f.dispatchEvent(new w.Event('input', { bubbles:true }));
  console.log('filter "ferritin":', count(), '| rows', rows());
  if (!count().endsWith('of ' + TOTAL + ' tests')) fail.push('a filtered count does not state the total');
  if (!rows()) fail.push('the name filter found nothing');
  f.value = ''; const v = d.getElementById('tqv');
  v.value = '1'; v.dispatchEvent(new w.Event('input', { bubbles:true }));
  const quoted = J.tests.filter(t => t.v).length;
  console.log('source-quoted only:', count(), '| expected', quoted);
  if (count().indexOf(String(quoted).replace(/\B(?=(\d{3})+(?!\d))/g, ',')) !== 0)
   fail.push('the quoted-only count does not match the data');

  // and back — the map starts with no panel active, so "it came back" is
  // checked by the always-drawn concerns column, not by markers
  click(d.querySelector('.sitehd [data-view2="map"]'));
  console.log('back to the map: concerns', d.querySelectorAll('.map .row.cnc').length);
  if (d.body.classList.contains('view-table')) fail.push('the logo/Atlas link did not switch back');
  if (!d.querySelectorAll('.map .row.cnc').length) fail.push('the map did not come back');

  console.log(fail.length ? '\nFAIL:\n - ' + fail.join('\n - ') : '\nALL PASS');
  if (fail.length) process.exitCode = 1;
 }, 400);
}, 800);
