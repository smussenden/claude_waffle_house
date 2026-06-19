# RUN OF SHOW — Intro to Claude Code for Reporters
### "From a raw CSV to a story an editor can fact-check"

**Total: 3.5 hrs · Desktop app · Audience: investigative reporters, spreadsheet-fluent, no coding.**

**Before students arrive**
- Put the four links into the class page: class page itself, Claude signup, desktop app download, and the **class-folder zip**.
- The zip students download contains `waffle_houses.csv`, `Menu-Nutritionals-2026-05-05.pdf`, and `WORKSHEET.md` — and nothing else.
- Keep the `prepared/` folder on YOUR machine only — it's your safety net, not in the students' zip.
- Open the `prepared/` artifacts once yourself so you know what "good" looks like.

**How to read this script**
- 🗣️ = say this · ⌨️ = type this prompt into Claude Code · 👀 = what to expect · 🧯 = fallback if it goes sideways · 💡 = teaching point · 🔦 = **FEATURE SPOTLIGHT** (pause and show this feature).
- Prompts are starting points. Claude's exact wording will vary — that's fine and worth pointing out.
- UI labels move around as the app updates — these spotlights name features by *what they do*; confirm exact buttons/menus on your machine before class.

---

## INTRO (2 min)

🗣️ "You have questions. You have data. What you're missing is the ability to write code to answer them — maybe the question's too fiddly, the file's too big for a spreadsheet, or it needs joining several sources. Today we're deliberately **not** doing anything hugely complex. The point is for you to walk out comfortable in the environment and confident driving it."

🗣️ "Concretely: you'll turn a spreadsheet of every Waffle House in America into documentation, a map, a real analysis, and a notebook your editor could re-run to check your work — and you won't write a line of code. You'll *ask*."

---

## BLOCK 0 — Setup (20–30 min)

*Pre-flight. Everything in this block is on the class page; walk it top to bottom.*

