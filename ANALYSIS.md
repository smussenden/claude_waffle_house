# Waffle House Locations — Analysis

**Source:** `waffle_houses.csv` · **Total rows:** 2,006 · **Date:** 2026-06-19

*All 2,006 rows are included in these counts. Flagged rows: the Waffle House Museum (`WH_Museum`, Decatur GA), the #442/#3442 same-site duplicate (2363 College Dr, Baton Rouge LA), and 2 stores marked Closed (Xenia OH #2473, Buchanan GA #2475). See `DATA_DICTIONARY.md §4/4a` for details.*

---

## 1 · Which state has the most Waffle Houses?

**Georgia (GA) leads with 442 locations — 22.0% of all 2,006.**

Calculation: 442 ÷ 2006 × 100 = 22.0%

| Rank | State | Count | Share |
|------|-------|------:|------:|
| 1 | Georgia (GA) | 442 | 22.0% |
| 2 | Florida (FL) | 188 | 9.4% |
| 3 | North Carolina (NC) | 186 | 9.3% |
| 4 | South Carolina (SC) | 175 | 8.7% |
| 5 | Alabama (AL) | 156 | 7.8% |
| 6 | Tennessee (TN) | 139 | 6.9% |
| 7 | Texas (TX) | 127 | 6.3% |
| 8 | Louisiana (LA) | 103 | 5.1% |
| 9 | Mississippi (MS) | 88 | 4.4% |
| 10 | Ohio (OH) | 83 | 4.1% |

---

## 2 · What share of all locations are in the top five states?

**The top five states account for 1,147 locations — 57.2% of all 2,006.**

Calculation: 442 (GA) + 188 (FL) + 186 (NC) + 175 (SC) + 156 (AL) = 1147 ÷ 2006 × 100 = 57.2%

| Rank | State | Count | Share |
|------|-------|------:|------:|
| 1 | Georgia (GA) | 442 | 22.0% |
| 2 | Florida (FL) | 188 | 9.4% |
| 3 | North Carolina (NC) | 186 | 9.3% |
| 4 | South Carolina (SC) | 175 | 8.7% |
| 5 | Alabama (AL) | 156 | 7.8% |
| — | **Top 5 total** | **1,147** | **57.2%** |

---

## 3 · Locations by operator type

**Corporate stores dominate: nearly two-thirds of all Waffle Houses are operated directly by Waffle House, Inc.; about one-third by fully owned subsidiaries; under 7% by franchisees.**

| Operator type | Count | Share | Examples |
|---------------|------:|------:|---------|
| Corporate | 1,251 | 62.4% | WAFFLE HOUSE, INC |
| Subsidiary | 627 | 31.3% | FULLY OWNED SUBSIDIARY: EAST COAST WAFFLES, INC.; FULLY OWNED SUBSIDIARY: MID SOUTH WAFFLES, INC.; FULLY OWNED SUBSIDIARY: MIDWEST WAFFLES, INC. (+1 more) |
| Franchise | 127 | 6.3% | FRANCHISE : AMARILLO WAFFLES, LLC.; FRANCHISE : CHOO-CHOO WAFFLES; FRANCHISE : D.LOVE'S RESTAURANTS,LLC. (+7 more) |
| Unknown | 1 | 0.0% |  |

**How the types are defined** (from the `Operated By` column):
- **Corporate** — exact value `WAFFLE HOUSE, INC` (1,251 stores)
- **Subsidiary** — starts with `FULLY OWNED SUBSIDIARY:` (4 subsidiaries: East Coast Waffles, Mid South Waffles, Midwest Waffles, Ozark Waffles)
- **Franchise** — starts with `FRANCHISE :` (10 franchisees, e.g. Rocky Top Waffles, Lookout Waffles)
- **Unknown** — blank `Operated By` field (1 store: the museum)

---

## 4 · Which single city has the most Waffle Houses?

**Atlanta, GA has the most with 20 locations.**

*(Cities normalized to uppercase and joined with state to disambiguate same-name cities in different states.)*

| Rank | City, State | Count |
|------|-------------|------:|
| 1 | Atlanta, GA | 20 |
| 2 | Pensacola, FL | 16 |
| 3 | Marietta, GA | 16 |
| 4 | Nashville, TN | 15 |
| 5 | Augusta, GA | 14 |

---

## 5 · How many states have zero Waffle Houses?

**25 of 50 US states have no Waffle House locations in this dataset.**

The data covers 25 states (plus DC is not separately counted — all locations are filed under state codes). The 25 states with zero locations:

Alaska, California, Connecticut, Hawaii, Idaho, Iowa, Maine, Massachusetts, Michigan, Minnesota, Montana, Nebraska, Nevada, New Hampshire, New Jersey, New York, North Dakota, Oregon, Rhode Island, South Dakota, Utah, Vermont, Washington, Wisconsin, Wyoming

*(These are all western, mountain, New England, and upper-Midwest states — consistent with Waffle House's historically Southeast-concentrated footprint.)*

---

## 6 · The four compass-edge Waffle Houses

*Each is the store with the extreme latitude or longitude in the raw CSV — verified by sorting all 2,006 rows on that coordinate.*

### Furthest north: lat 41.78379°
  - **#1830** Waffle House #1830 — 2850 G. H. Drive, Austinburg, OH 44010
### Furthest south: lat 25.10050°
  - **#1310** Waffle House #1310 — 100270 Overseas Hwy, Key Largo, FL 33037
### Furthest east: lon -75.33919°
  - **#1691** Waffle House #1691 — 2101 Cherry Lane, Bethlehem, PA 18015
### Furthest west: lon -112.34128°
  - **#481** Waffle House #481 — 820 North Dysart Rd, Goodyear, AZ 85338

| Direction | Store | Address | Coordinate |
|-----------|-------|---------|------------|
| North | #1830 Waffle House #1830 | 2850 G. H. Drive, Austinburg, OH | lat: 41.78379° |
| South | #1310 Waffle House #1310 | 100270 Overseas Hwy, Key Largo, FL | lat: 25.10050° |
| East | #1691 Waffle House #1691 | 2101 Cherry Lane, Bethlehem, PA | lon: -75.33919° |
| West | #481 Waffle House #481 | 820 North Dysart Rd, Goodyear, AZ | lon: -112.34128° |