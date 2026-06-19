#!/usr/bin/env python3
"""Build a self-contained, offline Waffle House explorer (one HTML file).

Reads waffle_houses.csv and a simplified US-states GeoJSON, then writes
waffle_explorer.html with both the data and the map outline embedded inline
so the page works with zero internet access and no external libraries.

Usage:
    python3 build_explorer.py
"""

import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "waffle_houses.csv")
GEOJSON_PATH = "/tmp/us-states.json"          # fetched at build time
OUT_PATH = os.path.join(HERE, "waffle_explorer.html")

DUPLICATE_CODES = {"442", "3442"}             # same physical site (see DATA_DICTIONARY §4a)


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


def row_flag(r):
    if r["Store Code"] == "WH_Museum":
        return "museum"
    if "Closed" in (r["Formatted Business Hours"] or ""):
        return "closed"
    if r["Store Code"] in DUPLICATE_CODES:
        return "duplicate"
    return None


def load_rows():
    out = []
    with open(CSV_PATH, newline="") as f:
        for r in csv.DictReader(f):
            out.append({
                "code": r["Store Code"],
                "name": r["Business Name"],
                "address": r["Address"],
                "city": r["City"],
                "state": r["State"],
                "zip": r["Postal Code"],
                "lat": float(r["Latitude"]),
                "lon": float(r["Longitude"]),
                "phone": r["Phone Number"],
                "operator": (r["Operated By"] or "").strip(),
                "hours": (r["Formatted Business Hours"] or "").strip(),
                "family": operator_family(r["Operated By"]),
                "flag": row_flag(r),
            })
    return out


