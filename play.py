import os, json, re, datetime, random, argparse, textwrap, requests
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"

def load_seeds(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

PROMPT_TEMPLATE = """SYSTEM: You are a mystery editor. Create a FICTIONAL, SOLVABLE case from a seed.
Never use real names or exact places. One HUMAN suspect must be the culprit.
Include 1–2 flavor-appropriate red herrings (cryptid/cult/etc.), but the solution must be human.
Output STRICTLY in Markdown with EXACT sections, then embed the solution as an HTML comment.

USER:
Seed (do not copy literally; use only vibes/priors):
{seed_pretty}

Write Markdown with these sections and nothing else:
Title: "Case {case_id} — Incident near {{fictional_location}}"
Case Type: one of [classic, appalachian, cryptid, cult] to match the seed vibe
Victim: name, age, "last seen" time/place (fictionalized)

## Timeline
- 5–6 concise beats with times; weave weather/terrain from the seed

## Suspects
- 2–3 suspects: each has relation, motive hint, alibi, and a quirk

## Evidence
- 6–9 items; include exactly TWO that subtly implicate ONE suspect
- include 1–2 flavor red herrings (cryptid/cult/etc.) that are NOT the true cause

## Contradictions
- 1–2 contradictions that cast doubt on an innocent suspect’s alibi

Embed ONLY ONE HTML comment for solution, exactly:
<!-- culprit: NAME | rationale: reference 2–3 evidence items concisely -->

Constraints:
- All names/places invented. No real people or addresses.
- Keep it solvable, forensic, atmospheric.
"""

def build_prompt(seed):
    seed_pretty = json.dumps(seed, ensure_ascii=False, indent=2)
    case_id = hex(random.getrandbits(16)).upper()[2:]
    return PROMPT_TEMPLATE.format(seed_pretty=seed_pretty, case_id=case_id), case_id

def call_ollama(model, prompt, temperature=0.9, top_p=0.95, num_ctx=4096):
    resp = requests.post(OLLAMA_URL, json={
        "model": model,
        "prompt": prompt,
        "options": {"temperature": temperature, "top_p": top_p, "num_ctx": num_ctx},
        "stream": False
    }, timeout=120)
    resp.raise_for_status()
    return resp.json().get("response","")

def extract_culprit(markdown):
    m = re.search(r"<!--\s*culprit:\s*(.+?)\s*\|\s*rationale:\s*(.+?)\s*-->", markdown, re.I|re.S)
    if not m: return None, None
    return m.group(1).strip(), " ".join(m.group(2).strip().split())

def list_suspects(markdown):
    block = re.search(r"##\s*Suspects(.+?)(?:\n##|\Z)", markdown, re.S|re.I)
    if not block: return []
    suspects = []
    for ln in (ln.strip() for ln in block.group(1).splitlines() if ln.strip()):
        m = re.search(r"-\s*\*\*(.+?)\*\*", ln)
        if m: suspects.append(m.group(1).strip())
    return suspects[:3]

def print_brief(markdown):
    title = re.search(r"^#\s*(.+)$", markdown, re.M)
    victim = re.search(r"^\*\*Victim:\*\*\s*(.+)$", markdown, re.M)
    sus = list_suspects(markdown)
    print("\n" + (title.group(1) if title else "Untitled"))
    if victim: print(victim.group(0))
    if sus:
        letters = ['A','B','C']
        print("\nSuspects:")
        for i, name in enumerate(sus):
            print(f"  {letters[i]}. {name}")
    else:
        print("\n(Suspects not found; model output might be malformed.)")
    print("\n(See full case in the saved Markdown.)\n")

def save_case(md, outdir, case_id):
    Path(outdir).mkdir(parents=True, exist_ok=True)
    fname = f"CASE_{datetime.date.today()}_{case_id}.md"
    fpath = Path(outdir) / fname
    fpath.write_text(md, encoding="utf-8")
    return str(fpath)

def main():
    ap = argparse.ArgumentParser(description="Gen Cold Case Lab — LLM mystery (Ollama)")
    ap.add_argument("--seeds", default="data/seeds.jsonl")
    ap.add_argument("--model", default="gemma:4b")
    ap.add_argument("--show", choices=["brief","full"], default="brief")
    ap.add_argument("--reveal", action="store_true")
    ap.add_argument("--outdir", default="cases")
    args = ap.parse_args()

    seeds = load_seeds(args.seeds)
    if not seeds:
        print("No seeds found."); return
    seed = random.choice(seeds)

    prompt, case_id = build_prompt(seed)
    md = call_ollama(args.model, prompt)

    path = save_case(md, args.outdir, case_id)
    print(f"\nSaved case → {path}")

    if args.show == "brief":
        print_brief(md)
    else:
        print("\n" + md)

    suspects = list_suspects(md)
    culprit_name, rationale = extract_culprit(md)
    if not suspects or not culprit_name:
        print("Could not parse suspects or solution. Open the file to read manually."); return

    letters = ['A','B','C']
    mapping = {letters[i]: suspects[i] for i in range(len(suspects))}
    while True:
        choice = input(f"Who did it? ({'/'.join(letters[:len(suspects)])}): ").strip().upper()
        if choice in mapping: break
        print("Choose a valid letter.")

    picked = mapping[choice]
    print()
    if picked.lower() == culprit_name.lower():
        print("✅ Correct. You followed the evidence.")
    else:
        print(f"❌ Not quite. You chose {picked}; the culprit was {culprit_name}.")

    if args.reveal:
        print(f"\nReasoning: {rationale}")

    print("\nPlay again: `python play.py --model gemma:4b --show brief`")

if __name__ == "__main__":
    main()
