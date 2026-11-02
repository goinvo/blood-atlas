# Regression gate

```
npm install jsdom          # once
node pipeline/tests/run.js
```

Renders the built `index.html` (and, for `header-parity`, `catalogue.html`) in jsdom.
The geometry checks seed `localStorage` to skip the first-run frame, so they measure
the full map — the demanding case. `guide` is the one that exercises the first frame at several window sizes and measures the
result. A non-zero exit means do not promote.

Every check here is a mistake that shipped once:

| check | what it measures | the bug it catches |
|---|---|---|
| `default-view` | all 26 markers and 47 concerns drawn, annual panel only | rows silently rolled up on the first screen |
| `rows-and-panels` | one Annual chip, a subset panel names its overlap, edge weights equal, rows clickable | Basic Metabolic Panel rendering an empty group |
| `picker-shortcuts` | annual-only / select-all, and what they do to the rail | a shortcut that dims but does not act |
| `clear-of-the-panel` | widest label's right edge vs the 16px detail-panel gutter, 6 sizes | names sliding under the panel |
| `clear-of-the-rail` | leftmost label vs the rail edge, 5 sizes | names sliding under the rail |
| `equal-thirds` | three equal columns, two equal gaps, titles on one baseline | columns drifting out of proportion |
| `even-spacing` | gap spread within each column ≤ 0.6px | leftover height shared in proportion, not equally |
| `row-padding` | box-top to first baseline, last baseline to box-bottom | padding that grows with the window |
| `no-overlapping-highlights` | highlight boxes never overlap, all 13 panels on | a row pitch shorter than its own highlight |
| `scrolling-canvas` | canvas grows past the window, 68 markers drawn | content hidden instead of scrolled |
| `column-band` | titles live in the fixed band, no inline font sizes in the SVG | headings scrolling away |
| `header-parity` | one 56px header on all four screens; identical `id \| nav \| act` grid shape and nav labels; current marked; every bound id intact; in-place route switch | headers drifting apart, nav pills landing at a different x per screen, or a rebuilt header orphaning the JS that binds to it |
| `guide` | overlay is `position:fixed` and reserves no canvas height; scrim and ring take no pointer events; ring matches the rail's box and the two map columns to the pixel; one task at 16px; steps tick on the real action; retires for good and is remembered | a tutorial that blocks clicks, drifts out of register with the columns it points at, reserves layout, or comes back after being finished |
| `guide-restarts` | two loads sharing one localStorage: a refresh opens at step 1, Skip lasts the visit only, nothing about the guide is written to storage | a tutorial that resumes mid-way, or one that vanishes for good after a single run |
| `no-landing` | catalogue.html with no hash, `#landing`, `#feel` and `#tests` all open a real view; the route chooser never appears | a front door that asks which door you want |
| `table-view` | the All tests tab switches view in place; the catalogue is fetched once and only on open; counts are the true totals; paging states what it is not showing; filters match the data; the map returns intact | a table that silently truncates, a count that lies, or the 2.8MB catalogue creeping into the front door |
| `system-view` | each system view draws all five questions, every quote with its source link, your own marks read back correctly, its tests open like list rows, and the concerns that lead to it do | a question with nothing under it, a quote that lost its source, a pointer to a view that does not open |
| `title-band` | band opaque and above the canvas, three titles in it, legend fully removed, counts moved to the header | a background painted with an undefined variable; dead layout reserved for a deleted panel |

The window size is stubbed through `clientWidth` / `clientHeight`, so these are
geometry checks, not screenshots — they fail with a number, not a judgement.
