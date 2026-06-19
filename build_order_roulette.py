#!/usr/bin/env python3
"""Build order_roulette.html from menu_allergens.csv.

Geocities-aesthetic single-file HTML: click a button, get a random Waffle House order.
"""

import csv
import json

CSV = "menu_allergens.csv"
OUT = "order_roulette.html"

# Map slot names to sections from the CSV
SLOTS = [
    ("🧇 Waffle or Bread", ["Waffles", "Grilled Biscuits"]),
    ("🍳 Eggs", ["EGG BREAKFASTS", "EGG BREAKFASTS CONTINUED",
                  "Toddle House© Omelet Breakfasts", "Toddle House© Omelet Breakfasts Continued"]),
    ("🥓 Meat / Side", ["Breakfast Sides"]),
    ("🥔 Hashbrowns", ["Hashbrowns and Toppings"]),
    ("☕ Beverage", ["Beverages"]),
]


def main():
    items = []
    with open(CSV, newline="") as f:
        for r in csv.DictReader(f):
            # Skip composite rollup rows for ordering (use leaf items)
            if r["is_composite"] == "True":
                continue
            items.append({
                "section": r["section"],
                "item": r["item"],
                "cal": r["cal"],
                "allergens": [a for a in r["allergens"].split("; ") if a],
            })

    slots_json = json.dumps(
        [[name, sections] for name, sections in SLOTS],
        separators=(",", ":"), ensure_ascii=False
    )
    data_json = json.dumps(items, separators=(",", ":"), ensure_ascii=False)

    html = TEMPLATE \
        .replace("/*__DATA__*/null", data_json) \
        .replace("/*__SLOTS__*/null", slots_json)

    with open(OUT, "w") as f:
        f.write(html)
    print(f"Wrote {OUT}")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Waffle House Order Roulette!!!!</title>
