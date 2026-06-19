#!/usr/bin/env python3
"""Build allergen_explorer.html from menu_allergens.csv.

Self-contained, offline, no libraries: the menu data is embedded as JSON.
Pick one or more allergens to avoid and see which items are safe, with
live-updating counts. Run `python3 build_allergen_explorer.py`.
"""

import csv
import json

CSV = "menu_allergens.csv"
OUT = "allergen_explorer.html"
SRC_PDF = "Menu-Nutritionals-2026-05-05.pdf"
ALLERGENS = ["Egg", "Milk", "Soy", "Wheat", "Tree Nuts", "Peanut"]


def main():
    items = []
    with open(CSV, newline="") as f:
        for r in csv.DictReader(f):
            items.append({
                "section": r["section"],
                "item": r["item"],
                "composite": r["is_composite"] == "True",
                "cal": r["cal"],
                "allergens": [a for a in r["allergens"].split("; ") if a],
            })
    data_json = json.dumps(items, separators=(",", ":"), ensure_ascii=False)
    html = TEMPLATE.replace("/*__DATA__*/null", data_json) \
                   .replace("/*__ALLERGENS__*/null", json.dumps(ALLERGENS))
    with open(OUT, "w") as f:
        f.write(html)
    print(f"Wrote {OUT} ({len(items)} items embedded)")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Waffle House Allergen Explorer</title>
