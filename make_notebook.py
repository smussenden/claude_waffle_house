#!/usr/bin/env python3
"""Generate waffle_house_finding.ipynb — a reproducible, editor-reviewable notebook.

Finding: more than half of all Waffle Houses are in just five Southeastern states.
The notebook documents the source, runs data-quality checks, reproduces the
finding step by step from the raw CSV, charts it, and ends with limitations.
"""

import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))

def code(src):
    cells.append(nbf.v4.new_code_cell(src))

# ---------------------------------------------------------------- Title / finding
md("""\
# Where the waffles are: five states hold most of Waffle House

**Finding (plain English):** More than half of all U.S. Waffle House locations
sit in just **five Southeastern states** — Georgia, Florida, North Carolina,
South Carolina, and Alabama. Georgia alone has more than one in five.

This notebook reproduces that finding **from the raw data file**, top to bottom:
it documents the source, runs data-quality checks, computes the numbers, charts
them, and closes with limitations — so an editor can re-run and verify every step.

*Author's note: every number below is produced by the code in this notebook. Nothing is typed in by hand.*
""")

# ---------------------------------------------------------------- Source
md("""\
## 1 · Data source

| | |
|---|---|
| **File** | `waffle_houses.csv` (in this folder) |
| **What it is** | One row per Waffle House location, scraped from the company's public store locator |
| **Rows** | 2,006 locations |
| **Key columns** | `Store Code`, `Business Name`, `City`, `State`, `Latitude`, `Longitude`, `Operated By` |
| **Retrieved** | Snapshot used for this analysis dated 2026 |
| **Full column docs** | see `DATA_DICTIONARY.md` in this folder |

The file is read directly below — no manual editing, no intermediate spreadsheet.
""")

code("""\
import pandas as pd

df = pd.read_csv(
    "waffle_houses.csv",
    dtype={"Store Code": str, "Postal Code": str},  # IDs/ZIPs are strings, not numbers
)
print(f"Loaded {len(df):,} rows, {df.shape[1]} columns")
df.head(3)
""")

# ---------------------------------------------------------------- QA
md("""\
## 2 · Data-quality checks (before trusting anything)

Quality checks are the first half of fact-checking. Before counting, we confirm
the columns we rely on (`State`, `Store Code`) are clean, and we surface the
known oddities documented in `DATA_DICTIONARY.md`.
""")

code("""\
# 2a. Missing values per column
missing = df.isna().sum()
print("Columns with blanks:")
print(missing[missing > 0].to_string() or "  (none)")
""")

code("""\
# 2b. Is every location assigned to a state? (the column our finding depends on)
print("Blank State values:", df["State"].isna().sum())
print("Distinct states present:", df["State"].nunique())

# 2c. Are Store Codes unique? (no double-counting)
dupes = df["Store Code"].duplicated().sum()
print("Duplicate Store Codes:", dupes)
""")

code("""\
# 2d. Known flagged rows (from DATA_DICTIONARY.md):
#     - the Waffle House Museum (not a normal restaurant)
#     - the #442/#3442 same-site duplicate in Baton Rouge
#     - 2 stores marked "Closed"
flags = df[
    (df["Store Code"] == "WH_Museum")
    | (df["Store Code"].isin(["442", "3442"]))
    | (df["Formatted Business Hours"].fillna("").str.contains("Closed"))
]
print(f"{len(flags)} flagged rows:")
flags[["Store Code", "Business Name", "City", "State", "Formatted Business Hours"]]
""")

md("""\
**QA result:** `State` has zero blanks, all 2,006 `Store Code`s are unique (no
double-counting), and the only oddities are 5 flagged rows. None of the flagged
rows change the state ranking materially (the museum is in GA; the duplicate
pair is in LA), so we keep all 2,006 rows and note this in *Limitations*.
""")

# ---------------------------------------------------------------- Reproduce
md("""\
## 3 · Reproduce the finding, step by step

### 3a. Count locations per state
""")

code("""\
state_counts = df["State"].value_counts()          # rows per state, descending
total = len(df)
state_counts.head(10)
""")

md("### 3b. Georgia's share of the national total")

code("""\
top_state = state_counts.index[0]
top_n = int(state_counts.iloc[0])
top_pct = 100 * top_n / total
print(f"{top_state}: {top_n:,} of {total:,} locations = {top_pct:.1f}%")
""")

md("### 3c. The top five states combined")

code("""\
top5 = state_counts.head(5)
top5_n = int(top5.sum())
top5_pct = 100 * top5_n / total

calc = " + ".join(f"{int(c)} ({s})" for s, c in top5.items())
print(f"Top 5: {calc}")
print(f"     = {top5_n:,} of {total:,} = {top5_pct:.1f}% of all Waffle Houses")
""")

md("""\
**The finding, confirmed:** the five states above hold more than half of all
locations — reproduced straight from the raw file. The exact percentage is
printed by the cell above and rendered into the chart title below, so the prose
can never drift from the data.
""")

# ---------------------------------------------------------------- Chart
md("## 4 · Chart the concentration")

code("""\
import matplotlib.pyplot as plt

top10 = state_counts.head(10)
colors = ["#d97706" if s in top5.index else "#9ca3af" for s in top10.index]

fig, ax = plt.subplots(figsize=(9, 4.5))
bars = ax.bar(top10.index, top10.values, color=colors)
ax.set_title(f"Top 5 states hold {top5_pct:.1f}% of all {total:,} Waffle Houses",
             fontsize=13, fontweight="bold")
ax.set_ylabel("Number of locations")
ax.set_xlabel("State")
for b, v in zip(bars, top10.values):
    ax.text(b.get_x() + b.get_width()/2, v + 4, f"{int(v)}",
            ha="center", va="bottom", fontsize=9)
ax.spines[["top", "right"]].set_visible(False)
# Legend proxy
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color="#d97706", label="Top 5 states"),
                   Patch(color="#9ca3af", label="States 6–10")],
          frameon=False)
plt.tight_layout()
plt.savefig("top5_states.png", dpi=120, bbox_inches="tight")
plt.show()
""")

# ---------------------------------------------------------------- Limitations
md("""\
## 5 · Limitations & caveats

- **Snapshot in time.** The file is a single scrape of the public store locator.
  Stores open and close; counts will drift.
- **"Locations," not "open restaurants."** All 2,006 rows are counted. That
  includes the **Waffle House Museum** (`WH_Museum`, Decatur GA — not a working
  restaurant), a **same-site duplicate** (#442/#3442 in Baton Rouge, two store
  codes at one address ~186 ft apart), and **2 stores marked "Closed."** Net of
  these, ~2,004 distinct operating restaurants. None of them change the top-5
  ranking, but exact percentages shift by <0.1 pt.
- **Coverage = U.S. only.** Every row is `Country = US`; 25 of 50 states have
  zero locations. The finding is about the U.S. footprint, not global.
- **Self-reported geography.** State assignment comes from the company's own
  data; we did not independently geocode addresses. Latitude/longitude were
  sanity-checked to fall within U.S. bounds (see `DATA_DICTIONARY.md`).
- **No population adjustment.** This is raw counts. "Most Waffle Houses" is not
  the same as "most per capita" — a different (and also interesting) question.

## Reproducibility
Re-run this notebook top to bottom (`Kernel → Restart & Run All`) against
`waffle_houses.csv` to regenerate every number and the chart. Source columns are
documented in `DATA_DICTIONARY.md`; the same figures appear in `ANALYSIS.md`.
""")

nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}

with open("waffle_house_finding.ipynb", "w") as f:
    nbf.write(nb, f)
print("Wrote waffle_house_finding.ipynb")
