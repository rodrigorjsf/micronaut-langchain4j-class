#!/usr/bin/env python3
import re, os, glob

BASE = "/home/rodrigo/Workspace/micronaut-langchain4j-class/lessons"
ref = open(f"{BASE}/0001-modelo-mental.html", encoding="utf-8").read()

def extract(block, html):
    m = re.search(rf"<{block}>(.*?)</{block}>", html, re.S)
    return m.group(1) if m else None

ref_style, ref_script = extract("style", ref), extract("script", ref)

PARITY_TAGS = ["div","blockquote","table","thead","tbody","tr","td","th",
               "pre","code","ol","ul","li","p","h1","h2","h3","footer","nav","span","button"]

problems = {}
def add(f, m): problems.setdefault(f, []).append(m)

for f in sorted(glob.glob(f"{BASE}/0*.html")):
    name = os.path.basename(f)
    html = open(f, encoding="utf-8").read()
    if extract("style", html) != ref_style:  add(name, "STYLE differs from 0001")
    if extract("script", html) != ref_script: add(name, "SCRIPT differs from 0001")
    nq   = len(re.findall(r'class="q"', html))
    nopt = len(re.findall(r'class="opt"', html))
    nexp = len(re.findall(r'class="explain"', html))
    if nq   != 3: add(name, f".q={nq} (exp 3)")
    if nopt != 9: add(name, f".opt={nopt} (exp 9)")
    if nexp != 3: add(name, f".explain={nexp} (exp 3)")
    dcs = re.findall(r'data-correct="([^"]*)"', html)
    if len(dcs) != 3: add(name, f"data-correct count={len(dcs)} (exp 3)")
    for v in dcs:
        if v not in ("a","b","c"): add(name, f"data-correct={v!r} invalid")
    for pre in re.findall(r'<pre>(.*?)</pre>', html, re.S):
        g = re.search(r'<[A-Z]\w*>', pre)
        if g: add(name, f"raw generic {g.group(0)!r} inside <pre>")
    if 'class="mission"' not in html: add(name, "missing .mission")
    if 'GLOSSARY.md' not in html:     add(name, "missing GLOSSARY link")
    if 'Fonte prim' not in html:      add(name, "missing primary source")
    if '../curso/modulo-' not in html: add(name, "missing source-draft link")
    # tag open/close parity (ignore void; ignore self-closing)
    for tag in PARITY_TAGS:
        opens  = len(re.findall(rf'<{tag}(?=[\s>])', html))
        closes = len(re.findall(rf'</{tag}>', html))
        if opens != closes:
            add(name, f"<{tag}> parity: {opens} open vs {closes} close")

files = sorted(glob.glob(f"{BASE}/0*.html"))
print(f"LESSONS CHECKED: {len(files)}")
if not problems:
    print("ALL GREEN")
else:
    for f in sorted(problems):
        print(f"\n{f}:")
        for p in problems[f]: print("  -", p)
    print(f"\n{len(problems)} file(s) with issues")
