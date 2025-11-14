from pathlib import Path

def normalize_key(k: str) -> str:
    import re
    return re.sub(r'[^a-z0-9]', '', k.lower())

def parse_engagement_file(path: Path):
    txt = path.read_text(encoding='utf-8')
    lines = [l.rstrip() for l in txt.splitlines()]
    data = {}
    cur = None
    buf = []
    
    for ln in lines:
        s = ln.strip()
        if not s:  # skip empty lines
            continue
            
        # Check for pipe-separated key|value format: `key`|value or key|value
        if "|" in s:
            parts = s.split("|", 1)
            key = parts[0].strip().strip("`").strip("'").strip()
            value = parts[1].strip() if len(parts) > 1 else ""
            
            # Save previous key's buffer if any
            if cur:
                data[cur] = "\n".join(buf).strip()
            
            cur = key
            buf = [value] if value else []
        # Bullet point or continuation - add to current buffer
        elif s.startswith("•") or (cur and "|" not in s):
            if cur:
                buf.append(ln)
        else:
            # Unknown line format - skip
            pass
    
    # Save last key's buffer
    if cur:
        data[cur] = "\n".join(buf).strip()
    
    return data

path = Path('c:/gitrepo/cv/content/engagements/opdracht_2025_heden.txt')
data = parse_engagement_file(path)
print("Parsed keys:")
for k, v in data.items():
    print(f'  {k}: {v[:50]}...' if len(v) > 50 else f'  {k}: {v}')

# Now test matching
ENG_SYNONYMS = {
    "functie": ["functie","functienaam","job","jobtitle","job_title"],
    "werkzaamheden": ["werkzaamheden","work","workdetails","textblockwork","text_block_work","work_description"],
    "prestaties": ["belangrijksteprestaties","achievements","achievements_text","text_block_achievements","achievements_list"],
    "trefwoorden": ["trefwoorden","keywords","text_block_keywords","keywords_list"],
    "organisatie": ["organisatie","organisatie_naam","organization","employer"]
}

print("\n\nTesting organisatie matching:")
variants = ENG_SYNONYMS["organisatie"]
normalized = {normalize_key(k): (k, v) for k,v in data.items()}

def get_variant(variants):
    for v in variants:
        nv = normalize_key(v)
        print(f"  Looking for normalized '{nv}' (from '{v}')")
        if nv in normalized:
            print(f"    Found!")
            return normalized[nv][1]
    return None

result = get_variant(variants)
print(f"\nResult: {result}")
