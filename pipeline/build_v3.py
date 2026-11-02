#!/usr/bin/env python3
"""
Regenerates the data embedded in index.html — the ripple atlas, the front
door of the site — from data/catalogue.json.

index.html is hand-edited directly (markup, CSS, JS all live there); this
script only ever rewrites its one generated line, "const D = {...};", in
place. There is no separate template file to keep in sync — index.html is
both the source and the build target for everything except that one line.

Flow:  annual panel marker -> concerns it can represent -> tests that would
       follow it up, with sourced relationship notes on how markers connect.

Every relationship note in REL below is a verbatim quote from a page that was
actually fetched, with its URL. Nothing here is paraphrased or inferred.

    python3 pipeline/build_v3.py
"""
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, "data", "catalogue.json")
DST  = os.path.join(ROOT, "index.html")

# The catalogue is a data file, not a page. Nothing here reads a document
# that a build might later write.
D = json.loads(io.open(SRC, encoding="utf8").read())
TESTS, GROUPS, CONCERNS, CGROUPS, PANELS = D["tests"], D["groups"], D["concerns"], D["cgroups"], D["panels"]

def unquote(t):
    """Strip wrapping quote marks of any flavour.

    The catalogue stores descriptions already wrapped in quotes, and the panel
    renders them in a <q> element which adds its own — so the straight-quote
    strip we had left curly ones through and produced a doubled mark.
    """
    return (t or "").strip().strip('"\u201c\u201d\u2018\u2019\'').strip()



# ---------------------------------------------------------------------------
# 2. concerns, and the tests that would follow each one up
# ---------------------------------------------------------------------------
def analyte(name):
    """Collapse a LOINC long name to the thing being measured.

    LOINC carries one code per unit, specimen and method. The property sits in
    brackets — "Lead [Mass/volume] in Blood" — but the specimen and method are
    often bare text, so "Carboxyhemoglobin/Hemoglobin.total in Venous blood"
    and "... in Arterial blood" are two codes for one measurement. Stripping
    the bracket, the trailing "in <specimen>" and any "by <method>" leaves the
    analyte, which is what a reader means by "the test".
    """
    n = name.split("[")[0]
    n = re.sub(r"\s+by\s+.*$", "", n, flags=re.I)
    n = re.sub(r"\s+in\s+(?:the\s+)?[A-Z].*$", "", n)
    return n.strip(" /,") or name.strip()


# ---------------------------------------------------------------------------
# PANEL LIBRARY
#
# Each panel carries a verbatim description and component list from a named
# source. Components are matched to the catalogue by LOINC analyte name; a
# component the catalogue does not carry is kept with missing=1 and shown as
# such, because a panel we cannot fully model is itself worth knowing about.
# ---------------------------------------------------------------------------
MPLUS = "MedlinePlus (NIH)"
# Not a published panel definition — one person's report, transcribed.
MINE  = "Your own annual panel report"
CLEVE = "Cleveland Clinic"

LABCORP = "Labcorp test directory"
QUEST   = "Quest Diagnostics"
ARUP    = "ARUP Laboratories"

