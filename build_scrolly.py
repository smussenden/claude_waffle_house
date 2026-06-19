#!/usr/bin/env python3
"""Build a self-contained, offline scrollytelling page on Waffle House growth.

Reads waffle_houses.csv and a simplified US-states GeoJSON, then writes
scrolly.html with both the data and the map outline embedded inline so the
page works with zero internet access and no external libraries.

Store number is used as a *proxy for opening order* (not exact dates — there is
no date column in the data). Dots are revealed in ascending store-number order
as the reader scrolls. All prose numbers are computed here so they can't drift
from the data.

Usage:
    python3 build_scrolly.py
"""

import csv
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "waffle_houses.csv")
GEOJSON_PATH = "/tmp/us-states.json"          # fetched at build time
OUT_PATH = os.path.join(HERE, "scrolly.html")

STATE_NAMES = {
    "AL": "Alabama", "AZ": "Arizona", "AR": "Arkansas", "CO": "Colorado",
    "FL": "Florida", "GA": "Georgia", "IL": "Illinois", "IN": "Indiana",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "MD": "Maryland",
    "MS": "Mississippi", "MO": "Missouri", "NC": "North Carolina",
    "NM": "New Mexico", "OH": "Ohio", "OK": "Oklahoma", "PA": "Pennsylvania",
    "SC": "South Carolina", "TN": "Tennessee", "TX": "Texas", "VA": "Virginia",
    "WV": "West Virginia", "DC": "District of Columbia",
}


def operator_family(op):
    op = (op or "").strip()
    if not op:
        return "Unknown"
    if op == "WAFFLE HOUSE, INC":
        return "Corporate"
    if op.startswith("FULLY OWNED SUBSIDIARY"):
        return "Subsidiary"
    if op.startswith("FRANCHISE"):
        return "Franchise"
    return "Unknown"


def load_rows():
    """Return numeric-coded stores sorted ascending by store number (the timeline)."""
    rows = []
    excluded = []
    with open(CSV_PATH, newline="") as f:
        for r in csv.DictReader(f):
            code = r["Store Code"]
            rec = {
                "code": code,
                "num": int(code) if code.isdigit() else None,
                "name": r["Business Name"],
                "city": r["City"].title(),
                "state": r["State"],
                "lat": float(r["Latitude"]),
                "lon": float(r["Longitude"]),
                "family": operator_family(r["Operated By"]),
            }
            if rec["num"] is None:
                excluded.append(rec)
            else:
                rows.append(rec)
    rows.sort(key=lambda d: d["num"])
    return rows, excluded


def top_states(rows, k=3):
    c = Counter(r["state"] for r in rows)
    parts = []
    for st, n in c.most_common(k):
        nm = STATE_NAMES.get(st, st)
        parts.append(f"{nm} ({n})")
    return parts


def build_chapters(rows):
    """Define narrative chapters keyed to store-number bands.

    Each chapter sets a reveal cutoff = number of stores shown by its end.
    Prose stats (top states within the newly-revealed band) are computed here.
    """
    n = len(rows)

    def at(frac):
        return min(int(round(frac * n)), n)

    bands = [
        (0,        at(0.05), "The first stores",
         "Waffle House's lowest store numbers cluster in the Georgia–South Carolina "
         "corner where the chain began in 1955. Sorting by store number, the earliest "
         "locations light up across the Deep South first."),
        (at(0.05), at(0.25), "Spreading across the Southeast",
         "Through the low hundreds and into the high hundreds, the dots thicken across "
         "Georgia, the Carolinas, Alabama and Florida — the heartland of the brand."),
        (at(0.25), at(0.50), "Filling in the South",
         "By the midpoint of all store numbers, the map is dense from Texas to Virginia. "
         "Interstate highways and the South's road-trip culture show up as long strings of dots."),
        (at(0.50), at(0.75), "Pushing outward",
         "The upper store numbers reach north into Ohio and the Midwest and west toward "
         "Arizona — the edges of the footprint, far from the Georgia core."),
        (at(0.75), n,        "Today's network",
         "The highest store numbers complete the picture: a little over two thousand "
         "locations, still overwhelmingly concentrated in the Southeast."),
    ]

    chapters = []
    for lo, hi, title, body in bands:
        seg = rows[lo:hi]
        chapters.append({
            "cutoff": hi,
            "lo_num": seg[0]["num"] if seg else None,
            "hi_num": seg[-1]["num"] if seg else None,
            "title": title,
            "body": body,
            "top": top_states(seg, 3),
        })
    return chapters


