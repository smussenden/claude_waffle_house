# Data Dictionary — `waffle_houses.csv`

**Source file:** `waffle_houses.csv`
**Rows:** 2,006 data rows (+ 1 header row = 2,007 lines)
**Columns:** 14
**Coverage:** 2,006 US locations across 25 states
**Documented:** 2026-06-19

---

## 1 · Column dictionary

| # | Column | Type | Description | Example | Notes / gotchas |
|---|--------|------|-------------|---------|-----------------|
| 1 | **Store Code** | String (usually integer) | Unique store identifier | `100` | All numeric **except** one row: `WH_Museum`. Treat as a **string**, not an integer — see §3. No duplicates. |
| 2 | **Business Name** | String | Display name, includes the store number | `Waffle House #100` | Museum row reads `Waffle House Museum #WH_Museum`. |
| 3 | **Address** | String | Street address | `2842 PANOLA RD` | Mostly UPPERCASE; the museum row is mixed-case. |
| 4 | **City** | String | City name | `LITHONIA` | UPPERCASE for all rows **except** `Decatur` (the museum). See §4. |
| 5 | **State** | String (2-letter) | USPS state abbreviation | `GA` | 25 distinct values, all valid US states. No blanks. |
| 6 | **Postal Code** | String | 5-digit ZIP code | `30058` | All 2,006 are clean 5-digit. Store as **string** to be safe (none start with 0 in this set, but ZIPs can). |
| 7 | **Country** | String | Country code | `US` | Constant — `US` for every row. No analytic value. |
| 8 | **Latitude** | Float | Decimal degrees (WGS84) | `33.704706` | Range 25.10 → 41.78. All within plausible US bounds. No blanks/bad values. |
| 9 | **Longitude** | Float | Decimal degrees (WGS84) | `-84.169849` | Range −112.34 → −75.34. All negative (western hemisphere), as expected. No blanks/bad values. |
| 10 | **Phone Number** | String | Contact phone | `(770) 981-1914` | Two formats — see §4. 228 rows hold **two** numbers separated by `; `. |
| 11 | **Website URL** | String | Location page | `https://locations.wafflehouse.com///lithonia-ga-100` | **Every** URL contains a triple slash `///` — a source quirk, not corruption. |
| 12 | **Operated By** | String (categorical) | Operating entity | `WAFFLE HOUSE, INC` | 16 distinct values in 3 families: corporate, subsidiary, franchise. 1 blank. See §2 & §3. |
| 13 | **Online Order Link** | String (URL) | Online ordering page | `https://order.wafflehouse.com/menu/waffle-house-100` | 3 blanks. |
| 14 | **Formatted Business Hours** | String | Operating hours | `Monday - Sunday\| 24 hours` | Pipe-delimited `days\| hours`. 1,998 are 24-hour; 6 outliers + 2 blanks. See §2 & §4. |

---

## 2 · Categorical breakdowns

### Operator type (column `Operated By`)
Three operating families, derived from the prefix:

| Family | Count | Share |
|--------|------:|------:|
| Corporate (`WAFFLE HOUSE, INC`) | 1,251 | 62.4% |
| Fully owned subsidiary (`FULLY OWNED SUBSIDIARY: …`) | 627 | 31.3% |
| Franchise (`FRANCHISE : …`) | 127 | 6.3% |
| *(blank)* | 1 | <0.1% |

Subsidiaries: East Coast Waffles (212), Mid South Waffles (169), Midwest Waffles (143), Ozark Waffles (103).
Franchises: 10 distinct franchisees (Rocky Top 37, Lookout 23, J. Thomas 19, Choo-Choo 18, etc.).

### States (top of 25)
GA 442 · FL 188 · NC 186 · SC 175 · AL 156 · TN 139 · TX 127 · LA 103 · MS 88 · OH 83 … down to IL 2 · NM 1. Heavily Southeast-concentrated.

---

## 3 · Data-quality checks

| Check | Result |
|-------|--------|
| **Missing values** | `Operated By` 1 blank · `Online Order Link` 3 blanks · `Formatted Business Hours` 2 blanks. All other columns 100% populated. |
| **Duplicate Store Codes** | None — all 2,006 unique. |
| **Fully duplicated rows** | None. |
| **Duplicate lat/long pairs** | None. |
| **Store Code type** | 2,005 numeric, **1 non-numeric** (`WH_Museum`). ⚠️ Do not cast the column to integer — it will error. |
| **Latitude / Longitude type** | All parse as floats; all within US bounds (lat 25.1–41.8, lon −112.3 to −75.3). |
| **Postal Code** | All 2,006 are valid 5-digit strings. |
| **Country** | Constant `US`. |

---

## 4 · Inconsistencies that could affect analysis

1. **The "Waffle House Museum" is not a normal restaurant.** Store Code `WH_Museum`, in Decatur, GA. It is mixed-case, has a blank operator, blank order link, blank hours, and a non-`(xxx) xxx-xxxx` phone. **Decide whether to include or exclude it** before counting locations — it can shift "exact" counts by one and breaks any integer cast on Store Code.

2. **Phone Number has two formats.** 1,777 rows use `(xxx) xxx-xxxx`; **228 rows contain two numbers** joined by `; ` (e.g. `(706) 956-4560; (706) 356-9921`); the museum uses `770-326-7086`. Split on `; ` before parsing.

3. **City casing is not uniform.** Every city is UPPERCASE except `Decatur` (museum). Normalize casing before grouping by city, or the museum could form its own group.

4. **Business hours are nearly constant.** 1,998 of 2,006 are "24 hours." Outliers: 2 marked **Closed** (Xenia OH #2473, Buchanan GA #2475), 4 with limited hours, and 2 blank. The two "Closed" stores may be **temporarily/permanently closed** — flag before treating the file as "open locations."

5. **Website URLs all contain `///`.** A consistent source-formatting artifact (`locations.wafflehouse.com///…`). Harmless but worth noting if you parse or validate URLs.

6. **`Country` adds nothing** — single value `US`. Safe to ignore for analysis.

---

## 5 · Recommended handling

- Read **Store Code** and **Postal Code** as **strings**.
- Treat **lat/long** as floats (clean, no nulls).
- For location counts, **state your decision on the museum row** and the two "Closed" stores explicitly.
- Derive an **operator-family** column (Corporate / Subsidiary / Franchise) from `Operated By` for cleaner grouping.
- When using phone numbers, **split the 228 dual-number rows**.