PANEL_DEFS = [
 # ---- the report, section by section, exactly as printed -------------------
 {"id":"MYHEM", "name":"Hematology", "short":"Hematology", "src":MINE, "default":1, "grp":"ANNUAL",
  "url":"",
  "quote":"Transcribed from your own annual panel report, section \u201cHematology\u201d.",
  "comp":[("WBC","White Blood Cell count"),("RBC","Erythrocytes"),
          ("Hemoglobin","Hemoglobin"),("Hematocrit","Hematocrit"),
          ("MCV, MCH, MCHC","Red Blood Cell indices"),
          ("RDW","Erythrocyte distribution width"),
          ("Platelet Count","Platelet count")]},

 {"id":"MYDIFF", "name":"Differential", "short":"Differential", "src":MINE, "default":1, "grp":"ANNUAL",
  "url":"",
  "quote":"Transcribed from your own annual panel report, section \u201cDifferential\u201d.",
  "comp":[("Neutrophils","Neutrophils"),("Lymphocytes","Lymphocytes"),
          ("Monocytes","Monocytes"),("Eosinophils","Eosinophils"),
          ("Basophils","Basophils"),
          ("Immature Granulocytes",None),
          ("Nucleated RBC","Nucleated erythrocytes")]},

 {"id":"MYANEM", "name":"Biochemical investigation of anemias", "short":"Anemia workup",
  "src":MINE, "default":1, "grp":"ANNUAL", "url":"",
  "quote":"Transcribed from your own annual panel report, section \u201cBiochemical Investigation of Anemias\u201d.",
  "comp":[("Vitamin B12","Vitamin B12"),("Ferritin","Ferritin")]},

 {"id":"MYCHEM", "name":"General chemistry", "short":"Chemistry", "src":MINE, "default":1, "grp":"ANNUAL",
  "url":"",
  "quote":"Transcribed from your own annual panel report, section \u201cGeneral Chemistry\u201d.",
  "comp":[("Glucose (Random)","Blood glucose"),("Hemoglobin A1c","Hemoglobin A1c"),
          ("Sodium","Sodium [Moles/volume] in Serum or Plasma"),
          ("Potassium","Potassium [Moles/volume] in Serum or Plasma"),
          ("Chloride","Chloride [Moles/volume] in Serum or Plasma"),
          ("Creatinine","Creatinine"),
          ("Glomerular Filtration Rate (eGFR)","Glomerular filtration rate"),
          ("Urate","Uric acid"),("Albumin","Albumin"),
          ("Bilirubin Total","Bilirubin"),
          ("Alkaline Phosphatase","Alkaline phosphatase"),
          ("Alanine Aminotransferase","Alanine aminotransferase")]},

 {"id":"MYMUSC", "name":"Muscle enzymes", "short":"Muscle", "src":MINE, "default":1, "grp":"ANNUAL",
  "url":"",
  "quote":"Transcribed from your own annual panel report, section \u201cMuscle Enzymes\u201d.",
  "comp":[("Creatine Kinase","Creatine kinase")]},

 {"id":"MYLIP", "name":"Lipids", "short":"Lipids", "src":MINE, "default":1, "grp":"ANNUAL",
  "url":"",
  "quote":"Transcribed from your own annual panel report, section \u201cLipids\u201d.",
  "comp":[("Triglyceride","Triglycerides"),("Cholesterol","Total cholesterol"),
          ("HDL Cholesterol","HDL cholesterol"),
          ("Non HDL Cholesterol","Cholesterol non HDL"),
          ("LDL Cholesterol","LDL cholesterol"),
          ("Cholesterol/HDL Ratio","Cholesterol.total/Cholesterol")]},

 {"id":"MYTHY", "name":"Thyroid function", "short":"Thyroid", "src":MINE, "default":1, "grp":"ANNUAL",
  "url":"",
  "quote":"Transcribed from your own annual panel report, section \u201cThyroid Function\u201d.",
  "comp":[("Thyroid Stimulating Hormone","Thyroid-stimulating hormone"),("Free T4","Thyroxine (Free T4)")]},

 {"id":"MYBONE", "name":"Bone markers", "short":"Bone", "src":MINE, "default":1, "grp":"ANNUAL",
  "url":"",
  "quote":"Transcribed from your own annual panel report, section \u201cBone Markers\u201d.",
  "comp":[("25-Hydroxy Vitamin D","Vitamin D (25-hydroxyvitamin D)")]},

 # ---- the published definition of a routine checkup, kept for comparison ---
 {"id":"CBC", "name":"Complete Blood Count", "short":"CBC", "src":MPLUS, "default":0,
  "url":"https://medlineplus.gov/lab-tests/complete-blood-count-cbc/",
  "quote":"A complete blood count is often part of a routine checkup.",
  "comp":[("Red Blood Cell count","Red Blood Cell count"),("White Blood Cell count","White Blood Cell count"),
          ("Platelet count","Platelet count"),("Hemoglobin","Hemoglobin"),("Hematocrit","Hematocrit"),
          ("Red Blood Cell indices","Red Blood Cell indices"),("Complete Blood Count","Complete Blood Count")]},

 {"id":"CMP", "name":"Comprehensive Metabolic Panel", "short":"CMP", "src":MPLUS, "default":0,
  "url":"https://medlineplus.gov/lab-tests/comprehensive-metabolic-panel-cmp/",
  "quote":"A comprehensive metabolic panel (CMP) is a group of routine blood tests that measures 14 different substances in a sample of your blood.",
  "comp":[("Blood glucose","Blood glucose"),("Calcium","Calcium"),("Sodium","Sodium"),("Potassium","Potassium"),
          ("Bicarbonate","Bicarbonate"),("Chloride","Chloride"),("Albumin","Albumin"),("Total protein","Total protein"),
          ("Alkaline phosphatase","Alkaline phosphatase"),("Alanine aminotransferase","Alanine aminotransferase"),
          ("Aspartate aminotransferase","Aspartate aminotransferase"),("Bilirubin","Bilirubin"),
          ("Blood Urea Nitrogen","Blood Urea Nitrogen"),("Creatinine","Creatinine")]},

 {"id":"LIPID", "name":"Cholesterol / lipid panel", "short":"Lipids", "src":MPLUS, "default":0,
  "url":"https://medlineplus.gov/lab-tests/cholesterol-levels/",
  "quote":"Younger adults should have the test every 5 years. Men ages 45 to 65 and women ages 55 to 65 should have it every 1 to 2 years.",
  "comp":[("Total cholesterol","Total cholesterol"),("LDL cholesterol","LDL cholesterol"),
          ("HDL cholesterol","HDL cholesterol"),("Triglycerides","Triglycerides"),
          ("Lipid panel (cholesterol)","Lipid panel (cholesterol)")]},

 {"id":"BMP", "name":"Basic Metabolic Panel", "short":"BMP", "src":MPLUS, "default":0,
  "url":"https://medlineplus.gov/lab-tests/basic-metabolic-panel-bmp/",
  "quote":"A basic metabolic panel (BMP) measures eight different substances in your blood. It provides important information about your body's fluid balance, your metabolism (the process your body uses to make energy from food you eat), and how well your kidneys are working.",
  "comp":[("Blood glucose","Blood glucose"),("Calcium","Calcium"),("Sodium","Sodium"),("Potassium","Potassium"),
          ("Bicarbonate","Bicarbonate"),("Chloride","Chloride"),
          ("Blood Urea Nitrogen","Blood Urea Nitrogen"),("Creatinine","Creatinine")]},

 {"id":"LIVER", "name":"Liver function panel", "short":"Liver", "src":MPLUS, "default":0,
  "url":"https://medlineplus.gov/lab-tests/liver-function-tests/",
  "quote":"Liver function tests (also called a liver panel) use a sample of your blood to measure several substances made by your liver.",
  "comp":[("Albumin","Albumin"),("Total protein","Total protein"),("Alkaline phosphatase","Alkaline phosphatase"),
          ("Alanine aminotransferase","Alanine aminotransferase"),("Aspartate aminotransferase","Aspartate aminotransferase"),
          ("Gamma-glutamyl transferase","Gamma-glutamyl transferase"),("Bilirubin","Bilirubin"),
          ("Lactate dehydrogenase","Lactate dehydrogenase"),("Prothrombin Time / INR","Prothrombin Time / INR")]},

 {"id":"IRON", "name":"Iron studies", "short":"Iron", "src":MPLUS, "default":0,
  "url":"https://medlineplus.gov/lab-tests/iron-tests/",
  "quote":"Iron tests measure different substances in the blood to check iron levels in your body.",
  "comp":[("Serum iron","Iron"),("Transferrin","Transferrin"),
          ("Total iron-binding capacity","Iron binding capacity"),("Ferritin","Ferritin")]},

 {"id":"THYROID", "name":"Thyroid panel", "short":"Thyroid", "src":CLEVE, "default":0,
  "url":"https://my.clevelandclinic.org/health/diagnostics/thyroid-panel",
  "quote":"A thyroid panel measures the hormones made by your thyroid gland and antibodies that might affect thyroid function.",
  "comp":[("TSH (thyroid-stimulating hormone)","Thyroid-stimulating hormone"),
          ("T3 or free T3 (triiodothyronine)","Triiodothyronine (Free T3)"),
          ("T4 or free T4 (thyroxine)","Thyroxine (Free T4)"),
          ("Tg (thyroglobulin)","Thyroglobulin"),
          ("TPO (thyroid peroxidase antibodies)",None),
          ("Tg Ab (thyroglobulin antibodies)",None),
          ("TSI (thyroid-stimulating immunoglobulin)",None)]},

 {"id":"ENA", "name":"ENA panel (autoimmune)", "short":"ENA", "src":CLEVE, "default":0,
  "url":"https://my.clevelandclinic.org/health/diagnostics/ena-panel",
  "quote":"An ENA (extractable nuclear antigen) panel is a blood test that looks for antibodies that cause your immune system to attack healthy parts of your body. It can help your healthcare provider diagnose or rule out autoimmune diseases.",
  "comp":[("Anti-SSA","Sjogrens syndrome-A extractable nuclear Ab"),
          ("Anti-SSB","Sjogrens syndrome-B extractable nuclear Ab"),
          ("Anti-Smith","Smith extractable nuclear Ab"),
          ("Anti-RNP","Ribonucleoprotein extractable nuclear Ab"),
          ("Anti-Scl-70","SCL-70 extractable nuclear Ab"),
          ("Anti-Jo-1","Jo-1 extractable nuclear Ab")]},
 {"id":"ANEMIA", "name":"Anemia Profile B", "short":"Anemia", "src":LABCORP, "default":0,
  "url":"https://www.labcorp.com/tests/042077/anemia-profile-b",
  "quote":"Test Includes: CBC with differential and platelet count; ferritin; folates (folic acid); iron; iron binding capacity; reticulocyte count; vitamin B12",
  "comp":[("CBC with differential and platelet count","Complete Blood Count"),("Ferritin","Ferritin"),
          ("Folates (folic acid)","Folate"),("Iron","Iron"),("Iron binding capacity","Iron binding capacity"),
          ("Reticulocyte count","Reticulocytes"),("Vitamin B12","Cobalamin")]},

 {"id":"HORMM", "name":"Testicular Function Profile I", "short":"Hormones (M)", "src":LABCORP, "default":0,
  "url":"https://www.labcorp.com/tests/035741/testicular-function-profile-i",
  "quote":"Test Includes: Follicle-stimulating hormone (FSH); luteinizing hormone (LH); prolactin; testosterone, total",
  "comp":[("Follicle-stimulating hormone (FSH)","Follitropin"),("Luteinizing hormone (LH)","Luteinizing hormone"),
          ("Prolactin","Prolactin"),("Testosterone, total","Testosterone")]},

 {"id":"HORMF", "name":"ReproSURE ovarian reserve", "short":"Hormones (F)", "src":LABCORP, "default":0,
  "url":"https://www.labcorp.com/tests/504295/reprosure-ovarian-reserve-profile",
  "quote":"ReproSURE\u2122 is a blood test comprised of Anti-M\u00fcllerian Hormone (AMH), Follicle Stimulating Hormone (FSH), and Estradiol designed to provide information about ovarian reserve.",
  "comp":[("Anti-Mullerian Hormone (AMH)","Mullerian inhibiting substance"),
          ("Follicle Stimulating Hormone","Follitropin"),("Estradiol","Estradiol / Estrogen")]},

 {"id":"AUTOI", "name":"Autoimmune and Inflammation Marker Panel", "short":"Inflammation", "src":QUEST, "default":0,
  "url":"https://www.questhealth.com/product/autoimmune-and-inflammation-marker-test-panel/18359M.html",
  "quote":"This blood test measures 7+ key markers related to autoimmune and inflammatory activity, including markers often considered in conditions such as rheumatoid arthritis, lupus, and psoriatic arthritis.",
  "comp":[("Antinuclear antibodies (ANA)","Nuclear Ab"),("Rheumatoid factor (RF)","Rheumatoid factor"),
          ("C-reactive protein (CRP)","C reactive protein"),
          ("Erythrocyte sedimentation rate (ESR)","Erythrocyte Sedimentation Rate"),
          ("Cyclic citrullinated peptides (CCP)",None),("Mutated citrullinated vimentin (MCV)",None),
          ("14-3-3 eta protein",None)]},

 {"id":"HCC", "name":"Hepatocellular Carcinoma Tumor Marker Panel", "short":"Cancer (HCC)", "src":ARUP, "default":0,
  "url":"https://ltd.aruplab.com/Tests/Pub/0081326",
  "quote":"Acceptable panel for surveillance and monitoring of hepatocellular carcinoma.",
  "comp":[("Alpha Fetoprotein Total","Alpha-fetoprotein (tumor marker)"),
          ("Alpha Fetoprotein L3 Pct",None),("Des-gamma-carboxy Prothrombin",None)]},
]

