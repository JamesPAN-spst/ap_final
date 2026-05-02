"""Better extractor: locate first '{' in code-block, then balance braces while
respecting JSON string boundaries (correctly handling escapes)."""
import json, sys, re
from pathlib import Path

ROOT = Path(r"c:\Users\89240\AppData\Roaming\Code\User\workspaceStorage\0114f2e7a9992276bc24651d4aefeb92\GitHub.copilot-chat\chat-session-resources\f5578f8c-5207-4273-9788-8ded7ed3dd93")
OUT = Path(r"s:\tmp\RESOURCE\ap\work\web\data\handwritten")

def extract_top_level(text):
    start = text.find('{')
    if start == -1:
        return None
    s = text
    depth = 0
    i = start
    in_str = False
    esc = False
    while i < len(s):
        c = s[i]
        if in_str:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return s[start:i+1]
        i += 1
    return None

for f in sorted(ROOT.glob("toolu_*/content.txt")):
    text = f.read_text(encoding="utf-8")
    body = extract_top_level(text)
    if body is None:
        print(f"  NO JSON {f.parent.name}")
        continue
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        fixed = re.sub(r'(?<=[\u4e00-\u9fff])"(?=[\u4e00-\u9fff])', r'\\"', body)
        try:
            data = json.loads(fixed)
            print(f"  fixed CJK quotes in {f.parent.name}")
        except json.JSONDecodeError:
            fixed2 = re.sub(r'(?<=[A-Za-z\u4e00-\u9fff])"(?=[A-Za-z\u4e00-\u9fff])', r'\\"', body)
            try:
                data = json.loads(fixed2)
                print(f"  fixed mixed quotes in {f.parent.name}")
            except json.JSONDecodeError as e3:
                print(f"  parse fail {f.parent.name}: {e3} (orig {e})")
                continue
    sid = data.get("id")
    if not isinstance(sid, int):
        print(f"  missing id in {f.parent.name}")
        continue
    qcount = len(data.get("questions", []))
    out = OUT / f"set_{sid}.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  -> set_{sid}.json ({qcount} questions) from {f.parent.name}")