def load_outline():
    """Return simplified US-states GeoJSON, or None to trigger the offline fallback."""
    try:
        with open(GEOJSON_PATH) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def main():
    rows = load_rows()
    outline = load_outline()
    data_json = json.dumps(rows, separators=(",", ":"))
    outline_json = json.dumps(outline, separators=(",", ":")) if outline else "null"

    html = HTML_TEMPLATE.replace("/*__DATA__*/null", data_json) \
                        .replace("/*__OUTLINE__*/null", outline_json)
    with open(OUT_PATH, "w") as f:
        f.write(html)

    flagged = sum(1 for r in rows if r["flag"])
    print(f"Wrote {OUT_PATH}")
    print(f"  rows: {len(rows)} | flagged: {flagged} | outline: {'embedded' if outline else 'FALLBACK (hull)'}")


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Waffle House Locations — Explorer</title>
<style>
  :root {
    --corp:#2563eb; --sub:#16a34a; --fran:#ea580c; --unk:#9ca3af;
    --ink:#1f2937; --muted:#6b7280; --line:#e5e7eb; --bg:#f8fafc; --panel:#fff;
  }
  * { box-sizing:border-box; }
  body { margin:0; font:14px/1.45 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
         color:var(--ink); background:var(--bg); }
  header { padding:18px 22px 12px; border-bottom:1px solid var(--line); background:var(--panel); }
  h1 { margin:0 0 4px; font-size:20px; }
  .sub { color:var(--muted); font-size:13px; }
  .caveat { color:var(--muted); font-size:12px; margin-top:6px; }
  .wrap { display:grid; grid-template-columns:1.55fr 1fr; gap:16px; padding:16px 22px; align-items:start; }
  @media (max-width:900px){ .wrap{ grid-template-columns:1fr; } }
  .card { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px; }
  .card h2 { margin:0 0 10px; font-size:14px; font-weight:600; }
  .controls { display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-bottom:8px; }
  select, button { font:inherit; padding:6px 10px; border:1px solid var(--line); border-radius:7px;
                   background:#fff; color:var(--ink); cursor:pointer; }
  button:hover, select:hover { border-color:#cbd5e1; }
  #status { font-size:13px; color:var(--muted); }
  .legend { display:flex; gap:14px; flex-wrap:wrap; font-size:12px; margin-top:10px; color:var(--muted); }
  .legend span { display:inline-flex; align-items:center; gap:5px; }
  .swatch { width:11px; height:11px; border-radius:50%; display:inline-block; }
  svg { width:100%; height:auto; display:block; }
  .state-poly { fill:#eef2f7; stroke:#cbd5e1; stroke-width:0.6; }
  .dot { cursor:pointer; }
  .dot.dim { opacity:0.08; }
  .bar-row { cursor:pointer; }
  .bar-row:hover .bar { filter:brightness(0.92); }
  .bar { fill:#3b82f6; }
  .bar.active { fill:#1d4ed8; }
  .bar-label, .bar-val { font-size:11px; fill:var(--ink); }
  .bar-val { fill:var(--muted); }
  #tooltip { position:fixed; pointer-events:none; z-index:10; background:#111827; color:#fff;
             padding:8px 10px; border-radius:8px; font-size:12px; max-width:260px; opacity:0;
             transition:opacity .08s; box-shadow:0 4px 14px rgba(0,0,0,.25); }
  #tooltip b { color:#fbbf24; }
  .flag-note { color:#fca5a5; }
  .chartwrap { max-height:520px; overflow-y:auto; }
</style>
</head>
<body>
<header>
  <h1>Waffle House Locations — Explorer</h1>
  <div class="sub"><b id="total">0</b> locations across <b id="nstates">0</b> states ·
    <span id="status">showing all</span></div>
  <div class="caveat">Source: <code>waffle_houses.csv</code>. All rows shown. Flagged rows (museum,
    the #442/#3442 same-site duplicate, 2 closed stores) are ringed — net ≈ <b>2,004</b> distinct
    operating restaurants. See <code>DATA_DICTIONARY.md §4/4a</code>.</div>
</header>

<div class="wrap">
  <div class="card">
    <h2>Map of locations</h2>
    <div id="mapbox"></div>
    <div class="legend">
      <span><i class="swatch" style="background:var(--corp)"></i>Corporate</span>
      <span><i class="swatch" style="background:var(--sub)"></i>Subsidiary</span>
      <span><i class="swatch" style="background:var(--fran)"></i>Franchise</span>
      <span><i class="swatch" style="background:var(--unk)"></i>Unknown</span>
      <span><i class="swatch" style="background:#fff;border:2px solid #dc2626"></i>Flagged (museum/dup/closed)</span>
    </div>
  </div>

  <div class="card">
    <h2>Counts</h2>
    <div class="controls">
      <label>Count by
        <select id="countby">
          <option value="state">State</option>
          <option value="family">Operator family</option>
          <option value="operator">Operator (full)</option>
          <option value="flag">Status flag</option>
        </select>
      </label>
      <button id="reset">Reset filter</button>
    </div>
    <div class="chartwrap"><div id="chart"></div></div>
  </div>
</div>

<div id="tooltip"></div>

<script>
const DATA = /*__DATA__*/null;
const OUTLINE = /*__OUTLINE__*/null;

const FAMILY_COLOR = { Corporate:"#2563eb", Subsidiary:"#16a34a", Franchise:"#ea580c", Unknown:"#9ca3af" };
const FLAG_LABEL = { museum:"Museum (not a restaurant)", duplicate:"Duplicate site (#442/#3442)", closed:"Marked Closed" };

// ---- projection (equirectangular, aspect-corrected) ----
// Fit to the CONTIGUOUS-US outline so all 48 states show. Dots use the same
// transform, so they land wherever the CSV's lat/lon put them (no guessing).
const MAP_W = 640, MAP_H = 420, PAD = 16;
const EXCLUDE = new Set(["Alaska","Hawaii","Puerto Rico"]);  // not contiguous
const STATES = OUTLINE ? OUTLINE.features.filter(f=>!EXCLUDE.has(f.properties.name)) : [];
let latMin=Infinity, latMax=-Infinity, lonMin=Infinity, lonMax=-Infinity;
if (STATES.length){
  STATES.forEach(f=>eachCoord(f.geometry,(lon,lat)=>{
    if(lon<lonMin)lonMin=lon; if(lon>lonMax)lonMax=lon;
    if(lat<latMin)latMin=lat; if(lat>latMax)latMax=lat;
  }));
} else {
  // fallback (no outline available): fit to the data footprint instead
  const lats=DATA.map(d=>d.lat), lons=DATA.map(d=>d.lon), M=1.5;
  latMin=Math.min(...lats)-M; latMax=Math.max(...lats)+M;
  lonMin=Math.min(...lons)-M; lonMax=Math.max(...lons)+M;
}
const meanLat=(latMin+latMax)/2, kx=Math.cos(meanLat*Math.PI/180);
const spanX=(lonMax-lonMin)*kx, spanY=(latMax-latMin);
const scale=Math.min((MAP_W-2*PAD)/spanX, (MAP_H-2*PAD)/spanY);
const offX=(MAP_W-spanX*scale)/2, offY=(MAP_H-spanY*scale)/2;
function project(lon,lat){
  return [ offX + (lon-lonMin)*kx*scale,
           offY + (latMax-lat)*scale ];   // y flipped
}
function eachCoord(geom, fn){
  const walk = c => {
    if (typeof c[0]==="number") fn(c[0],c[1]);
    else c.forEach(walk);
  };
  walk(geom.coordinates);
}

// ---- build SVG map ----
const SVGNS="http://www.w3.org/2000/svg";
function el(tag, attrs){ const e=document.createElementNS(SVGNS,tag);
  for(const k in attrs) e.setAttribute(k, attrs[k]); return e; }

const svg = el("svg",{viewBox:`0 0 ${MAP_W} ${MAP_H}`});

// state polygons — all 48 contiguous states
if (STATES.length){
  STATES.forEach(f=>{
    const polys = f.geometry.type==="Polygon" ? [f.geometry.coordinates] : f.geometry.coordinates;
    polys.forEach(poly=>{
      const ring = poly[0].map(([lon,lat])=>project(lon,lat).join(",")).join(" ");
      svg.appendChild(el("polygon",{points:ring, class:"state-poly"}));
    });
  });
} else {
  // fallback: faint bounding rect so dots still read as a map
  const [x0,y0]=project(lonMin,latMax), [x1,y1]=project(lonMax,latMin);
  svg.appendChild(el("rect",{x:x0,y:y0,width:x1-x0,height:y1-y0,class:"state-poly"}));
}

// dots
const dotEls=[];
DATA.forEach((d,i)=>{
  const [x,y]=project(d.lon,d.lat);
  const c=el("circle",{cx:x,cy:y,r:d.flag?3.4:2.4,class:"dot",
    fill:d.flag?"#fff":FAMILY_COLOR[d.family],
    stroke:d.flag?"#dc2626":"none","stroke-width":d.flag?1.6:0,"data-i":i});
  c.addEventListener("mousemove",e=>showTip(e,d));
  c.addEventListener("mouseleave",hideTip);
  svg.appendChild(c); dotEls.push(c);
});
document.getElementById("mapbox").appendChild(svg);

// ---- tooltip ----
const tip=document.getElementById("tooltip");
function showTip(e,d){
  tip.innerHTML = `<b>${esc(d.name)}</b><br>${esc(d.address)}<br>${esc(d.city)}, ${d.state} ${d.zip}`
    + `<br>${esc(d.operator||"—")}<br>${esc(d.hours||"—")}`
    + (d.flag?`<br><span class="flag-note">⚑ ${FLAG_LABEL[d.flag]}</span>`:"");
  tip.style.opacity=1;
  const ox=14; let x=e.clientX+ox, y=e.clientY+ox;
  if(x+270>innerWidth) x=e.clientX-270;
  tip.style.left=x+"px"; tip.style.top=y+"px";
}
function hideTip(){ tip.style.opacity=0; }
function esc(s){ return String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c])); }

// ---- header totals ----
document.getElementById("total").textContent = DATA.length.toLocaleString();
document.getElementById("nstates").textContent = new Set(DATA.map(d=>d.state)).size;

// ---- chart + linking ----
let activeFilter=null;   // {key, value}
function valueFor(d, key){
  if(key==="flag") return d.flag ? FLAG_LABEL[d.flag] : "OK (none)";
  const v=d[key];
  return (v===undefined||v==="") ? "(blank / NA)" : v;
}
function renderChart(){
  const key=document.getElementById("countby").value;
  const counts={};
  DATA.forEach(d=>{ const v=valueFor(d,key); counts[v]=(counts[v]||0)+1; });
  const entries=Object.entries(counts).sort((a,b)=>b[1]-a[1]);
  const max=entries[0][1], total=DATA.length;
  const rowH=22, labelW=key==="operator"?180:90, valW=64;
  const W=560, barMax=W-labelW-valW-10, H=entries.length*rowH+6;
  const c=el("svg",{viewBox:`0 0 ${W} ${H}`});
  entries.forEach(([val,n],i)=>{
    const y=i*rowH+4, bw=Math.max(1,(n/max)*barMax);
    const g=el("g",{class:"bar-row"});
    const isActive=activeFilter&&activeFilter.key===key&&activeFilter.value===val;
    const t1=el("text",{x:0,y:y+14,class:"bar-label"});
    t1.textContent = val.length>26 ? val.slice(0,25)+"…" : val;
    const rect=el("rect",{x:labelW,y:y+3,width:bw,height:14,rx:3,class:"bar"+(isActive?" active":"")});
    const t2=el("text",{x:labelW+bw+6,y:y+14,class:"bar-val"});
    t2.textContent = `${n.toLocaleString()} · ${(100*n/total).toFixed(1)}%`;
    g.appendChild(t1); g.appendChild(rect); g.appendChild(t2);
    g.addEventListener("click",()=>toggleFilter(key,val));
    c.appendChild(g);
  });
  const box=document.getElementById("chart"); box.innerHTML=""; box.appendChild(c);
}
function toggleFilter(key,value){
  if(activeFilter&&activeFilter.key===key&&activeFilter.value===value) activeFilter=null;
  else activeFilter={key,value};
  applyFilter(); renderChart();
}
function applyFilter(){
  const st=document.getElementById("status");
  if(!activeFilter){
    dotEls.forEach(c=>c.classList.remove("dim"));
    st.textContent="showing all"; return;
  }
  let shown=0;
  DATA.forEach((d,i)=>{
    const match = valueFor(d,activeFilter.key)===activeFilter.value;
    dotEls[i].classList.toggle("dim",!match);
    if(match) shown++;
  });
  st.textContent=`showing ${shown.toLocaleString()} of ${DATA.length.toLocaleString()} · ${esc(activeFilter.value)}`;
}
document.getElementById("countby").addEventListener("change",()=>{ activeFilter=null; applyFilter(); renderChart(); });
document.getElementById("reset").addEventListener("click",()=>{ activeFilter=null; applyFilter(); renderChart(); });

renderChart();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