ABBR_HINT = {
 "redbloodcellcount":"RBC","whitebloodcellcount":"WBC","plateletcount":"PLT","hemoglobin":"Hgb",
 "hematocrit":"Hct","redbloodcellindices":"MCV","completebloodcount":"CBC","bloodglucose":"Glu",
 "calcium":"Ca","sodium":"Na","potassium":"K","bicarbonate":"HCO₃","chloride":"Cl","albumin":"Alb",
 "totalprotein":"TP","alkalinephosphatase":"ALP","alanineaminotransfe":"ALT","aspartateaminotran":"AST",
 "bilirubin":"TBIL","bloodureanitrogen":"BUN","creatinine":"Cr","totalcholesterol":"TC",
 "ldlcholesterol":"LDL","hdlcholesterol":"HDL","triglycerides":"TG","lipidpanelcholester":"Lipids",
 "gammaglutamyltransf":"GGT","lactatedehydrogenas":"LDH","prothrombintimeinr":"PT/INR",
 "serumiron":"Fe","transferrin":"Tf","totalironbindingcap":"TIBC","ferritin":"Ferr",
}

def slugify(t):
    return re.sub(r"[^a-z0-9]+", "", t.lower())[:19]

def pick(match):
    """Best catalogue row whose analyte name is `match`: source-quoted first,
    then the more commonly ordered, then the shortest name."""
    ml = match.lower()
    # An exact LOINC long name pins one code. Matching by analyte alone let
    # "Leukocytes" resolve to a cord-blood count and "Thyrotropin" to a
    # presence test, neither of which is what an annual panel measures.
    exact = [k for k, t in enumerate(TESTS) if t["n"].lower() == ml]
    if exact:
        return exact[0]
    hits = [k for k, t in enumerate(TESTS) if analyte(t["n"]).lower() == ml]
    if not hits:
        hits = [k for k, t in enumerate(TESTS) if analyte(t["n"]).lower().startswith(ml)]
    if not hits:
        return None
    hits.sort(key=lambda k: (-(TESTS[k].get("v") or 0), -(TESTS[k].get("t") or 0), len(TESTS[k]["n"])))
    return hits[0]