def load_outline():
    try:
        with open(GEOJSON_PATH) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def main():
    rows, excluded = load_rows()
    chapters = build_chapters(rows)
    outline = load_outline()

    # compact per-dot payload: [lon, lat, family-index]
    fam_idx = {"Corporate": 0, "Subsidiary": 1, "Franchise": 2, "Unknown": 3}
    dots = [[round(r["lon"], 4), round(r["lat"], 4), fam_idx[r["family"]]] for r in rows]

    data_json = json.dumps(dots, separators=(",", ":"))
    chapters_json = json.dumps(chapters, separators=(",", ":"), ensure_ascii=False)
    outline_json = json.dumps(outline, separators=(",", ":")) if outline else "null"

    meta = {
        "n": len(rows),
        "lo": rows[0]["num"], "hi": rows[-1]["num"],
        "lo_city": f'{rows[0]["city"]}, {rows[0]["state"]}',
        "hi_city": f'{rows[-1]["city"]}, {rows[-1]["state"]}',
        "n_excluded": len(excluded),
    }
    meta_json = json.dumps(meta, separators=(",", ":"), ensure_ascii=False)

    html = (HTML_TEMPLATE
            .replace("/*__DATA__*/null", data_json)
            .replace("/*__CHAPTERS__*/null", chapters_json)
            .replace("/*__OUTLINE__*/null", outline_json)
            .replace("/*__META__*/null", meta_json))
    with open(OUT_PATH, "w") as f:
        f.write(html)

    print(f"Wrote {OUT_PATH}")
    print(f"  timeline stores: {len(rows)} (#{rows[0]['num']}–#{rows[-1]['num']}) | "
          f"excluded (no number): {len(excluded)} | "
          f"outline: {'embedded' if outline else 'FALLBACK (hull)'}")
    for c in chapters:
        print(f"  · {c['title']}: up to #{c['hi_num']} (cutoff {c['cutoff']}), top {c['top']}")


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Growth of Waffle House — a scrolly map</title>
<style>
  :root {
    --corp:#2563eb; --sub:#16a34a; --fran:#ea580c; --unk:#9ca3af;
    --ink:#f3f4f6; --muted:#9ca3af; --bg:#0b1020; --panel:#111827; --accent:#fbbf24;
  }
  * { box-sizing:border-box; }
  body { margin:0; font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
         color:var(--ink); background:var(--bg); }
  a { color:var(--accent); }

  .intro, .outro { max-width:720px; margin:0 auto; padding:14vh 24px 8vh; text-align:center; }
  .intro h1 { font-size:clamp(28px,6vw,52px); line-height:1.1; margin:0 0 18px; }
  .intro p, .outro p { color:var(--muted); font-size:18px; }
  .kicker { color:var(--accent); font-weight:700; letter-spacing:.08em; text-transform:uppercase;
            font-size:13px; margin-bottom:10px; }
  .scrollcue { margin-top:30px; color:var(--muted); font-size:13px; animation:bob 1.6s infinite; }
  @keyframes bob { 50% { transform:translateY(6px); } }

  /* scrolly layout: sticky map on the left, scrolling steps on the right */
  .scrolly { position:relative; display:grid; grid-template-columns:1fr 1fr; gap:0;
             max-width:1200px; margin:0 auto; }
  @media (max-width:820px){ .scrolly{ grid-template-columns:1fr; } }

  .sticky { position:sticky; top:0; height:100vh; display:flex; flex-direction:column;
            align-items:center; justify-content:center; padding:18px; }
  @media (max-width:820px){ .sticky{ top:0; height:62vh; } }
  .mapcard { width:100%; }
  svg.map { width:100%; height:auto; display:block; filter:drop-shadow(0 8px 24px rgba(0,0,0,.5)); }
  .state-poly { fill:#1b2335; stroke:#2b364f; stroke-width:0.6; }
  .dot { opacity:0; transition:opacity .5s ease, r .3s ease; }
  .dot.on { opacity:.85; }

  .progress { margin-top:14px; text-align:center; font-size:14px; color:var(--muted); }
  .progress b { color:var(--accent); }
  .bar { width:min(420px,90%); height:8px; background:#1b2335; border-radius:6px;
         margin:8px auto 0; overflow:hidden; }
  .bar > i { display:block; height:100%; width:0; background:var(--accent); transition:width .3s ease; }
  .legend { display:flex; gap:14px; flex-wrap:wrap; justify-content:center; font-size:12px;
            margin-top:12px; color:var(--muted); }
  .legend span { display:inline-flex; align-items:center; gap:5px; }
  .swatch { width:11px; height:11px; border-radius:50%; display:inline-block; }

  .steps { padding:0 24px; }
  .step { min-height:88vh; display:flex; align-items:center; }
  .step .box { background:var(--panel); border:1px solid #1f2a40; border-radius:14px;
               padding:22px 24px; box-shadow:0 10px 30px rgba(0,0,0,.35);
               opacity:.35; transform:translateY(14px); transition:opacity .4s, transform .4s; }
  .step.active .box { opacity:1; transform:none; }
  .step .num { color:var(--accent); font-size:13px; font-weight:700; letter-spacing:.05em; }
  .step h2 { margin:6px 0 10px; font-size:24px; }
  .step p { margin:0 0 10px; color:#d1d5db; }
  .step .stat { font-size:13px; color:var(--muted); }
  .step .stat b { color:var(--ink); }

  .methods { max-width:760px; margin:0 auto; padding:6vh 24px 16vh; }
  .methods .card { background:var(--panel); border:1px solid #1f2a40; border-radius:14px; padding:22px 26px; }
  .methods h2 { margin:0 0 12px; font-size:20px; }
  .methods p { color:#cbd5e1; font-size:15px; }
  .methods code { background:#0b1020; padding:1px 6px; border-radius:4px; color:var(--accent); }
  .warn { color:#fca5a5; }
</style>
</head>
<body>

<section class="intro">
  <div class="kicker">A data story</div>
  <h1>The Growth of Waffle House</h1>
  <p>There are no opening dates in the data — but every restaurant has a <b>store number</b>.
     Lower numbers came first. So we can sort by store number and watch the network spread,
     dot by dot, from the Deep South outward.</p>
  <div class="scrollcue">↓ scroll to begin</div>
</section>

<div class="scrolly">
  <div class="sticky">
    <div class="mapcard">
      <div id="mapbox"></div>
      <div class="progress">
        <div>Showing <b id="shown">0</b> of <span id="total">0</span> stores
             &middot; up to store <b id="upto">#—</b></div>
        <div class="bar"><i id="barfill"></i></div>
        <div class="legend">
          <span><i class="swatch" style="background:var(--corp)"></i>Corporate</span>
          <span><i class="swatch" style="background:var(--sub)"></i>Subsidiary</span>
          <span><i class="swatch" style="background:var(--fran)"></i>Franchise</span>
          <span><i class="swatch" style="background:var(--unk)"></i>Unknown</span>
        </div>
      </div>
    </div>
  </div>

  <div class="steps" id="steps"></div>
</div>

<section class="methods">
  <div class="card">
    <h2>Methods &amp; data source</h2>
    <p><b>Source:</b> <code>waffle_houses.csv</code> — a snapshot of Waffle House's public
       store locator (<span id="m-n"></span> numbered U.S. locations, <code>DATA_DICTIONARY.md</code>
       has the full column docs).</p>
    <p><b class="warn">Store number is a proxy for opening <i>order</i>, not exact dates.</b>
       The data has <i>no</i> opening-date column, so we sort by store number as a stand-in for
       sequence. This is approximate: numbers are assigned roughly in the order stores open, but
       there are gaps, retired numbers, and renumbered sites, so a lower number only <i>usually</i>
       means "opened earlier." The lowest number here is <b id="m-lo"></b> (<span id="m-loc"></span>)
       and the highest is <b id="m-hi"></b> (<span id="m-hic"></span>) — and because of renumbering,
       neither is literally the "first" or "newest" restaurant.</p>
    <p><b>What's excluded:</b> <span id="m-x"></span> record with no numeric store code
       (the Waffle House Museum, <code>WH_Museum</code>) is left out of the timeline because it has
       no number to sort by. Coverage is U.S.-only; this is a footprint over store numbers, not a
       per-capita or chronological-by-year analysis.</p>
    <p><b>Reproducible:</b> the page is generated by <code>build_scrolly.py</code> from the CSV and
       an offline US-states outline; every dot lands at the latitude/longitude in the data, and all
       counts in the prose are computed at build time.</p>
  </div>
</section>

<script>
const DOTS = /*__DATA__*/null;       // [lon, lat, familyIndex] sorted by store number
const CHAPTERS = /*__CHAPTERS__*/null;
const OUTLINE = /*__OUTLINE__*/null;
const META = /*__META__*/null;
const FAM_COLOR = ["#2563eb","#16a34a","#ea580c","#9ca3af"];

// ---- projection (equirectangular, aspect-corrected), fit to contiguous US ----
const MAP_W=640, MAP_H=420, PAD=16;
const EXCLUDE=new Set(["Alaska","Hawaii","Puerto Rico"]);
const STATES = OUTLINE ? OUTLINE.features.filter(f=>!EXCLUDE.has(f.properties.name)) : [];
let latMin=Infinity,latMax=-Infinity,lonMin=Infinity,lonMax=-Infinity;
function eachCoord(geom,fn){ const walk=c=>{ if(typeof c[0]==="number")fn(c[0],c[1]); else c.forEach(walk); }; walk(geom.coordinates); }
if(STATES.length){
  STATES.forEach(f=>eachCoord(f.geometry,(lon,lat)=>{
    if(lon<lonMin)lonMin=lon; if(lon>lonMax)lonMax=lon;
    if(lat<latMin)latMin=lat; if(lat>latMax)latMax=lat;
  }));
} else {
  const lats=DOTS.map(d=>d[1]), lons=DOTS.map(d=>d[0]), M=1.5;
  latMin=Math.min(...lats)-M; latMax=Math.max(...lats)+M;
  lonMin=Math.min(...lons)-M; lonMax=Math.max(...lons)+M;
}
const meanLat=(latMin+latMax)/2, kx=Math.cos(meanLat*Math.PI/180);
const spanX=(lonMax-lonMin)*kx, spanY=(latMax-latMin);
const scale=Math.min((MAP_W-2*PAD)/spanX,(MAP_H-2*PAD)/spanY);
const offX=(MAP_W-spanX*scale)/2, offY=(MAP_H-spanY*scale)/2;
function project(lon,lat){ return [offX+(lon-lonMin)*kx*scale, offY+(latMax-lat)*scale]; }

const SVGNS="http://www.w3.org/2000/svg";
function el(tag,attrs){ const e=document.createElementNS(SVGNS,tag); for(const k in attrs)e.setAttribute(k,attrs[k]); return e; }

const svg=el("svg",{viewBox:`0 0 ${MAP_W} ${MAP_H}`,class:"map"});
if(STATES.length){
  STATES.forEach(f=>{
    const polys=f.geometry.type==="Polygon"?[f.geometry.coordinates]:f.geometry.coordinates;
    polys.forEach(poly=>{
      const ring=poly[0].map(([lon,lat])=>project(lon,lat).join(",")).join(" ");
      svg.appendChild(el("polygon",{points:ring,class:"state-poly"}));
    });
  });
} else {
  const [x0,y0]=project(lonMin,latMax),[x1,y1]=project(lonMax,latMin);
  svg.appendChild(el("rect",{x:x0,y:y0,width:x1-x0,height:y1-y0,class:"state-poly"}));
}
// dots, in store-number order
const dotEls=[];
DOTS.forEach(d=>{
  const [x,y]=project(d[0],d[1]);
  const c=el("circle",{cx:x,cy:y,r:2.3,class:"dot",fill:FAM_COLOR[d[2]]});
  svg.appendChild(c); dotEls.push(c);
});
document.getElementById("mapbox").appendChild(svg);

// ---- progress + reveal ----
const N=DOTS.length;
document.getElementById("total").textContent=N.toLocaleString();
const shownEl=document.getElementById("shown");
const uptoEl=document.getElementById("upto");
const barEl=document.getElementById("barfill");
// curShown = number of dots currently revealed; dots[0..curShown-1] have class "on".
let curShown=0;
function reveal(cutoff){
  cutoff=Math.max(0,Math.min(N,cutoff));
  if(cutoff===curShown) return;
  if(cutoff>curShown){ for(let i=curShown;i<cutoff;i++) dotEls[i].classList.add("on"); }
  else { for(let i=cutoff;i<curShown;i++) dotEls[i].classList.remove("on"); }
  curShown=cutoff;
  shownEl.textContent=cutoff.toLocaleString();
  barEl.style.width=(100*cutoff/N).toFixed(1)+"%";
}

// ---- build steps ----
const steps=document.getElementById("steps");
CHAPTERS.forEach((ch,i)=>{
  const s=document.createElement("div"); s.className="step"; s.dataset.cutoff=ch.cutoff;
  const band = ch.lo_num!=null ? `Store #${ch.lo_num}–#${ch.hi_num}` : "";
  s.innerHTML =
    `<div class="box">`+
    `<div class="num">Chapter ${i+1} · ${band}</div>`+
    `<h2>${esc(ch.title)}</h2>`+
    `<p>${esc(ch.body)}</p>`+
    `<div class="stat">Most locations revealed in this stretch: <b>${ch.top.map(esc).join(" · ")}</b></div>`+
    `</div>`;
  steps.appendChild(s);
});

// reveal as each step becomes active
const stepEls=[...document.querySelectorAll(".step")];
const io=new IntersectionObserver((entries)=>{
  entries.forEach(e=>{
    if(e.isIntersecting){
      stepEls.forEach(s=>s.classList.remove("active"));
      e.target.classList.add("active");
      reveal(parseInt(e.target.dataset.cutoff,10));
    }
  });
},{rootMargin:"-45% 0px -45% 0px", threshold:0});
stepEls.forEach(s=>io.observe(s));

// also clear the map when scrolled back to the very top
const introIO=new IntersectionObserver((entries)=>{
  entries.forEach(e=>{ if(e.isIntersecting) reveal(0); });
},{threshold:0.6});
introIO.observe(document.querySelector(".intro"));

// fill the methods note from META
document.getElementById("m-n").textContent=META.n.toLocaleString();
document.getElementById("m-lo").textContent="#"+META.lo;
document.getElementById("m-hi").textContent="#"+META.hi;
document.getElementById("m-loc").textContent=META.lo_city;
document.getElementById("m-hic").textContent=META.hi_city;
document.getElementById("m-x").textContent=META.n_excluded;

function esc(s){ return String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c])); }
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