1. **Open the class page and follow along** → `[INSERT GOOGLE DOC / CLASS PAGE LINK]` — the hub with every link below.
2. **Create a Claude account** → `[INSERT claude.ai SIGNUP LINK]`.
3. **Download the desktop app** → `[INSERT DESKTOP APP LINK]`.
   - 🔦 **Chat vs Cowork vs Code.** "Who's used Claude online — the chat? *This is that.*" Point out the three surfaces: **Chat** (the familiar one), **Cowork** (not today), **Code** (what we're using). "It looks like a chat box. It's cooler — it can read your files, run code, and build things."
   - 🔦 **Set the model to Opus 4.8 (medium reasoning)** in the model picker.
4. **Sign up for Claude Pro** — required for Claude Code. 🗣️ "It's **$20/month**. **Cancel after one month. Do NOT pick the annual plan.** If you'd rather not pay, pair up and follow along with a neighbor — you'll still get everything."
5. 🗣️ **Don't run anything in Claude yet — we're saving tokens.** 🔦 **Usage limits:** explain the rolling **5-hour limit** — Pro gives you a usage budget that resets every 5 hours, and heavy use can exhaust it. "That's why we won't burn tokens warming up."
6. **Download the class folder** → `[INSERT ZIP LINK]`. Unzip it and put the folder **on your Desktop**. It contains the data and your worksheet.
   - 💡 **The one idea that matters:** Claude Code works on the files **in a folder**. You point it at this folder on your computer; nothing gets uploaded.
- 🧯 Pair up slow installers so nobody sits idle.

---

## BLOCK 1 — The core arc (~90 min)

### Segment A — Load & meet the data (10 min)
- **First contact** — everyone runs one prompt so they see it work:
  - ⌨️ `What files are in this folder?`
  - 👀 It lists `waffle_houses.csv` and the PDF.
  - 🔦 **Permissions.** The first action triggers a permission prompt — Claude asks before it reads or changes anything. Approve it. Then show **Bypass Permissions** mode: "for today's sandbox folder you can flip this on so it stops asking — convenient, but understand it means Claude acts without checking with you first."
  - 🔦 **Interrupt (Esc).** "If it ever heads somewhere you didn't want, hit **Esc** to stop it. You're always in control." (Say this early — it relaxes the room.)
- ⌨️ `Load waffle_houses.csv and tell me what's in it — how many rows, what are the columns, and show me a few example rows.`
- 👀 ~2,006 rows, 14 columns, a sample table.
- 🔦 **Usage / token icon.** "Click here to see how many tokens you've used — this is your budget, and it's where the 5-hour limit lives." (Loading a 2,000-row file is a visible bump — a good moment to show it.)
- 🔦 **See what it's doing.** Expand the activity/steps to watch it actually read the file and run code. "This is how you *check its work* instead of just trusting the answer — the reporter's instinct."
- 🔦 **@-mention files.** "Instead of typing a filename, type `@` and pick the file from the list."
- 💡 No uploading, no importing. It read the file off the disk. Compare to opening a CSV in Excel — same idea, but you can now *ask questions in English*.
- 🗣️ Prompt the room: "What would you want to check first before you trusted this data?" (Leads into QA.)

### Segment B — Data dictionary + quality checks (20 min)
- ⌨️ `Create a data dictionary documenting every column: what it is, its type, and any quality issues. Then run standard data-quality checks — missing values, duplicates, type problems, and any inconsistencies that could affect analysis. Save the dictionary as DATA_DICTIONARY.md.`
- 👀 A per-column table + a QA section, written to a file.
- 💡 **The teachable catches** (make sure these surface — ask follow-ups if not):
  - A **non-numeric `Store Code`: `WH_Museum`** (the original location, now a museum). *"If you'd assumed store codes were numbers, your code would have crashed — or worse, silently dropped a row."*
  - **Blanks** in `Operated By` (1), `Online Order Link` (3), `Formatted Business Hours` (2).
  - `Postal Code` should stay **text** (leading zeros).
  - `Operated By` has three buckets (corporate / subsidiary / franchise) that need cleaning before use.
- 🔦 **Open a created file in the sidebar.** The moment `DATA_DICTIONARY.md` appears, click the file link Claude produces — it opens in the sidebar/preview. "Claude doesn't just talk; it leaves real files in your folder you can open and keep."
- 🔦 **Checkpoints / undo.** Right after that first file write: "Claude Code keeps **checkpoints** — you can **rewind** to before any change. In this folder, you can't permanently break anything." (This single feature relaxes non-coders more than anything else — lean on it.)
- ⌨️ Follow-up to model curiosity: `Are all locations really open 24 hours? Check the hours column.`
  - 👀 **8 are not** — including 2 marked `Closed`. (Plant this; it becomes a finding.)
- 🧯 If it misses the `WH_Museum` oddity: `Are all the store codes numeric? Check.` · If the file doesn't save: open `prepared/DATA_DICTIONARY.md` and walk through it.
- 💡 **Editorial framing:** documentation + QA *is* the first half of fact-checking. You do it before you believe a single number.

### Segment C — Exploratory web app (25 min)
- 🔦 **Plan Mode.** Have everyone switch to **Plan Mode** first. "Instead of building immediately, Claude will plan it *with* you and ask questions — you stay the editor." Then type the open-ended prompt:
- ⌨️ `I want to build a self-contained web app in one HTML file with a map of the locations and a bar chart with a count by state. I'm sure there are other interesting things we could do. Enter plan mode and ask me some questions to come up with a simple app.`
- 👀 Claude asks a few questions (what to show, how to style, what's interesting) before writing anything. Answer them live — let the room suggest answers. Then it builds: open the `.html` → scatter-map of the U.S. + bar chart led by GA.
- 💡 "You just shipped a data viz — and you *designed* it by answering questions, not by knowing how. Notice the map *looks like the South* — the data has a shape, and you can see it."
- 🗣️ **Encourage their own ideas.** The follow-ups below are examples; push students to ask for whatever *they'd* find interesting.
- ⌨️ Iterate live (this is the point — show conversation, not perfection):
  - `Add a "Count by" dropdown so the bar chart can count any column, not just State — and always show blank/NA values as their own bar.`
  - 👀 Picking `Operated By` reveals the corporate/subsidiary/franchise split with a single blank row in red; picking `Formatted Business Hours` shows the 2 blanks. 💡 Seeing the NA bar makes missing data *visible* instead of silently dropped — exactly the instinct from Segment B.
  - `Draw a real base map under the dots — continental U.S. state outlines — and make it work offline.`
  - `Make each dot hoverable: show a popup with that location's name, address, phone, operator, and hours.`
  - 👀 A faint state-outline map; hovering a dot pops its details. 💡 This is the difference between a chart and a *tool a reporter can interrogate* — "what's that lonely dot out west?" → hover and find out.
- 🧯 If it tries to use an internet map service and it won't load offline: `Make the map work fully offline — just plot the points, no external map tiles.` · Last resort: open `prepared/waffle_explorer.html`.
- 💡 **Why self-contained matters for reporters:** one file you can email an editor, attach to a story, or keep — no server, no dependencies, works in five years.

### Segment D — Analysis: "I ask, you analyze" (20 min)
- 🗣️ This is the interactive heart. *You* (or students) ask questions; Claude answers. Use the bank below; let the room drive.
- ⌨️ Starter questions:
  1. `Which state has the most Waffle Houses, and what share of the total is that?` → **GA, 442, 22%**
  2. `What share of all locations are in the top five states?` → **57%**
  3. `Break locations down by operator type — corporate vs. subsidiary vs. franchise.` → only **~6% franchised**
  4. `Which single city has the most?`
  5. `How many states have zero Waffle Houses?` (25 present → 25 states/territories covered)
  6. `Which Waffle House is the furthest north, south, east, and west?` → **N: Austinburg, OH · S: Key Largo, FL · E: Bethlehem, PA · W: Goodyear, AZ.** 💡 A great "show me on the map" moment — flip on the N/S/E/W markers in the web app. This becomes the notebook's third finding.
- 💡 Each of these is a spreadsheet move (group, count, sort, %) — done by asking. Stress: **always ask Claude to show its work / the numbers**, so you can check them.
- 🧯 If an answer seems off, model the right instinct out loud: `Show me exactly how you got that number.`

### Segment E — Pick one finding → reproducible notebook (15 min) ⭐
- 🗣️ "Now the journalism part. We pick **one** finding and build a notebook an editor could open and re-run — start to finish — to verify we're right."
- **You pick live.** Recommended: **the South dominance** finding (robust, visual), with **the 8 non-24h exceptions** as a second section. Both are in the prepared notebook.
- ⌨️ `Build a Jupyter notebook that an editor could review. It should: (1) state the central finding up front in plain English; (2) document where the data came from; (3) run the data-quality checks; (4) reproduce the finding step by step from the raw CSV, with a chart; (5) end with limitations. Make every number trace back to the raw file. Also reproduce two more findings: that 8 locations are not open 24 hours, and which location is furthest north, south, east, and west.`
- 👀 A `.ipynb` with a "nut graf," provenance, QA, the state analysis + bar chart, the 8-row table, the N/S/E/W extremes + a map, and a limitations section.
- ⌨️ `Run the whole notebook top to bottom and show me it works.`
- 💡 **This is the deliverable that separates a tool demo from journalism:** reproducibility = your methodology is auditable. Anyone can re-run it and get your numbers. That's the standard.
- ⌨️ **Make it shareable:** `Export the notebook as a standalone HTML file I can open in any browser.`
  - 👀 One `.html` with the charts and numbers baked in — double-clicks open with no install.
  - 💡 The `.ipynb` is the **working** file (needs Jupyter/VS Code/Colab to open). The **HTML is the shareable deliverable** — it opens anywhere, so it's what you hand an editor or attach to a story.
- 🧯 If execution fails (missing package): `Install whatever this notebook needs and run it again.` · Last resort: open `prepared/waffle_house_finding.ipynb`, or the ready-made `prepared/waffle_house_finding.html`.

---

## BLOCK 2 — Publish: PDF → story (~60 min)

- 🔦 **New chat to reset & save tokens.** Before starting Block 2: "Open a **fresh chat**. It clears the context so far — which keeps Claude focused *and* saves tokens against your 5-hour budget. Carry over only what you need." (Natural breakpoint; reinforces the token-discipline theme from setup.)

### Segment F — Parse the nutrition PDF + verify (30 min)
- 🗣️ "New source, harder format. Reporters live in PDFs. Watch Claude pull a table out — then watch us *not trust it blindly.*"
- ⌨️ `Read Menu-Nutritionals-2026-05-05.pdf. Extract the nutrition tables — item name, section, calories, fat, sodium, etc. — into a clean CSV called nutrition.csv.`
- 👀 A `nutrition.csv` with a few hundred rows across menu sections.
- 🔦 **Skills.** "Claude just reached for its built-in **PDF skill** to read that file — skills are packaged expertise it pulls in automatically when a task calls for it. Type `/` to see the commands and skills available to you." (We'll *build* one at the end.)
- ⌨️ **The verification step (don't skip — it's the lesson):** `Pick 5 rows at random and show them next to the original PDF values so I can confirm the parse is correct. What might have gone wrong in the extraction?`
- 💡 **The habit:** an extracted table is a *claim*, not a fact, until you check it against the source. PDFs have merged cells, footnotes, wrapped rows. Spot-check before you publish.
- ⌨️ Then analyze: `In nutrition.csv, which items have the most sodium? The most calories? How does the saltiest item compare to the 2,300 mg daily limit?`
  - 👀 Saltiest: **Country Ham Biscuits (2), 3,710 mg** (~1.6× daily limit); most calories: **Sausage Egg & Cheese Hashbrown Bowl, 920**.
- 🧯 If the parse is messy: `Some rows look misaligned. Fix the parser so the numbers line up with the right columns, and re-verify.` · Last resort: `prepared/nutrition.csv`.

### Segment G — Scrollytelling finale (30 min)
- 🗣️ "Let's turn that finding into something readers would actually scroll through."
- ⌨️ `Build a single-file scrollytelling web page about the saltiest items at Waffle House. As I scroll, tell the story with a sticky chart that updates — start with sodium, highlight the worst offender against the daily limit, then switch to calories. Use the numbers from nutrition.csv. Make it look like a polished news graphic.`
- 👀 A scroll-driven page: hero headline → sticky bar chart that animates as text steps scroll by.
- ⌨️ Iterate: `Make the headline bigger and add a short methods note at the bottom citing the PDF.`
- 💡 The arc completes: **raw PDF → verified data → published interactive.** The methods note at the bottom is the same reproducibility instinct from the notebook, now reader-facing.
- 🧯 Last resort: open `prepared/nutrition_scrollytelling.html`.

---

## BONUS — Build your own skill (if time, ~10 min) 🎁
- 🗣️ "Everything we did today, you could do again on your *next* dataset. Skills let you bottle a workflow so it's one command forever after."
- ⌨️ `Create a skill called data-intake that, given a CSV, loads it, writes a data dictionary, and runs standard data-quality checks — so I can reuse this on any dataset.`
- 👀 Claude writes a skill file; then invoke it (type `/data-intake`, or just point it at a new CSV and let it trigger).
- 💡 "This is the jump from *using* a tool to *building your own workflow*. The data-intake move from this morning is now a reusable button." 
- 🧯 **Optional/bonus — skip without guilt if you're short on time.** Even just showing that skills *can* be created lands the point.

---

## CLOSE (buffer / ~10 min)
🗣️ Recap the arc on screen:
**Load → Document → Check → See → Ask → Reproduce → Export → Extract → Verify → Publish.**
- "Every step was a conversation. The habits that didn't change: documenting your data, checking it before you trust it, and making your work reproducible. Claude Code just made each step faster."
- 🗣️ "Remember the **HTML exports** — the notebook page and the scrollytelling — those are what you actually share; they open anywhere with nothing installed."
- Point them to their **`WORKSHEET.md`**: the prompt cheat-sheet to repeat this on their own data, plus the **'features we used today' map**. The bonus `data-intake` skill is their take-home next step.

## Pacing cheatsheet
| Running clock | You should be… |
|---|---|
| 0:30 | finishing setup (account, Pro, folder on Desktop), everyone ran "What files are in this folder?" — permission + bypass shown |
| 1:00 | data dictionary + QA done, the `WH_Museum` catch landed; sidebar + checkpoints shown |
| 1:25 | web app open, map showing the Southern shape |
| 1:50 | analysis Q&A, finding chosen |
| 2:05 | notebook built, executed, AND exported to HTML |
| 2:15 | fresh chat started for Block 2 (token reset) |
| 2:40 | nutrition CSV parsed AND spot-checked; PDF skill noted |
| 3:10 | scrollytelling live |
| 3:20 | bonus: build the `data-intake` skill (if time) |
| 3:30 | recap, worksheet, questions |

> **Feature spotlights (🔦) by block:** Block 0 — Chat/Cowork/Code, model = Opus 4.8 medium, 5-hour limit. Segment A — permissions + bypass, Esc, usage icon, "see what it's doing", @-mention. Segment B — open file in sidebar, checkpoints/undo. Segment C — Plan Mode. Block 2 — new chat to save tokens, skills (`/` menu). Bonus — build a custom skill.