markers, PANEL_ORDER = {}, []
for pdef in PANEL_DEFS:
    slugs, nmiss = [], 0
    for disp, match in pdef["comp"]:
        sl = slugify(disp)
        if sl not in markers:
            if match is None:
                nmiss += 1
                markers[sl] = {"slug": sl, "name": disp, "abbr": ABBR_HINT.get(sl, disp[:5]),
                               "grp": "not in our catalogue", "k": [], "q": "", "qs": "",
                               "v": 0, "url": "", "missing": 1, "panels": []}
            else:
                k = pick(match)
                assert k is not None, "no catalogue row for %r (%s)" % (match, pdef["id"])
                t = TESTS[k]
                markers[sl] = {"slug": sl, "name": disp,
                               "abbr": ABBR_HINT.get(sl, (t.get("a") or disp)[:5]),
                               "grp": GROUPS[t["g"]], "k": t.get("k") or [], "q": unquote(t.get("q")),
                               "qs": t.get("qs") or "", "v": 1 if t.get("v") else 0,
                               "url": (t.get("r") or [["", ""]])[0][0], "loinc": t["n"],
                               "missing": 0, "panels": []}
        elif match is None:
            nmiss += 1
        markers[sl]["panels"].append(pdef["id"])
        slugs.append(sl)
    PANEL_ORDER.append({"id": pdef["id"], "name": pdef["name"], "short": pdef["short"],
                        "quote": pdef["quote"], "src": pdef["src"], "url": pdef["url"],
                        "grp": pdef.get("grp"), "slugs": slugs,
                        "nMissing": nmiss, "default": pdef["default"]})

# Your annual panel is an adult's blood draw. A marker that resolves to a
# newborn or non-blood specimen, or to a yes/no presence test, is the wrong
# code: it gives the marker the wrong meaning and the wrong edges on the map
# (WBC once read "Measures Leukocytes in cord blood" and pointed at pregnancy).
WRONG_FOR_ANNUAL = re.compile(r"Cord blood|Urine|Cerebral spinal fluid|Body fluid|Amniotic|\[Presence\]", re.I)
for pdef in PANEL_DEFS:
    if pdef.get("grp") != "ANNUAL":
        continue
    for disp, match in pdef["comp"]:
        loinc = markers[slugify(disp)].get("loinc") or ""
        assert not WRONG_FOR_ANNUAL.search(loinc), "annual marker %r maps to %r" % (disp, loinc)