<style>
  :root{ --ink:#1f2937; --muted:#6b7280; --line:#e5e7eb; --bg:#f8fafc; --panel:#fff;
         --safe:#16a34a; --avoid:#dc2626; --avoidbg:#fef2f2; }
  *{ box-sizing:border-box; }
  body{ margin:0; font:15px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
        color:var(--ink); background:var(--bg); }
  header{ padding:20px 22px 14px; background:var(--panel); border-bottom:1px solid var(--line); }
  h1{ margin:0 0 4px; font-size:21px; }
  .count{ font-size:15px; color:var(--muted); margin-top:8px; }
  .count b{ color:var(--safe); font-size:18px; }
  .wrap{ max-width:900px; margin:0 auto; padding:18px 22px 60px; }
  .picker{ display:flex; gap:9px; flex-wrap:wrap; align-items:center; margin:4px 0 6px; }
  .picker .lbl{ font-weight:600; margin-right:4px; }
  .chip{ border:1.5px solid var(--line); background:#fff; color:var(--ink); border-radius:999px;
         padding:7px 14px; font:inherit; font-size:14px; cursor:pointer; transition:all .1s; }
  .chip:hover{ border-color:#cbd5e1; }
  .chip.on{ background:var(--avoid); border-color:var(--avoid); color:#fff; }
  .toolbar{ display:flex; gap:14px; align-items:center; flex-wrap:wrap; margin:12px 0 4px;
            font-size:14px; color:var(--muted); }
  .toolbar label{ cursor:pointer; }
  button.link{ background:none; border:none; color:#2563eb; cursor:pointer; font:inherit; padding:0; }
  .section{ margin-top:22px; }
  .section h2{ font-size:14px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted);
               border-bottom:1px solid var(--line); padding-bottom:5px; margin:0 0 8px;
               display:flex; justify-content:space-between; }
  .section h2 .sc{ color:var(--safe); font-weight:600; }
  .item{ display:flex; justify-content:space-between; align-items:baseline; gap:12px;
         padding:6px 8px; border-radius:7px; }
  .item.unsafe{ opacity:.4; background:var(--avoidbg); }
  .item .nm{ font-weight:500; }
  .item .cal{ color:var(--muted); font-size:12px; font-weight:400; }
  .tags{ display:flex; gap:5px; flex-wrap:wrap; justify-content:flex-end; }
  .tag{ font-size:11px; padding:2px 7px; border-radius:999px; background:#eef2f7; color:var(--muted); }
  .tag.hit{ background:var(--avoid); color:#fff; }
  .tag.none{ background:#dcfce7; color:#166534; }
  .ci{ cursor:help; color:#9ca3af; font-size:12px; }
  details.methods{ background:#fffbeb; border:1px solid #fde68a; border-radius:9px;
                   padding:10px 14px; margin-top:18px; font-size:13px; color:#92400e; }
  details.methods summary{ cursor:pointer; font-weight:600; }
  details.methods p{ margin:8px 0; color:#78350f; }
  details.methods code{ background:#fef3c7; padding:1px 4px; border-radius:3px; }
</style>
</head>
<body>
<header>
  <h1>🧇 Waffle House Allergen Explorer</h1>
  <div>Pick the allergens you need to <b>avoid</b>; the list shows what's safe to eat.</div>
  <div class="count" id="count"></div>
</header>

<div class="wrap">
  <div class="picker" id="picker"><span class="lbl">Avoid:</span></div>
  <div class="toolbar">
    <label><input type="checkbox" id="hideUnsafe" checked> Hide unsafe items</label>
    <button class="link" id="clear">Clear selection</button>
  </div>
  <div id="list"></div>

  <details class="methods" open>
    <summary>Methods &amp; data source</summary>
    <p><b>Source:</b> <code>Menu-Nutritionals-2026-05-05.pdf</code> (Waffle House published
       nutritional guide, dated 05/05/26), extracted into <code>menu_allergens.csv</code>.
       Each row is one menu line item; the menu's <b>Allergens</b> column lists allergens an
       item <i>contains</i>, so "safe" here means the item does <b>not</b> list the allergen(s)
       you selected.</p>
    <p><b>What "no allergens" means:</b> a blank allergen cell in the source means none of the
       six tracked allergens (Egg, Milk, Soy, Wheat, Tree Nuts, Peanut) are listed. The menu does
       not track Fish or Shellfish.</p>
    <p><b>Combined items:</b> items marked <span class="ci">ⓘ</span> are composites (e.g. a
       hashbrown bowl) whose allergens were rolled up from all their components, so a meal never
       falsely appears allergen-free. Build-your-own specials are rolled up the same way and may
       therefore list more allergens than a single component would.</p>
    <p><b>⚠️ Not medical advice.</b> Waffle House prepares food in shared kitchens and fryers, so
       cross-contact is possible even for items with no listed allergen. Always confirm with the
       restaurant if you have a serious allergy.</p>
  </details>
</div>

<script>
const DATA = /*__DATA__*/null;
const ALLERGENS = /*__ALLERGENS__*/null;
const avoid = new Set();

// build allergen chips
const picker = document.getElementById("picker");
ALLERGENS.forEach(a=>{
  const b=document.createElement("button");
  b.className="chip"; b.textContent=a; b.dataset.a=a;
  b.onclick=()=>{ avoid.has(a)?avoid.delete(a):avoid.add(a); render(); };
  picker.appendChild(b);
});
document.getElementById("clear").onclick=()=>{ avoid.clear(); render(); };
document.getElementById("hideUnsafe").onchange=render;

function isSafe(it){ return !it.allergens.some(a=>avoid.has(a)); }

function render(){
  // chip states
  document.querySelectorAll(".chip").forEach(c=>
    c.classList.toggle("on", avoid.has(c.dataset.a)));

  const hideUnsafe = document.getElementById("hideUnsafe").checked;
  const total = DATA.length;
  const safe = DATA.filter(isSafe).length;

  // header count
  const cnt = document.getElementById("count");
  if (avoid.size===0){
    cnt.innerHTML = `Showing all <b>${total}</b> menu items. Select an allergen to filter.`;
  } else {
    cnt.innerHTML = `<b>${safe}</b> of ${total} items are safe `
      + `(no ${[...avoid].join(", ")}).`;
  }

  // group by section, preserving first-seen order
  const order=[]; const groups={};
  DATA.forEach(it=>{ if(!groups[it.section]){groups[it.section]=[];order.push(it.section);} groups[it.section].push(it); });

  const list=document.getElementById("list"); list.innerHTML="";
  order.forEach(sec=>{
    const rows=groups[sec];
    const safeRows=rows.filter(isSafe);
    const shown = hideUnsafe ? safeRows : rows;
    if (shown.length===0) return;
    const sd=document.createElement("div"); sd.className="section";
    const h=document.createElement("h2");
    h.innerHTML=`<span>${esc(sec)}</span><span class="sc">${safeRows.length}/${rows.length} safe</span>`;
    sd.appendChild(h);
    shown.forEach(it=>{
      const safe=isSafe(it);
      const row=document.createElement("div");
      row.className="item"+(safe?"":" unsafe");
      const tags = it.allergens.length
        ? it.allergens.map(a=>`<span class="tag${avoid.has(a)?" hit":""}">${esc(a)}</span>`).join("")
        : `<span class="tag none">no listed allergens</span>`;
      const ci = it.composite ? ` <span class="ci" title="Allergens combined from all components">ⓘ</span>` : "";
      row.innerHTML =
        `<span class="nm">${esc(it.item)}${ci} <span class="cal">${it.cal} cal</span></span>`
        + `<span class="tags">${tags}</span>`;
      sd.appendChild(row);
    });
    list.appendChild(sd);
  });
}
function esc(s){ return String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c])); }
render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
