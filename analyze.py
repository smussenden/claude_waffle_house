#!/usr/bin/env python3
"""Analyze waffle_houses.csv and write ANALYSIS.md.

Answers six worksheet questions; uses all 2,006 rows with flagged
rows (museum, #442/#3442 duplicate, 2 closed stores) noted where
they affect the numbers.
"""

import csv
from collections import Counter
from textwrap import dedent

CSV = "waffle_houses.csv"
OUT = "ANALYSIS.md"

# All 50 US state abbreviations
ALL_STATES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN",
    "IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV",
    "NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN",
    "TX","UT","VT","VA","WA","WV","WI","WY",
}
STATE_NAMES = {
    "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California",
    "CO":"Colorado","CT":"Connecticut","DE":"Delaware","FL":"Florida","GA":"Georgia",
    "HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa",
    "KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland",
    "MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi",
    "MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire",
    "NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
    "ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania",
    "RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee",
    "TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington",
    "WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming",
}

DUPLICATE_CODES = {"442", "3442"}
FLAGGED_NOTE = (
    "*All 2,006 rows are included in these counts. "
    "Flagged rows: the Waffle House Museum (`WH_Museum`, Decatur GA), "
    "the #442/#3442 same-site duplicate (2363 College Dr, Baton Rouge LA), "
    "and 2 stores marked Closed (Xenia OH #2473, Buchanan GA #2475). "
    "See `DATA_DICTIONARY.md §4/4a` for details.*"
)


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


def fmt_row(r, note=""):
    loc = f"{r['Address'].title()}, {r['City'].title()}, {r['State']} {r['Postal Code']}"
    extra = f" ⚑ *{note}*" if note else ""
    return f"  - **#{r['Store Code']}** {r['Business Name']} — {loc}{extra}"