base_idx = {k for k, t in enumerate(TESTS) if t.get("b")}
panel_concerns = sorted({c for m in markers.values() for c in m["k"]})

concerns = {}
for ci, c in enumerate(CONCERNS):
    tagged = [k for k, t in enumerate(TESTS) if ci in (t.get("k") or [])]
    outside = [k for k in tagged if k not in base_idx]
    outside.sort(key=lambda k: (-(TESTS[k].get("v") or 0), -(TESTS[k].get("t") or 0), len(TESTS[k]["n"])))
    # De-duplicate by analyte. LOINC carries one code per unit and method, so
    # "Lead [Presence] in Blood", "Lead [Mass/volume] in Blood" and
    # "Lead [Moles/volume] in Blood" are three rows for one test. Truncating at
    # the first "[" for display collapsed them into a list that read as
    # "Lead, Lead, Lead". Keep the best-ranked row per analyte and count the
    # rest as variants. `outside` is already in rank order, so the first
    # occurrence is the representative.
    byAnalyte = {}
    for k in outside:
        name = analyte(TESTS[k]["n"])
        if name in byAnalyte:
            byAnalyte[name]["nv"] += 1
            continue
        byAnalyte[name] = {
            "n": name,
            "a": TESTS[k].get("a") or "",
            "g": GROUPS[TESTS[k]["g"]],
            "v": 1 if TESTS[k].get("v") else 0,
            "u": (TESTS[k].get("r") or [["", ""]])[-1][0],
            "q": unquote(TESTS[k].get("q"))[:260],
            "qs": TESTS[k].get("qs") or "",
            "cs": TESTS[k].get("k") or [],
            "t": TESTS[k].get("t", 0),      # how commonly ordered: 18 common .. -3 obscure
            "nv": 1,
        }
    distinct = list(byAnalyte.values())

    # Family rollup over EVERY distinct marker, not just the carried top 40, so
    # the counts a reader sees are the true ones. `common` is the catalogue's
    # own ordering tier: 8 and above is a test a general clinician orders.
    fams, order_seen = {}, []
    for t in distinct:
        f = fams.get(t["g"])
        if not f:
            f = fams[t["g"]] = {"g": t["g"], "n": 0, "c": 0}
            order_seen.append(t["g"])
        f["n"] += 1
        if t["t"] >= 8:
            f["c"] += 1
    famList = sorted(fams.values(), key=lambda f: (-f["c"], -f["n"], f["g"]))

    concerns[ci] = {
        "id": c["id"], "label": c["label"], "grp": c["grp"],
        "inPanel": ci in panel_concerns,
        "nTagged": len(tagged),
        "nOutside": len(outside),        # LOINC rows outside the panel
        "nDistinct": len(distinct),      # distinct markers among them
        "from": [m["slug"] for m in markers.values() if ci in m["k"]],
        # 8 drawn on the map; up to 40 carried so the panel can expand.
        "next": distinct[:40],
        "fams": famList,
    }

# Hand-written "why this test" notes live in their own data file, so a rebuild
# carries them instead of wiping them. Each note names the row it belongs to;
# one that no longer finds its row fails the build rather than vanishing.
_NOTES = json.loads(io.open(os.path.join(ROOT, "data", "follow-up-notes.json"), encoding="utf8").read())
NOTES = _NOTES["notes"]
for c in concerns.values():
    pinned = _NOTES.get("order", {}).get(c["id"])
    if pinned:
        assert sorted(pinned) == sorted(t["n"] for t in c["next"]), "pinned order for %r no longer matches its rows" % c["id"]
        c["next"].sort(key=lambda t: pinned.index(t["n"]))
_rows = {(c["id"], t["n"]): t for c in concerns.values() for t in c["next"]}
for note in NOTES:
    row = _rows.get((note["concern"], note["test"]))
    assert row is not None, "follow-up note for %r / %r no longer matches a row" % (note["concern"], note["test"])
    row.update({k: note[k] for k in ("why", "whys", "whyu")})
for pin in _NOTES.get("tier", []):
    row = _rows.get((pin["concern"], pin["test"]))
    assert row is not None, "tier pin for %r / %r no longer matches a row" % (pin["concern"], pin["test"])
    row["t"] = pin["t"]

# ---------------------------------------------------------------------------
# SYSTEM VIEWS — a concern seen as a system (data/systems/*.json): what your
# panel already says, what it cannot, what to measure first, what can wait,
# and when you know enough. Every sentence shown is a quote, re-checked here
# against the page snapshot it was cut from, so it cannot drift into
# paraphrase. Tests are named by analyte and must resolve to rows this
# concern actually carries, so every one of them opens like any other row.
# ---------------------------------------------------------------------------
def squash(t):
    t = re.sub(r"\s+", " ", t)
    return re.sub(r" ([.,;:)])", lambda m: m.group(1), t).strip()

_PAGES = {}
def cited(q):
    if q["file"] not in _PAGES:
        _PAGES[q["file"]] = squash(io.open(os.path.join(ROOT, "data", "sources", q["file"] + ".txt"), encoding="utf8").read())
    assert squash(q["q"]) in _PAGES[q["file"]], "quote not in %s: %r" % (q["file"], q["q"][:80])
    return {"q": q["q"], "s": q["s"], "u": q["u"]}

