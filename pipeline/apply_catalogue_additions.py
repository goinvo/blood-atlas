#!/usr/bin/env python3
"""
Applies data/catalogue-additions.json to data/catalogue.json.

The catalogue is a data file with no generator of its own, so changes to it
are written down here rather than hand-edited: the additions file says which
rows were added, which were corrected and why, and carries the source quote
behind each. Running this twice changes nothing.

    python3 pipeline/apply_catalogue_additions.py
    python3 pipeline/build_v3.py

Every quote must appear word for word in its page snapshot under
data/sources/ — the same check build_v3.py repeats — so a quote cannot be
paraphrased on its way into the catalogue.
"""
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(ROOT, "data", "catalogue.json")
ADD = os.path.join(ROOT, "data", "catalogue-additions.json")


def squash(t):
    # Stripping a page's tags leaves a space where a link ended ("bronchitis ."),
    # so spacing before punctuation is not part of the comparison.
    t = re.sub(r"\s+", " ", t)
    return re.sub(r" ([.,;:)])", lambda m: m.group(1), t).strip()


def check_quote(q):
    page = io.open(os.path.join(ROOT, "data", "sources", q["file"] + ".txt"), encoding="utf8").read()
    assert squash(q["q"]) in squash(page), "quote not found in %s: %r" % (q["file"], q["q"][:80])


def loinc_of(row):
    return next((u for u, label in row.get("r") or [] if label == "LOINC"), None)


cat = json.loads(io.open(CAT, encoding="utf8", newline="").read())
spec = json.loads(io.open(ADD, encoding="utf8").read())
tests = cat["tests"]

for row in spec["add"]:
    check_quote(row["_quote"])
    clean = {k: v for k, v in row.items() if not k.startswith("_")}
    at = next((i for i, t in enumerate(tests) if loinc_of(t) == loinc_of(clean)), None)
    if at is None:
        tests.append(clean)
    else:
        tests[at] = clean

for fix in spec["fix"]:
    if "_quote" in fix:
        check_quote(fix["_quote"])
    hits = [t for t in tests if t["n"] == fix["n"]]
    assert len(hits) == 1, "expected one catalogue row named %r, found %d" % (fix["n"], len(hits))
    t = hits[0]
    t.update(fix.get("set", {}))
    for k in fix.get("addk", []):
        if k not in t["k"]:
            t["k"].append(k)

meta = cat["meta"]
meta["total"] = len(tests)
meta["quoted"] = sum(1 for t in tests if t.get("v"))
meta["generated"] = meta["total"] - meta["quoted"]

# Same serialisation the file already uses, so a diff shows only real changes.
io.open(CAT, "w", encoding="utf8", newline="").write(json.dumps(cat, ensure_ascii=False, separators=(",", ":")))
print("catalogue.json: %d rows (%d quoted), %d added, %d corrected"
      % (meta["total"], meta["quoted"], len(spec["add"]), len(spec["fix"])))