def main():
    rows = []
    with open(CSV, newline="") as f:
        for r in csv.DictReader(f):
            r["_family"] = operator_family(r["Operated By"])
            r["_flag"] = row_flag(r)
            r["_lat"] = float(r["Latitude"])
            r["_lon"] = float(r["Longitude"])
            r["_city_key"] = (r["City"].upper().strip(), r["State"])
            rows.append(r)

    n = len(rows)
    sections = []

    # ------------------------------------------------------------------
    # Q1 — Which state has the most Waffle Houses, and what share?
    # ------------------------------------------------------------------
    state_counts = Counter(r["State"] for r in rows)
    top_state, top_n = state_counts.most_common(1)[0]
    top_pct = 100 * top_n / n
    sections.append(f"""\
## 1 · Which state has the most Waffle Houses?

**{STATE_NAMES[top_state]} ({top_state}) leads with {top_n:,} locations — {top_pct:.1f}% of all {n:,}.**

Calculation: {top_n} ÷ {n} × 100 = {top_pct:.1f}%

| Rank | State | Count | Share |
|------|-------|------:|------:|
""" + "\n".join(
        f"| {i+1} | {STATE_NAMES[s]} ({s}) | {c:,} | {100*c/n:.1f}% |"
        for i, (s, c) in enumerate(state_counts.most_common(10))
    ))

    # ------------------------------------------------------------------
    # Q2 — What share of all locations are in the top five states?
    # ------------------------------------------------------------------
    top5 = state_counts.most_common(5)
    top5_n = sum(c for _, c in top5)
    top5_pct = 100 * top5_n / n
    calc_parts = " + ".join(f"{c} ({s})" for s, c in top5)
    sections.append(f"""\
## 2 · What share of all locations are in the top five states?

**The top five states account for {top5_n:,} locations — {top5_pct:.1f}% of all {n:,}.**

Calculation: {calc_parts} = {top5_n} ÷ {n} × 100 = {top5_pct:.1f}%

| Rank | State | Count | Share |
|------|-------|------:|------:|
""" + "\n".join(
        f"| {i+1} | {STATE_NAMES[s]} ({s}) | {c:,} | {100*c/n:.1f}% |"
        for i, (s, c) in enumerate(top5)
    ) + f"\n| — | **Top 5 total** | **{top5_n:,}** | **{top5_pct:.1f}%** |")

    # ------------------------------------------------------------------
    # Q3 — Operator type breakdown
    # ------------------------------------------------------------------
    family_counts = Counter(r["_family"] for r in rows)
    sections.append("""\
## 3 · Locations by operator type

**Corporate stores dominate: nearly two-thirds of all Waffle Houses are operated directly \
by Waffle House, Inc.; about one-third by fully owned subsidiaries; \
under 7% by franchisees.**

| Operator type | Count | Share | Examples |
|---------------|------:|------:|---------|
""" + "\n".join(
        f"| {fam} | {c:,} | {100*c/n:.1f}% | {_family_examples(rows, fam)} |"
        for fam, c in family_counts.most_common()
    ) + """

**How the types are defined** (from the `Operated By` column):
- **Corporate** — exact value `WAFFLE HOUSE, INC` (1,251 stores)
- **Subsidiary** — starts with `FULLY OWNED SUBSIDIARY:` (4 subsidiaries: East Coast Waffles, Mid South Waffles, Midwest Waffles, Ozark Waffles)
- **Franchise** — starts with `FRANCHISE :` (10 franchisees, e.g. Rocky Top Waffles, Lookout Waffles)
- **Unknown** — blank `Operated By` field (1 store: the museum)""")

    # ------------------------------------------------------------------
    # Q4 — Which single city has the most?
    # ------------------------------------------------------------------
    city_counts = Counter(r["_city_key"] for r in rows)
    top_city_key, top_city_n = city_counts.most_common(1)[0]
    city_display = f"{top_city_key[0].title()}, {top_city_key[1]}"
    top5_cities = city_counts.most_common(5)
    sections.append(f"""\
## 4 · Which single city has the most Waffle Houses?

**{city_display} has the most with {top_city_n} locations.**

*(Cities normalized to uppercase and joined with state to disambiguate same-name cities in different states.)*

| Rank | City, State | Count |
|------|-------------|------:|
""" + "\n".join(
        f"| {i+1} | {c[0].title()}, {c[1]} | {cnt} |"
        for i, (c, cnt) in enumerate(top5_cities)
    ))

    # ------------------------------------------------------------------
    # Q5 — How many states have zero Waffle Houses?
    # ------------------------------------------------------------------
    present = set(state_counts.keys())
    zero_states = sorted(ALL_STATES - present, key=lambda s: STATE_NAMES[s])
    sections.append(f"""\
## 5 · How many states have zero Waffle Houses?

**{len(zero_states)} of 50 US states have no Waffle House locations in this dataset.**

The data covers {len(present)} states (plus DC is not separately counted — \
all locations are filed under state codes). The {len(zero_states)} states with zero locations:

{', '.join(STATE_NAMES[s] for s in zero_states)}

*(These are all western, mountain, New England, and upper-Midwest states — \
consistent with Waffle House's historically Southeast-concentrated footprint.)*""")

    # ------------------------------------------------------------------
    # Q6 — Furthest north, south, east, west
    # ------------------------------------------------------------------
    north = max(rows, key=lambda r: r["_lat"])
    south = min(rows, key=lambda r: r["_lat"])
    east  = max(rows, key=lambda r: r["_lon"])   # least negative = furthest east
    west  = min(rows, key=lambda r: r["_lon"])   # most negative = furthest west

    def compass_row(label, r, coord_label, coord_val):
        flag = f" ⚑ *{r['_flag']}*" if r["_flag"] else ""
        return (
            f"### Furthest {label}: {coord_label} {coord_val:.5f}°\n"
            f"{fmt_row(r)}{flag}\n"
        )

    sections.append(
        "## 6 · The four compass-edge Waffle Houses\n\n"
        "*Each is the store with the extreme latitude or longitude in the raw CSV "
        "— verified by sorting all 2,006 rows on that coordinate.*\n\n"
        + compass_row("north", north, "lat", north["_lat"])
        + compass_row("south", south, "lat", south["_lat"])
        + compass_row("east",  east,  "lon", east["_lon"])
        + compass_row("west",  west,  "lon", west["_lon"])
        + "\n| Direction | Store | Address | Coordinate |\n"
        + "|-----------|-------|---------|------------|\n"
        + "\n".join(
            f"| {d} | #{r['Store Code']} {r['Business Name']} | "
            f"{r['Address'].title()}, {r['City'].title()}, {r['State']} | "
            f"{coord}: {val:.5f}° |"
            for d, r, coord, val in [
                ("North", north, "lat", north["_lat"]),
                ("South", south, "lat", south["_lat"]),
                ("East",  east,  "lon", east["_lon"]),
                ("West",  west,  "lon", west["_lon"]),
            ]
        )
    )

    # ------------------------------------------------------------------
    # Write ANALYSIS.md
    # ------------------------------------------------------------------
    md = f"""\
# Waffle House Locations — Analysis

**Source:** `waffle_houses.csv` · **Total rows:** {n:,} · **Date:** 2026-06-19

{FLAGGED_NOTE}

---

""" + "\n\n---\n\n".join(sections)

    with open(OUT, "w") as f:
        f.write(md)

    print(f"Wrote {OUT}")

    # Terminal verification printout
    print(f"\n=== VERIFICATION ===")
    print(f"Q1 top state: {top_state} = {top_n} ({top_pct:.1f}%)")
    print(f"Q2 top-5 sum: {top5_n} ({top5_pct:.1f}%) — {calc_parts}")
    print(f"Q3 families: { {k:v for k,v in family_counts.items()} }")
    print(f"Q4 top city: {city_display} = {top_city_n}")
    print(f"Q5 zero-WH states: {len(zero_states)}")
    print(f"Q6 N={north['Store Code']} lat={north['_lat']} | S={south['Store Code']} lat={south['_lat']}")
    print(f"   E={east['Store Code']} lon={east['_lon']} | W={west['Store Code']} lon={west['_lon']}")


def _family_examples(rows, fam):
    ops = sorted({r["Operated By"] for r in rows if r["_family"] == fam and r["Operated By"]})
    sample = ops[:3]
    more = len(ops) - 3
    out = "; ".join(sample)
    if more > 0:
        out += f" (+{more} more)"
    return out


if __name__ == "__main__":
    main()
