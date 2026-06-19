# Today's Worksheet — Reporting with Claude Code
*Keep this next to you. Part 1 is the prompts. Part 2 is the features we touched.*

---

# Part 1 · Prompt cheat-sheet
*Every step is just a sentence you type.*

### The one idea
Claude Code works on the **files in your folder**. No uploading. Put your data in a folder, point Claude at it, and ask.
> 💬 `What files are in this folder?`

### 1 · Load & meet your data
> 💬 `Load waffle_houses.csv and tell me what's in it — rows, columns, and a few example rows.`

### 2 · Document & quality-check (do this before you trust anything)
> 💬 `Create a data dictionary for every column, then check for missing values, duplicates, type problems, and inconsistencies that could affect analysis. Save it as DATA_DICTIONARY.md.`

**Always ask the skeptical follow-ups:**
> 💬 `Are the ID columns all the format I expect?`
> 💬 `What values are blank, and would that change any analysis?`

### 3 · See it (quick web app)
First switch to **Plan Mode** (so Claude plans it *with* you and asks questions before building), then type:
> 💬 `I want to build a self-contained web app in one HTML file with a map of the locations and a bar chart with a count by state. I'm sure there are other interesting things we could do. Enter plan mode and ask me some questions to come up with a simple app.`

Answer its questions, let it build, then keep going. A few follow-ups you *could* ask — but **come up with your own!**
> 💬 `Add a "Count by" dropdown so I can count any column, and always show blank/NA as its own bar.`
> 💬 `Draw a real base map under the dots and make it work offline.`
> 💬 `Make each dot hoverable with a popup of its details.`

### 4 · Ask your questions
Anything you'd do in a spreadsheet — grouping, counting, averages, sorting — just ask. Today's questions:
> 💬 `Which state has the most Waffle Houses, and what share of the total is that?`
> 💬 `What share of all locations are in the top five states?`
> 💬 `Break locations down by operator type — corporate vs. subsidiary vs. franchise.`
> 💬 `Which single city has the most?`
> 💬 `How many states have zero Waffle Houses?`
> 💬 `Which Waffle House is the furthest north, south, east, and west?`  ← the edges of your data
> 💬 **Always:** `Show me exactly how you got that number.`

### 5 · Make it reproducible (the editor test)
> 💬 `Build a Jupyter notebook an editor could review: state the finding in plain English, document the data source, run the quality checks, reproduce the finding step by step from the raw file with a chart, and end with limitations. Then run it top to bottom.`
> 💬 `Export the notebook as a standalone HTML file I can open in any browser.`  ← the version you share

### 6 · Pull data out of a PDF — then VERIFY
> 💬 `Read Menu-Nutritionals-2026-05-05.pdf and extract the tables into a clean CSV.`
> 💬 `Show me 5 rows next to the original PDF so I can confirm the parse is right. What could have gone wrong?`

⚠️ **An extracted table is a claim, not a fact, until you check it against the source.**

### 7 · Publish
> 💬 `Build a single-file scrollytelling page about [finding], with a sticky chart that updates as I scroll. Add a methods note citing the source.`

### Bonus · Make your own reusable skill
> 💬 `Create a skill called data-intake that, given a CSV, loads it, writes a data dictionary, and runs standard data-quality checks — so I can reuse this on any dataset.`

---

### Habits that make it journalism (not just a demo)
1. **Document and check before you analyze.** QA is the first half of fact-checking.
2. **Make Claude show its work.** Ask for the numbers, the steps, the source rows.
3. **Verify extractions** against the original.
4. **Keep it reproducible.** If an editor can't re-run it, it isn't done.

*The habits don't change — documenting, checking, reproducing. Claude Code just makes each step faster.*

---

# Part 2 · Claude Code features we used today
*Where to find them on your screen (labels may move as the app updates).*

| Feature | What it does / why it matters |
|---|---|
| **Chat vs Cowork vs Code** | Three surfaces in the app. **Chat** = the Claude you know. **Code** = what we used; it reads your files, runs code, builds things. **Cowork** = another mode, not today. |
| **Model picker → Opus 4.8 (medium)** | Sets which model and how hard it "thinks." We used Opus 4.8 at medium reasoning. |
| **Plan Mode** | Claude plans the work *with* you — and asks questions — before it builds. Great for designing something instead of just ordering it. |
| **Claude Pro** | Required for Claude Code. $20/mo — **cancel after a month, don't pick annual.** No budget? Pair up. |
| **5-hour usage limit** | Your token budget resets every 5 hours. Don't burn it on warm-ups. |
| **Usage / token icon** | Shows how many tokens you've spent — your budget meter. |
| **Permissions** | Claude asks before it reads or changes files. |
| **Bypass Permissions** | Turns the asking off for a trusted folder — convenient, but Claude then acts without checking first. |
| **Esc to interrupt** | Stops Claude mid-response. You're always in control. |
| **"See what it's doing"** | Expand the activity/steps to watch it read files and run code — how you check its work. |
| **@-mention a file** | Type `@` and pick a file instead of typing its name. |
| **Open a file in the sidebar** | Click a file link Claude makes to open it in the side panel. |
| **Checkpoints / rewind** | Undo Claude's changes — rewind to before any edit. You can't permanently break your folder. |
| **New chat** | Start fresh to clear context and save tokens. |
| **Skills (`/` menu)** | Packaged expertise Claude uses automatically (e.g., reading PDFs). Type `/` to see what's available — and you can build your own (see Bonus above). |
| **HTML export** | Turn a notebook or app into one shareable file that opens in any browser, no install. |
