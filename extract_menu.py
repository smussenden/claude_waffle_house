#!/usr/bin/env python3
"""Extract the Waffle House nutritional menu PDF into a clean allergen CSV.

Reads Menu-Nutritionals-2026-05-05.pdf (10 pages), parses each menu line into
one item with nutrition + an allergen set, rolls up composite "total" rows'
allergens from their components, and writes menu_allergens.csv.

Run `python3 extract_menu.py` (also prints a parsed-vs-raw verification).
"""

import csv
import re
import pdfplumber

PDF = "Menu-Nutritionals-2026-05-05.pdf"
OUT = "menu_allergens.csv"

CANON = {"Egg", "Milk", "Soy", "Wheat", "Tree Nuts", "Peanut"}

# A data row ends with 10 nutrition numbers (possibly decimals) then an
# optional allergen phrase. Capture: name, the 10 numbers, optional allergen tail.
_NUM = r"\d+(?:\.\d+)?"
ROW_RE = re.compile(
    r"^(?P<name>.*?)\s+"
    rf"(?P<cal>{_NUM})\s+(?P<fat>{_NUM})\s+(?P<satfat>{_NUM})\s+(?P<transfat>{_NUM})\s+"
    rf"(?P<chol>{_NUM})\s+(?P<sodium>{_NUM})\s+(?P<carbs>{_NUM})\s+(?P<fiber>{_NUM})\s+"
    rf"(?P<sugars>{_NUM})\s+(?P<protein>{_NUM})"
    r"(?:\s+(?P<allergens>[A-Za-z][A-Za-z,. ]*))?\s*$"
)
NUTRI_COLS = ["cal", "fat", "satfat", "transfat", "chol", "sodium",
              "carbs", "fiber", "sugars", "protein"]


def parse_allergens(raw):
    """Turn an allergen phrase into a canonical sorted list.

    Handles the source quirk 'Soy Wheat' (no comma) by also splitting on the
    space between two known allergen words.
    """
    if not raw:
        return []
    # normalize separators: commas, periods, and the 'Soy Wheat' no-comma case
    raw = raw.replace("Tree Nuts", "TreeNuts")        # protect the 2-word allergen
    parts = re.split(r"[,.\s]+", raw.strip())
    out = set()
    for p in parts:
        p = p.strip()
        if not p:
            continue
        name = "Tree Nuts" if p == "TreeNuts" else p
        if name in CANON:
            out.add(name)
    return sorted(out)


def is_colheader(s):
    return "Cal Fat" in s or s.startswith("Name ") or s.startswith("(g)")


def is_allcaps_header(line):
    # All-caps section titles (may contain ™, &, /, apostrophes, digits)
    s = line.replace("™", "").strip()
    letters = [c for c in s if c.isalpha()]
    return bool(letters) and s == s.upper() and "CAL" not in s and len(s) > 3


def is_noise(line):
    return (not line.strip()
            or is_colheader(line)
            or line.startswith("Updated ")
            or re.fullmatch(r"\s*\d+\s*", line) is not None)  # bare page number


def _num(s):
    f = float(s)
    return int(f) if f == int(f) else f


def main():
    # Flatten every line with its page number so we can look ahead (for
    # title-case section headers and names that wrap onto the next line).
    flat = []
    with pdfplumber.open(PDF) as pdf:
        for pageno, page in enumerate(pdf.pages, start=1):
            for raw_line in page.extract_text().split("\n"):
                flat.append((pageno, raw_line.strip()))

    rows = []
    section = ""
    k = 0
    while k < len(flat):
        pageno, line = flat[k]
        nxt = flat[k + 1][1] if k + 1 < len(flat) else ""
        if is_noise(line):
            k += 1
            continue
        # Section header: ALL-CAPS, or any non-row line immediately before a
        # "Name Cal Fat…" column header (catches title-case headers like
        # "Pies", "Beverages", "100% Angus Beef Hamburgers").
        if is_allcaps_header(line) or (is_colheader(nxt) and not ROW_RE.match(line)):
            section = line.replace("™", "").strip()
            k += 1
            continue

        m = ROW_RE.match(line)
        consumed = 1
        if not m:
            # Name wrapped onto two lines: join this line with the next.
            joined = f"{line} {nxt}".strip()
            m = ROW_RE.match(joined)
            if m:
                line = joined
                consumed = 2
            else:
                k += 1
                continue

        name = m.group("name").strip()
        includes = name.startswith("Includes:")
        name = re.sub(r"^(Includes:|Plus your choice of:\s*|:\s*)", "", name).strip()
        if not name:
            k += consumed
            continue
        item = {
            "section": section,
            "item": name,
            "page": pageno,
            "allergens": parse_allergens(m.group("allergens")),
            "_includes": includes,
            "_raw": line,
            "is_composite": False,
        }
        for col in NUTRI_COLS:
            item[col] = _num(m.group(col))
        rows.append(item)
        k += consumed

    # --- composite roll-up ---------------------------------------------------
    # A composite parent is a non-"Includes:" row immediately followed by an
    # "Includes:" row. Its children are the contiguous run of following rows in
    # the same section, up to (but not including) the next composite parent.
    # Each child also remains its own item with its own allergens; the parent
    # gains the UNION so a composite total never falsely reads as allergen-free.
    n = len(rows)
    composites = 0
    for i in range(n):
        is_parent = (not rows[i]["_includes"]
                     and i + 1 < n and rows[i + 1]["_includes"])
        if not is_parent:
            continue
        parent = rows[i]
        parent["is_composite"] = True
        combined = set(parent["allergens"])
        j = i + 1
        while j < n and rows[j]["section"] == parent["section"]:
            # stop at the next composite parent
            if not rows[j]["_includes"] and j + 1 < n and rows[j + 1]["_includes"]:
                break
            combined |= set(rows[j]["allergens"])
            j += 1
        parent["allergens"] = sorted(combined)
        composites += 1

    _write(rows)
    _verify(rows, composites)


def _write(rows):
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["section", "item", "is_composite", *NUTRI_COLS,
                    "allergens", "page"])
        for r in rows:
            w.writerow([r["section"], r["item"], r["is_composite"],
                        *[r[c] for c in NUTRI_COLS],
                        "; ".join(r["allergens"]), r["page"]])
    print(f"Wrote {OUT} ({len(rows)} items)")


def _verify(rows, composites):
    from collections import Counter
    print("\n=== VERIFICATION: parsed vs raw ===")
    wanted = ["Sausage Egg & Cheese Hashbrown Bowl", "Sausage Sandwich",
              "Pecans", "Peanut Butter Chips", "Bacon", "Classic Waffle"]
    for name in wanted:
        r = next((x for x in rows if x["item"] == name), None)
        if r:
            print(f"\nITEM: {r['item']}  (section={r['section']}, composite={r['is_composite']})")
            print(f"  RAW : {r['_raw']}")
            print(f"  PARSED allergens: {r['allergens'] or '(none listed)'}")
    af = Counter()
    for r in rows:
        for a in r["allergens"]:
            af[a] += 1
    print("\n=== TOTALS ===")
    print(f"items: {len(rows)} | composites rolled up: {composites}")
    print(f"allergen frequency: {dict(af.most_common())}")
    print(f"items with NO listed allergens: {sum(1 for r in rows if not r['allergens'])}")


if __name__ == "__main__":
    main()
