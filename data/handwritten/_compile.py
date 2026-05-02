"""Compile set_1.json..set_10.json into the final data/exams.json,
validate schema, and report duplicates."""
import json, re, sys
from pathlib import Path
from collections import Counter, defaultdict

HERE = Path(__file__).parent
OUT = HERE.parent / "exams.json"

REQUIRED_Q = {"chapter", "topic", "difficulty", "type", "statement_md", "answer", "explanation_md"}
TYPES = {"mcq", "short", "code"}
TARGET_PER_SET = 20

def normalize_stmt(s):
    # Keep the body inside code fences (it's the discriminating part).
    s = re.sub(r"```(?:[a-z]+)?\n?", "", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s

problems = []
sets_out = []

for i in range(1, 11):
    f = HERE / f"set_{i}.json"
    if not f.exists():
        problems.append(f"missing {f.name}")
        continue
    data = json.loads(f.read_text(encoding="utf-8"))
    if data.get("id") != i:
        problems.append(f"set_{i}: id mismatch ({data.get('id')})")
    qs = data.get("questions", [])
    if len(qs) < TARGET_PER_SET:
        problems.append(f"set_{i}: only {len(qs)} questions (<{TARGET_PER_SET})")
    if len(qs) > 22:
        qs = qs[:22]   # cap at 22 only (allow 20-22 range)
    # Validate each question
    cleaned = []
    for j, q in enumerate(qs, 1):
        miss = REQUIRED_Q - set(q.keys())
        if miss:
            problems.append(f"set_{i} q{j}: missing fields {miss}")
            continue
        if q["type"] not in TYPES:
            problems.append(f"set_{i} q{j}: bad type {q['type']!r}")
            continue
        if q["chapter"] not in (1, 2, 3, 4):
            problems.append(f"set_{i} q{j}: bad chapter {q['chapter']!r}")
        try:
            d = int(q["difficulty"])
            if d < 1 or d > 5:
                problems.append(f"set_{i} q{j}: difficulty {d} out of [1,5]")
        except Exception:
            problems.append(f"set_{i} q{j}: difficulty not int")
        if q["type"] == "mcq":
            ch = q.get("choices") or []
            if len(ch) != 4:
                problems.append(f"set_{i} q{j}: mcq has {len(ch)} choices (need 4)")
            if not (isinstance(q["answer"], str) and q["answer"] in "ABCD"):
                problems.append(f"set_{i} q{j}: mcq answer not in A-D ({q['answer']!r})")
        else:
            if not isinstance(q["answer"], str) or not q["answer"].strip():
                problems.append(f"set_{i} q{j}: empty answer")
        q["id"] = f"{i}-{j}"
        cleaned.append(q)
    set_obj = {
        "id": i,
        "title": data.get("title") or f"第 {i} 套",
        "focus": data.get("focus") or "",
        "questions": cleaned,
    }
    sets_out.append(set_obj)

# Global duplicate check
seen = defaultdict(list)
for s in sets_out:
    for q in s["questions"]:
        seen[normalize_stmt(q["statement_md"])].append(q["id"])

dup_groups = [(k, ids) for k, ids in seen.items() if len(ids) > 1]
if dup_groups:
    problems.append(f"Found {len(dup_groups)} duplicate statement groups:")
    for k, ids in dup_groups[:20]:
        problems.append(f"   {ids} :: {k[:80]}")

# Chapter coverage per set
for s in sets_out:
    chapters = Counter(q["chapter"] for q in s["questions"])
    for ch in (1, 2, 3, 4):
        if chapters.get(ch, 0) < 2:
            problems.append(f"set_{s['id']}: chapter {ch} only {chapters.get(ch,0)} questions")

# Final report
print(f"Sets compiled: {len(sets_out)}")
counts = [len(s["questions"]) for s in sets_out]
print(f"Question counts per set: {counts}; total = {sum(counts)}")
print(f"Per-chapter totals: {Counter(q['chapter'] for s in sets_out for q in s['questions'])}")
if problems:
    print(f"\n{len(problems)} issues:")
    for p in problems:
        print(" -", p)
else:
    print("No issues.")

meta = {
    "course": "AP2 — 算法与程序设计 2",
    "sets_count": len(sets_out),
    "questions_per_set": TARGET_PER_SET,
}
OUT.write_text(json.dumps({"meta": meta, "sets": sets_out}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nWrote {OUT} ({OUT.stat().st_size} bytes)")