CID = {c["id"]: ci for ci, c in concerns.items()}
SYSTEMS, SYSFROM = {}, {}
SYSDIR = os.path.join(ROOT, "data", "systems")
for fn in sorted(os.listdir(SYSDIR)):
    if not fn.endswith(".json"):
        continue
    sd = json.loads(io.open(os.path.join(SYSDIR, fn), encoding="utf8").read())
    ci = CID[sd["concern"]]
    rowat = {t["n"]: i for i, t in enumerate(concerns[ci]["next"])}
    def tests(names, _rowat=rowat, _fn=fn):
        for n in names:
            assert n in _rowat, "%s names %r, which %r does not carry" % (_fn, n, sd["concern"])
        return [_rowat[n] for n in names]
    qs = []
    for q in sd["questions"]:
        out = {"ask": q["ask"], "cite": [cited(c) for c in q.get("cite", [])]}
        if "markers" in q:
            for sl in q["markers"]:
                assert sl in markers, "%s names marker %r" % (fn, sl)
            out["markers"] = q["markers"]
        if "tests" in q:
            out["tests"] = tests(q["tests"])
        if "steps" in q:
            out["steps"] = [{"label": st["label"], "tests": tests(st["tests"]), "cite": [cited(st["cite"])]}
                            for st in q["steps"]]
        qs.append(out)
    SYSTEMS[ci] = {"title": sd["title"], "signs": [cited(c) for c in sd.get("signs", [])], "questions": qs}
    for other, q in sd.get("from", {}).items():
        SYSFROM[CID[other]] = {"to": ci, "title": sd["title"], "cite": cited(q)}

# ---------------------------------------------------------------------------
# 3. RELATIONSHIP NOTES — every one a verbatim quote from a fetched page
# ---------------------------------------------------------------------------
def R(a, b, when, quote, src, url, kind="relationship"):
    return {"a": a, "b": b, "when": when, "q": quote, "s": src, "u": url, "k": kind}

