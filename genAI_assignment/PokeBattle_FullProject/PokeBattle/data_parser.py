import re, os

FIELD_RE = re.compile(r"\s*([^:;]+)\s*:\s*([^;]+)\s*(?:;|$)")

def parse_block_text(text):
    return {m.group(1).strip(): m.group(2).strip() for m in FIELD_RE.finditer(text)}

def parse_moves_file(path):
    with open(path) as f: blocks=[b.strip() for b in f.read().split('\n\n') if b.strip()]
    return [parse_block_text(b) for b in blocks]

def parse_creatures_file(path):
    with open(path) as f: blocks=[b.strip() for b in f.read().split('\n\n') if b.strip()]
    creatures=[]
    for b in blocks:
        d=parse_block_text(b)
        if "Moves" in d: d["Moves"]=[m.strip() for m in d["Moves"].split(",")]
        creatures.append(d)
    return creatures
