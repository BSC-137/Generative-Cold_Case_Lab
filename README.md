# 🕵️ Gen Cold Case Lab

**Gen Cold Case Lab** is a local, text-based detective game powered by **LLMs**.
Each round, the program uses eerie **JSON "seed data"** + **structured prompting** to generate a fully fictional, solvable cold case mystery.

You play detective: read the case file, examine evidence, then guess who did it.

---

## 🎮 How to Play

### 1. Install requirements

* [Ollama](https://ollama.com) for running models locally (Windows/macOS/Linux supported).
* Python 3.10+ with `requests`:

  ```bash
  pip install requests
  ```
* Pull any model you want to use. For example:

  ```bash
  ollama pull gemma3:4b
  ```

  But you can choose another supported model depending on your system capabilities (e.g. `mistral:7b`, `llama3:8b`, etc.).

### 2. Run the game

From the project root:

```bash
py play.py --model <model_name> --show brief --reveal
```

Examples:

* `py play.py --model gemma3:4b --show brief --reveal`
* `py play.py --model mistral:7b --show full`

Options:

* `--show brief` → only prints victim + suspects (quick play).
* `--show full` → prints the entire eerie Markdown case file in terminal.
* `--reveal` → shows the hidden rationale after your guess.

### 3. Guess the culprit

* The program saves the full Markdown case to the `cases/` folder.
* You’re asked: `Who did it? (A/B/C)`
* Make your guess.
* The game checks the **hidden solution** embedded as an HTML comment in the Markdown.
* You’ll see if you were right, plus the reasoning.

---

## 🗂️ Project Structure

```
gen_cold_case_lab/
  play.py          # main game loop
  data/
    seeds.jsonl    # eerie seed data (JSON lines)
  cases/           # generated case files
  README.md
  .gitignore
```

---

## 🧩 Technical Highlights

This project isn’t just a game — it’s a **mini LLM pipeline** showcasing modern techniques:

### 1. Retrieval-Augmented Generation (RAG)

* We use a **seed dataset (`seeds.jsonl`)** as the retrieval layer.
* Each seed encodes the *vibe* of a mystery: terrain, season, anomalies, artifacts, folklore rumors.
* Example:

  ```json
  {
    "id": "A2",
    "flavor": "cryptid",
    "region_hint": "PNW logging road",
    "terrain": "forest",
    "weather": "dense fog",
    "artifacts": ["trail-cam with corrupted frames", "broken antler"],
    "rumors": ["tall thing crosses road at midnight"]
  }
  ```
* This retrieved context anchors the LLM’s generation, ensuring output is **thematically consistent but never repetitive**.

### 2. JSON Prompting

* Instead of freeform text, seeds are structured JSON → passed into the LLM inside a **strict template prompt**.
* This guarantees the case file always has:

  * **Timeline**
  * **Suspects (2–3, with motives & quirks)**
  * **Evidence (real clues + red herrings)**
  * **Contradictions (to mislead smartly)**
  * **Hidden truth** (HTML comment with culprit + rationale)

### 3. Deterministic Game Loop

* The **Python wrapper** handles:

  * Random seed selection.
  * Building the LLM prompt.
  * Parsing suspects + culprit from Markdown.
  * User interaction (`Who did it? A/B/C`).
* Cases are saved as `.md` → readable like eerie police files.

### 4. LLM Engineering Skills

* **Structured prompting:** Template ensures solvable cases.
* **Red herrings:** Model is instructed to weave in folklore/cryptid/cult clues while keeping the real culprit human.
* **Hidden answers:** Solution embedded in HTML comments lets us separate *player experience* from *ground truth*.
* **Post-processing:** Regex parsing extracts suspects + solution reliably.

---

## ⚡ Example Case Snippet

```md
# Case 4ECE — Incident near Blackwood Ridge
**Case Type:** Cryptid  
**Victim:** Silas Blackwood, 68, last seen 11:47 PM near logging road entrance.

## Suspects
- **Ezekiel Thorne** — logger; obsessed with folklore; alibi: home, hungover.
- **Mara Blackwood** — botanist; wanted rare specimen; alibi: fieldwork up ridge.
- **Ranger Davies** — on duty; skeptical of legends.

## Evidence
1. Three-toed impressions in sleet.
2. Antler in Thorne’s truck (traces of sedative).
3. Trail-cam with corrupted frames.
4. Mara’s sat-phone ping at 11:45 PM.
...

<!-- culprit: Ezekiel Thorne | rationale: sedative traces + staged folklore clues -->
```

---

## 📜 Disclaimer

All names, places, and details are **fictional**.
Seeds are synthetic “vibes,” not real cases.
This project is for **educational & entertainment purposes only**.
