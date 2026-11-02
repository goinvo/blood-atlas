# Design rules

Standing rules for this project. They apply to every build, at every level of
the design — not just the outer layout.

---

## 1. The 8px system — everywhere

**Every spacing value is a multiple of 8.** Padding, margin, gap, row height,
panel height, column width, offsets. 4px is permitted as a deliberate half-step
for tight inline cases (a badge's vertical padding, a 4px label gap); anything
else is a mistake.

Not on the system, and correctly so:

- **1px borders and rules.** A hairline is a hairline.
- **Font sizes and line-heights.** Type is sized for reading, not for the grid.
  A 24px row can carry 11px text.
- **Border radii.** Follow the shape, not the grid.
- **Percentages and fractions** used for proportional layout.

Reference values in use:

| | |
|---|---|
| Base unit | 8px |
| Panel gap / outer margin | 16px |
| Panel padding | 16px |
| Section header padding | 16px 16px 8px |
| List row height | 32px |
| Control height | 24px |
| Control inner padding | 0 8px |
| Chip padding | 4px 8px |
| Map row pitch | 24px |
| Left rail width | 320px (8×40) |
| Toggle column | 96px (8×12) |
| Detail panel width | 344px |
| Header height | 56px |
| Footer height | 72px |

Audit the CSS before shipping. `pipeline/build_v3.py` builds are checked with:

```python
# flags any padding/margin/gap/height that is not a multiple of 8 (or 4)
import re
for m in re.finditer(r'([\w.#>\-\s,:\[\]()="]+)\{([^}]*)\}', css):
    for pm in re.finditer(r'\b(padding|margin|gap|height|min-height|max-height)\s*:\s*([^;]+)', m.group(2)):
        for num in re.findall(r'(?<![\w.])(\d+(?:\.\d+)?)px', pm.group(2)):
            n = float(num)
            if n and n % 8 and n % 4:
                print('off-grid:', m.group(1), pm.group(1), num)
```

---

## 1b. The type scale

**12px is the floor for anything read as content** — names, values, sentences,
chips, buttons. Nothing that carries meaning on its own is smaller.

**10px is reserved for component labels**: mono, uppercase, tracked text that
names the thing below it rather than being part of it — column titles, group
headers, section kickers, the quoted/ai-written tags, the divider band. They are
signposts, and a signpost may be quieter than what it points at. If a label is
sentence-case, or is content in its own right, it is not one of these.

**Sizes go up in steps of 2px**: 10, 12, 14, 16, 18, 20. In use: 10 for
component labels, 12 for everything else, 16 for a section head, 18 for a panel
title, 20 for the app title.

**Line height on the map is 16px** for content and 12px for the 10px labels, and
the shortest a content row can be is 16px.

A floor this high costs room, and that cost is paid in height, not in type or in
content: the canvas grows and scrolls (see §6). Type size is never the variable
that absorbs a small window, and neither is the number of rows.

## 2. Nothing shifts under the cursor

Interacting with the page must not move anything already on screen.

- Column and panel positions are constants, not functions of state.
- Panels hold their size; content that could overflow scrolls **inside its own
  box** rather than growing the box.
- Scroll areas reserve their gutter (`overflow-y: scroll; scrollbar-gutter: stable`)
  so a scrollbar appearing never nudges content sideways.
- Layout is a pure function of state and window size — same inputs, same pixels.

The map is the exception that proves it: it is a box that scrolls its own
content. It can be taller than the window, but its edges never move, its column
titles are pinned in a band above it, and the panels around it do not travel
with it.

The other deliberate exception: a section explicitly labelled as expandable,
where the user asked for the growth.

The first-run tutorial needs no exception at all: it is an **overlay**. The card
floats, a ring is drawn around the section the current step is about, and the
rest dims behind it — all `position: fixed`, all measured from the real layout,
none of it reserving a pixel.

**The guide is per visit.** Every load opens at step 1, and finishing or skipping
it lasts for that visit only — nothing about it is written to storage. Each step
ticks on the *action*, never on state left over from last time: marks do persist,
so inferring step 1 from them would have reopened the tutorial half-finished.

A scrim must never swallow a click. Every part of the overlay except the card
itself is `pointer-events: none`, so the reader can do anything at any time,
including ignoring the step they are on.

## 3. No ambient motion

Nothing drifts, floats, breathes or animates on its own. A diagram that moves is
harder to read than one that does not. Motion is allowed only under §3b.

## 3b. Motion explains a change you caused

*Proposed in the motion-guidance PR; replaces "transitions are for colour and
opacity on direct interaction".*

Motion may show **how the page got from what it was to what it is now**, right
after the reader did something. It never decorates, never loops, and never
carries information the still page does not.

- **The end state is drawn first.** `render()` draws the result; motion only
  animates the way in. With motion off the page is identical, arrived at
  instantly. `pipeline/tests/motion.js` compares the two.
- **Cause, then effect.** Marking a result draws its lines from the marker,
  lights each concern as its line arrives, then the follow-ups. The order is
  the explanation: it is how the map is read.
- **Things that move to a new place travel there.** A concern you pick carries
  its name into the panel header, so the eye follows it instead of hunting.
  The travelling copy is a decoration: `aria-hidden`, no pointer events, gone
  when it lands.
- **Short.** Under half a second for any one change. A whole upload or a clear
  is too much to stage: it gets one fade.
- **The reader decides.** The header's Motion control: *auto* follows the
  system's reduce-motion setting; *full*; *reduced* keeps fades and drops
  anything that travels or draws; *off* is instant, colour transitions included.
  The intro follows the same setting.

The first frame (§5b2) uses the same idea without motion: with nothing marked,
added or picked, the concern column steps back to 40% so your own markers are
read first. Every concern is still drawn and readable, and the frame ends the
moment you mark or pick anything.

## 4. State is colour, not geometry

Selection, hover and focus change **colour and opacity only**. They never change
a line's weight, a dot's radius, a row's height or a label's size. (A transition
under §3b can travel on the way to a state; the state it lands in is still
colour, not geometry.)

Two reasons. A drawing whose geometry moves with state is a different drawing
each time you look at it, which is rule 2 in another guise. And weight is a
scarce channel: if hovering makes a line thicker, thickness can no longer mean
anything else — a reader comparing a teal edge to an orange one is reading a
difference that isn't there.

Every marked edge in the map is 1.6px, whatever its state.

## 5. The row is the button

Any row that does something is clickable across its whole width — label, badges,
counts, and the padding around them. The interactive element carries the data
attribute; text inside it is a `span`, not a nested button or link.

A row that fills on hover needs no underline. One signal per meaning.

A selected row is a fill, not a fill plus a border. Where rows are separated by
hairlines, the selected row hides its own and its neighbour's so the fill reads
as one uninterrupted block.

## 6. Reveal, don't clip

**Names are shown in full.** A label wraps onto as many rows as it needs; it is
never cut with an ellipsis while there is a way to wrap it. Truncation is a last
resort for when the container genuinely cannot hold the text at the minimum
type size, and even then the full name stays in the tooltip.

**Padding is constant regardless of line count.** An entry with a three-line
name carries exactly the same space above and below as a one-line one — the row
grows, the padding does not change. Rows in a list may therefore have different
heights; that is correct.

If a section's job is to explain something, it grows to fit its content rather
than scrolling or truncating it. Long *lists* may be capped with an explicit
expander that states the true total. Truncation without a stated count is never
acceptable.

**Long lists are grouped, not cut.** Past about ten entries, group by a
meaningful axis, show the commonly-relevant members by default, and put the true
count on every group header so nothing is hidden without being counted.

**Text never runs under a panel.** Every column measures its available width
from the nearest panel edge minus the constant 16px gutter, and wraps to that
width — at every window size, in every column, for every label. A name with no
space in it (`Gamma glutamyl transferase.macromolecular`) is broken at a natural
boundary — `.` `+` `/` `-` `,` — or hard if there is none. Nothing is allowed to
overflow its column and slide under the panel beside it. Verify by measurement,
not by eye: the regression checks the right edge of the widest label against the
gutter at six window sizes.

**When it will not fit, the canvas grows and scrolls.** Not smaller type, not
fewer rows, not a roll-up. Every marker and every concern has its own row at
every window size; when there are more of them than the window is tall, the map
becomes taller than the window and scrolls inside its own box. Rolling content
up to save space hides it behind a gesture nobody knows to make.

The panels do not scroll with it — the map is the box that scrolls, and its
column titles sit in a fixed band above it so scrolling never takes the headings
away.

## 5b. Even spacing within a column

Rows in a column may differ in height — a two-line name is taller than a
one-line one — but **the gap between one row's text and the next is a constant**
down the whole column.

**Spare height goes between the boxes, never inside them.** A row's highlight is
the lines it carries plus 8px above and below — the same box in every column, at
every window size, whatever the window height. Growing the highlight to absorb
leftover space makes the padding around a name a function of how much room the
column happens to have, which is how three columns end up looking like three
different components.

The failure mode is sharing leftover height *in proportion* to each row: a
two-line row then gets twice the breathing room of a one-line row and the column
reads as ragged. Share it as the same number of pixels added to every row.

Where two columns are set at one type size, both must be *measured* at that
size. Measuring a column at 12px and drawing it at 11px silently reintroduces
uneven gaps, because the wrapping that was budgeted for is not the wrapping that
gets drawn.

**Columns are equal, and so are the gaps between them.** Three columns divide
the free width into thirds separated by one constant gap (40px). A consequence
worth stating on its own: the two runs of edges then span the same distance, and
the dots that begin and end each run are evenly spaced.

**Headings share one baseline across the whole screen**, panel and canvas alike.
A column title on the map sits on the same baseline as the panel kicker beside
it. This only holds if the panel's own heading is pinned to the top of its box
rather than centred in it — centred text moves with its content.

Titles are short. A heading competes with the names below it for the same
column width, and the names need it more.

**Panel headers are one object.** Every panel header is the same thing in the
same box: a mono kicker, a serif title, one short line under it, 16px padding,
96px minimum height. Two panels side by side are then automatically in register.

## 5b2. Guidance, not gamification

A page about someone's blood may tell them **where to start and what to do
next**. It may not turn that into a game.

Allowed: a step list that ticks off what the reader actually did and deletes
itself when finished; worked examples they can load in one click, labelled as
examples; stating what their data cannot reach; **a first frame that shows less
than the full picture, provided it is a frame and not a mode** — it must end on
its own, and the way to the whole thing must be visible while it lasts.

Not allowed, and the reasons matter:

- **Points, XP, levels** — rewards engagement with a medical record. Success is
  that someone comes once, understands something, and leaves.
- **Streaks, daily check-ins** — bloodwork changes over months. A streak would
  manufacture anxiety and reward re-reading old results.
- **Badges for tests taken** — makes ordering more tests an achievement.
  Overtesting has real costs: false positives, incidental findings, money.
- **Leaderboards or comparison to others** — reference ranges already are
  population comparison, and they are age- and sex-dependent.
- **A single health score** — collapsing 68 markers into one number is the exact
  reduction this product exists to argue against.
- **Celebration animation** — breaks §3, and there is nothing here to celebrate.
- **Unlocking content by progress** — never gate clinical information behind a
  game loop.

If a mechanic would still make sense with the word "health" removed from the
product, it is probably fine. If it only makes sense because someone is anxious
about their body, it is not.

## 5c. No decoration

Nothing is applied for atmosphere. No drop shadows, no background blur, no
translucent panels, no gradients. A panel is a white box with a 1px border.

Every visual property should be answerable with what it tells the reader. If the
answer is "it looks nicer", remove it.

## 7. Sourcing

- No hallucination. Every claim carries a credible reference with a link.
- Quote the source verbatim; do not paraphrase it.
- Say what is quoted and what is generated, on the thing itself.
- State true totals even when showing a subset.

## 8. Style

Follow `goinvo-style-guide.md`. Palette, type and tone come from there.