<style>
  body {
    background-color: #ff00ff;
    background-image: repeating-linear-gradient(
      45deg, #ff00ff 0px, #ff00ff 10px,
      #ffff00 10px, #ffff00 20px
    );
    font-family: "Comic Sans MS", "Comic Sans", cursive, sans-serif;
    color: #000080;
    margin: 0;
    padding: 10px;
    text-align: center;
  }
  h1 {
    font-size: 2.8em;
    color: #ff0000;
    text-shadow: 3px 3px #ffff00, 6px 6px #0000ff;
    margin: 8px 0 0;
    letter-spacing: 2px;
  }
  .subtitle {
    font-size: 1.1em;
    color: #000080;
    margin: 4px 0 10px;
    font-weight: bold;
  }
  .panel {
    background: #ffffcc;
    border: 4px ridge #ff6600;
    border-radius: 0;
    max-width: 640px;
    margin: 0 auto 12px;
    padding: 14px 18px;
    box-shadow: 6px 6px 0 #ff00ff;
  }
  #spin-btn {
    background: #ff0000;
    color: #ffff00;
    font-family: inherit;
    font-size: 1.5em;
    font-weight: bold;
    border: 4px outset #cc0000;
    padding: 12px 32px;
    cursor: pointer;
    text-shadow: 1px 1px #000;
    letter-spacing: 1px;
    animation: blink 1s step-start infinite;
    margin: 8px 0 14px;
  }
  #spin-btn:active { border-style: inset; }
  @keyframes blink { 50% { opacity: 0.4; } }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.95em;
    margin: 0 auto;
    background: #fff;
  }
  th {
    background: #0000cc;
    color: #ffff00;
    padding: 5px 8px;
    text-align: left;
    font-size: 1em;
  }
  td {
    border: 1px solid #999;
    padding: 5px 8px;
    text-align: left;
  }
  tr:nth-child(even) td { background: #eeeeff; }
  .slot-name { color: #cc0000; font-weight: bold; }
  .cal { color: #666; font-size: 0.85em; }
  #total-row td { background: #000080; color: #ffff00; font-weight: bold; font-size: 1em; }
  .allergen-section {
    margin-top: 10px;
    padding: 8px;
    background: #ffcccc;
    border: 3px dashed #ff0000;
    font-size: 0.95em;
  }
  .allergen-section b { color: #cc0000; font-size: 1.05em; }
  .a-badge {
    display: inline-block;
    background: #ff3300;
    color: #fff;
    border-radius: 0;
    padding: 2px 8px;
    margin: 2px;
    font-weight: bold;
    border: 2px solid #cc0000;
  }
  .none-badge {
    display: inline-block;
    background: #009900;
    color: #fff;
    padding: 2px 10px;
    font-weight: bold;
    border: 2px solid #006600;
  }
  .divider {
    color: #ff6600;
    font-size: 1.3em;
    margin: 4px 0;
    letter-spacing: 4px;
  }
  .source {
    font-size: 0.78em;
    color: #555;
    margin-top: 8px;
    border-top: 1px dashed #aaa;
    padding-top: 6px;
  }
  #order-area { display: none; }
  marquee { color: #ff0000; font-weight: bold; font-size: 1.1em; margin: 4px 0; }
</style>
</head>
<body>

<h1>&#127959; WAFFLE HOUSE &#127959;<br>ORDER ROULETTE!!!!</h1>
<marquee scrollamount="5">★ ★ ★ Welcome to the BEST Waffle House Order Generator on the INTERNET ★ ★ ★ Since 2026 ★ ★ ★</marquee>
<div class="subtitle">Click the button. Get a REAL random Waffle House meal!!</div>

<div class="panel">
  <button id="spin-btn" onclick="spinOrder()">🎲 SPIN MY ORDER!! 🎲</button>

  <div id="order-area">
    <div class="divider">★ ★ ★ ★ ★ ★ ★ ★ ★ ★</div>
    <b style="font-size:1.1em;color:#000080;">YOUR ORDER:</b>
    <table id="order-table">
      <thead><tr><th>Course</th><th>Item</th><th>Cal</th></tr></thead>
      <tbody id="order-body"></tbody>
      <tfoot><tr id="total-row"><td colspan="2">TOTAL CALORIES</td><td id="total-cal"></td></tr></tfoot>
    </table>

    <div class="allergen-section">
      <b>⚠️ COMBINED ALLERGENS:</b><br>
      <div id="allergen-badges" style="margin-top:5px;"></div>
    </div>

    <div class="source">
      Data: <em>Menu-Nutritionals-2026-05-05.pdf</em> (Waffle House published nutritional guide, 05/05/26),
      extracted into <code>menu_allergens.csv</code>. Allergens listed are those the item <em>contains</em>.
      Waffle House uses shared kitchens — cross-contact is possible. Not medical advice.
    </div>
  </div>
</div>

<div class="divider">☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆</div>
<div style="font-size:0.8em;color:#000080;">
  <blink>★ VISITOR #<span id="vctr"></span> ★</blink>
</div>

<script>
const DATA = /*__DATA__*/null;
const SLOTS = /*__SLOTS__*/null;

// random visitor counter aesthetic
document.getElementById("vctr").textContent = (Math.floor(Math.random()*89000)+11000).toLocaleString();

// Build section lookup
const bySection = {};
DATA.forEach(item => {
  if (!bySection[item.section]) bySection[item.section] = [];
  bySection[item.section].push(item);
});

function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

function spinOrder() {
  const chosen = [];
  SLOTS.forEach(([name, sections]) => {
    const pool = sections.flatMap(s => bySection[s] || []);
    if (pool.length) chosen.push({slot: name, item: pick(pool)});
  });

  // Fill table
  const tbody = document.getElementById("order-body");
  tbody.innerHTML = "";
  let totalCal = 0;
  const allergenSet = new Set();

  chosen.forEach(({slot, item}) => {
    const cal = parseFloat(item.cal) || 0;
    totalCal += cal;
    item.allergens.forEach(a => allergenSet.add(a));
    const tr = document.createElement("tr");
    tr.innerHTML =
      `<td class="slot-name">${esc(slot)}</td>` +
      `<td>${esc(item.item)}</td>` +
      `<td class="cal">${item.cal}</td>`;
    tbody.appendChild(tr);
  });

  document.getElementById("total-cal").textContent = Math.round(totalCal);

  const badges = document.getElementById("allergen-badges");
  if (allergenSet.size === 0) {
    badges.innerHTML = '<span class="none-badge">None of the 6 tracked allergens!</span>';
  } else {
    badges.innerHTML = [...allergenSet].sort()
      .map(a => `<span class="a-badge">${esc(a)}</span>`).join(" ");
  }

  document.getElementById("order-area").style.display = "block";
}

function esc(s){ return String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c])); }
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