MP = MPLUS
REL = [
 R("hgb","hct","any",
   "Abnormal levels of red blood cells, hemoglobin, or hematocrit may be a sign of dehydration, anemia, heart disease, or too little iron in your body.",
   MP, "https://medlineplus.gov/lab-tests/complete-blood-count-cbc/"),
 R("hgb","ferritin","low",
   "You may also need this test if the results of other blood tests show that you have low levels of hematocrit (the amount of your blood that is made up of red blood cells) or hemoglobin (the protein that carries oxygen throughout the body).",
   MP, "https://medlineplus.gov/lab-tests/ferritin-blood-test/", "next-test"),
 R("mcv","ferritin","low",
   "If your red blood cells are smaller than normal, it may mean you have: Iron deficiency anemia, the most common form of anemia. It happens when you don't have enough iron in your body.",
   MP, "https://medlineplus.gov/lab-tests/red-blood-cell-rbc-indices/"),
 R("mcv","b12","high",
   "If your red blood cells are larger than normal, it may mean you have: Anemia caused by a vitamin B deficiency",
   MP, "https://medlineplus.gov/lab-tests/red-blood-cell-rbc-indices/"),
 R("bili","rbc","any",
   "Bilirubin is a yellowish substance made during your body's normal process of breaking down old red blood cells.",
   MP, "https://medlineplus.gov/lab-tests/bilirubin-blood-test/"),
 R("bili","alt","any",
   "If your liver is healthy, it will remove most of the bilirubin from your body through your bile ducts (the tubes that carry bile from your liver).",
   MP, "https://medlineplus.gov/lab-tests/bilirubin-blood-test/"),
 R("albumin","alt","any",
   "This is the main protein in your blood. It's made in your liver.",
   MP, "https://medlineplus.gov/lab-tests/comprehensive-metabolic-panel-cmp/"),
 R("albumin","creat","abnormal",
   "An albumin blood test is used to check your general health and nutrition, and to see how well your liver and kidneys are working. If your liver is damaged or you're not well nourished, your liver may not make enough albumin. If your kidneys are damaged, they may let albumin pass from your blood into your urine (pee).",
   MP, "https://medlineplus.gov/lab-tests/albumin-blood-test/"),
 R("tp","albumin","any",
   "There are two major types of protein in the blood: albumin and globulin. Albumin makes up most of the protein in the blood, while the rest are called globulins.",
   MP, "https://medlineplus.gov/lab-tests/total-protein-and-albumin-globulin-a-g-ratio/"),
 R("alt","ast","any",
   "Your ALT is usually measured along with another liver enzyme called AST as part of a liver function panel. Since ALT is mostly found in the liver, an ALT test checks more specifically for liver damage.",
   MP, "https://medlineplus.gov/lab-tests/alt-blood-test/"),
 R("ast","alt","any",
   "It is found mainly in your liver but also in your heart, muscles, and other tissues.",
   MP, "https://medlineplus.gov/lab-tests/ast-test/"),
 R("alp","alt","high",
   "ALP is found in all your body tissues, but higher amounts can be found in your liver, bile ducts, and bones. Each part of your body makes a different type of ALP.",
   MP, "https://medlineplus.gov/lab-tests/alkaline-phosphatase/"),
 R("alp","liverpanel","high",
   "If your test results show high ALP levels, your provider may order other tests to help figure out what's causing the problem.",
   MP, "https://medlineplus.gov/lab-tests/alkaline-phosphatase/", "next-test"),
 R("calcium","albumin","any",
   "\"Bound calcium\" is attached to proteins in your blood. \"Free calcium\" is not attached to proteins. It's also called ionized calcium. This form of blood calcium is active in many body functions.",
   MP, "https://medlineplus.gov/lab-tests/calcium-blood-test/"),
 R("calcium","ionized","abnormal",
   "An ionized calcium test is more difficult to do, so it's usually ordered if the results of a total calcium test aren't normal.",
   MP, "https://medlineplus.gov/lab-tests/calcium-blood-test/", "next-test"),
 R("calcium","tp","low",
   "Results from a total calcium test that are lower than normal (hypocalcemia) may be a sign of: Low blood protein levels, which may be caused by liver disease or malnutrition",
   MP, "https://medlineplus.gov/lab-tests/calcium-blood-test/"),
 R("calcium","pth","abnormal",
   "You may need a PTH test if you: Had a calcium test that showed your blood calcium levels aren't normal.",
   MP, "https://medlineplus.gov/lab-tests/parathyroid-hormone-pth-test/", "next-test"),
 R("calcium","phosphate","any",
   "When blood calcium levels increase, phosphate levels decrease. And when calcium levels decrease, phosphate levels increase.",
   MP, "https://medlineplus.gov/lab-tests/phosphate-in-blood/"),
 R("calcium","vitd","any",
   "Vitamin D helps your body absorb calcium to build healthy bones and teeth.",
   MP, "https://medlineplus.gov/lab-tests/vitamin-d-test/"),
 R("calcium","magnesium","abnormal",
   "A magnesium blood test may also be used to help find the cause of abnormal levels of other minerals, including calcium, potassium, and phosphorus. That's because magnesium plays a role in how your body absorbs these minerals.",
   MP, "https://medlineplus.gov/lab-tests/magnesium-blood-test/", "next-test"),
 R("creat","bun","any",
   "Creatinine blood levels measured as part of a CMP or a BMP may be compared with the level of BUN (blood urea nitrogen) that's measured in the same test. This can help find out the cause of a kidney problem.",
   MP, "https://medlineplus.gov/lab-tests/creatinine-test/"),
 R("creat","egfr","any",
   "Creatinine levels in blood are often used to calculate how fast your kidneys filter waste out of your blood. This is called an estimated glomerular filtration rate (eGFR).",
   MP, "https://medlineplus.gov/lab-tests/creatinine-test/"),
 R("creat","kidney","abnormal",
   "If your results are abnormal, a single high creatinine test can't diagnose a specific condition. You will likely need to be retested and/or have other tests, too.",
   MP, "https://medlineplus.gov/lab-tests/creatinine-test/", "next-test"),
 R("glucose","a1c","high",
   "If you're checking it at home, you are measuring what your blood glucose level is at that time. An A1C test gives you an average level of your blood glucose level over the past two to three months.",
   MP, "https://medlineplus.gov/lab-tests/hemoglobin-a1c-hba1c-test/", "next-test"),
 R("ldl","trig","any",
   "The LDL listed on your results may say \"calculated.\" This means that your LDL level is an estimate based on your total cholesterol, HDL, and triglycerides.",
   MP, "https://medlineplus.gov/lab-tests/cholesterol-levels/"),
 R("trig","vldl","any",
   "VLDL isn't usually included in routine cholesterol tests because it's difficult to measure. Because VLDL contains a certain percentage of triglycerides, a lab can use your triglycerides level to estimate your VLDL level.",
   MP, "https://medlineplus.gov/lab-tests/cholesterol-levels/"),
 R("trig","apob","high",
   "If your blood triglyceride levels are borderline, your provider may order another blood test called apolipoprotein B or \"apo B.\" The results of this test can help your provider understand how high your risk of heart and blood vessel problems may be.",
   MP, "https://medlineplus.gov/lab-tests/triglycerides-test/", "next-test"),
 R("cbc","panel","any",
   "A complete blood count is only one tool your provider uses to learn about your health. Your provider will consider your medical history, symptoms, and other factors to make a diagnosis. You may also need additional tests.",
   MP, "https://medlineplus.gov/lab-tests/complete-blood-count-cbc/"),
 R("panel","panel","abnormal",
   "In general, if you have one or more results that aren't normal, it may be a sign of a health condition. For example, high blood glucose may be a sign of diabetes. You will likely need more tests to confirm or rule out a specific diagnosis.",
   MP, "https://medlineplus.gov/lab-tests/comprehensive-metabolic-panel-cmp/"),
]
# names for the off-panel markers a relationship can point at
OFFPANEL = {
 "ferritin":"Ferritin", "b12":"Vitamin B12", "ionized":"Ionized calcium", "pth":"Parathyroid hormone",
 "phosphate":"Phosphate", "vitd":"Vitamin D", "magnesium":"Magnesium", "egfr":"Estimated GFR",
 "a1c":"Hemoglobin A1c", "vldl":"VLDL cholesterol", "apob":"Apolipoprotein B",
 "liverpanel":"Liver function tests", "kidney":"Further kidney tests", "panel":"Your annual panel",
}
# The relationship table was written against the old short slugs; map them onto
# the panel-library slugs so the notes keep their readable names in source.
ALIAS = {k: slugify(v) for k, v in {
 "rbc":"Red Blood Cell count", "wbc":"White Blood Cell count", "plt":"Platelet count",
 "hgb":"Hemoglobin", "hct":"Hematocrit", "mcv":"Red Blood Cell indices",
 "cbc":"Complete Blood Count", "glucose":"Blood glucose", "calcium":"Calcium",
 "sodium":"Sodium", "potassium":"Potassium", "bicarb":"Bicarbonate", "chloride":"Chloride",
 "albumin":"Albumin", "tp":"Total protein", "alp":"Alkaline phosphatase",
 "alt":"Alanine aminotransferase", "ast":"Aspartate aminotransferase", "bili":"Bilirubin",
 "bun":"Blood Urea Nitrogen", "creat":"Creatinine", "tc":"Total cholesterol",
 "ldl":"LDL cholesterol", "hdl":"HDL cholesterol", "trig":"Triglycerides",
 "lipid":"Lipid panel (cholesterol)",
}.items()}
for r in REL:
    for side in ("a", "b"):
        r[side] = ALIAS.get(r[side], r[side])
        assert r[side] in markers or r[side] in OFFPANEL, "unknown marker %r" % r[side]

# ---------------------------------------------------------------------------
PAY = {
 "panels": PANEL_ORDER,
 # Your report also contains measures this atlas structurally cannot map:
 # a urinalysis (urine, not blood) and a urea breath test (breath, not blood).
 # Stated rather than silently dropped.
 "offSpecimen": [
   {"name": "Urinalysis", "n": 11, "why": "urine, not blood"},
   {"name": "Urea Breath Test", "n": 1, "why": "breath, not blood"},
 ],
 "markers": markers,
 "concerns": concerns,
 "cgroups": CGROUPS,
 "rel": REL,
 "off": OFFPANEL,
 "systems": SYSTEMS,
 "sysFrom": SYSFROM,
 "meta": {
   "total": len(TESTS), "base": len(base_idx),
   "nConcerns": len(CONCERNS), "panelConcerns": len(panel_concerns),
   "quoted": sum(1 for t in TESTS if t.get("v")),
   "offPanelForPanelConcerns": sum(concerns[c]["nOutside"] for c in panel_concerns),
 },
}

# index.html is itself the template: the shell (markup/CSS/JS) is hand-edited
# in place, and this script only ever replaces its one generated line, "const
# D = {...};" — so there is no second copy of the shell to fall out of sync.
CUR = io.open(DST, encoding="utf8", newline="").read()
PREFIX = "const D = "
start = CUR.index(PREFIX)
line_end = CUR.index("\n", start)
old_line = CUR[start:line_end]
assert old_line.rstrip().endswith("};"), "index.html's \"const D = ...\" line isn't shaped as expected"
new_line = PREFIX + json.dumps(PAY, ensure_ascii=False, separators=(",", ":")) + ";"
out = CUR[:start] + new_line + CUR[line_end:]
# newline="" keeps the file's LF endings on Windows, where text mode would
# rewrite every line as CRLF and turn a one-line data change into a whole-file diff.
io.open(DST, "w", encoding="utf8", newline="").write(out)

m = PAY["meta"]
print("%s  %.0f KB" % (os.path.basename(DST), len(out) / 1024.0))
print("  %d markers across %d panels (%d components not in the catalogue)"
      % (len(markers), len(PANEL_ORDER), sum(p["nMissing"] for p in PANEL_ORDER)))
ann_slugs = []
for _p in PANEL_ORDER:
    if _p.get("grp") == "ANNUAL":
        ann_slugs += [sl for sl in _p["slugs"] if sl not in ann_slugs]
ann_reach = set()
for _sl in ann_slugs:
    ann_reach |= set(markers[_sl].get("k") or [])
print("  %d concerns (%d reachable from every panel in the library, %d from your annual panel)"
      % (m["nConcerns"], m["panelConcerns"], len(ann_reach)))
print("  your annual panel: %d sections, %d markers, %d components not in the catalogue"
      % (sum(1 for _p in PANEL_ORDER if _p.get("grp") == "ANNUAL"), len(ann_slugs),
         sum(_p["nMissing"] for _p in PANEL_ORDER if _p.get("grp") == "ANNUAL")))
print("  %d sourced relationship notes" % len(REL))
print("  %d system view(s): %s" % (len(SYSTEMS), ", ".join("%s (%d quotes)" % (concerns[ci]["label"],
      sum(len(q["cite"]) + sum(len(st["cite"]) for st in q.get("steps", [])) for q in s["questions"]) + len(s["signs"]))
      for ci, s in SYSTEMS.items())))
print("  %s follow-up tests sit outside the panel for those concerns" % format(m["offPanelForPanelConcerns"], ","))
print("  %d distinct follow-up markers carried (cap 40 per concern)" % sum(len(c["next"]) for c in concerns.values()))
print("  families per concern: median %d, max %d" % (sorted(len(c["fams"]) for c in concerns.values())[len(concerns)//2], max(len(c["fams"]) for c in concerns.values())))
print("  commonly-ordered markers per concern: median %d, max %d" % (
    sorted(sum(f["c"] for f in c["fams"]) for c in concerns.values())[len(concerns)//2],
    max(sum(f["c"] for f in c["fams"]) for c in concerns.values())))
print("  de-duplicated from %d LOINC rows" % sum(sum(t["nv"] for t in c["next"]) for c in concerns.values()))
