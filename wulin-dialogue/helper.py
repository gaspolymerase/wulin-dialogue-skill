#!/usr/bin/env python3
"""武林外传 dialogue skill helper.

Usage:
  helper.py chars                       List characters and line counts.
  helper.py find "<text>"               Find lines whose text contains/matches <text>.
                                        Returns up to 20 candidates with index, char, text, next-line.
  helper.py next <idx> [n]              Show line at idx and next n lines (default n=3).
  helper.py around <idx> [n]            Show n lines before and after idx (default n=3).
  helper.py char <name> [keyword]       Dump lines for character; optional keyword filter.
                                        Without keyword, prints all (large for main characters).
  helper.py sample <name> <keyword>     Sample lines containing keyword for given character,
                                        with prev/next context.
"""
import json, sys, os, re

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# 显示名(中文) <-> 文件名(ASCII slug) 映射，从 _chars.json 加载。
def _load_charmap():
    p = os.path.join(DATA, '_chars.json')
    if not os.path.exists(p):
        return {}, {}, {}
    with open(p, encoding='utf-8') as f:
        info = json.load(f)
    n2f = {name: meta['slug'] for name, meta in info.items()}
    f2n = {meta['slug']: name for name, meta in info.items()}
    return n2f, f2n, info

NAME2FILE, FILE2NAME, CHAR_INFO = _load_charmap()

def resolve_file(name):
    # accept either Chinese display name or pinyin filename
    if name in NAME2FILE:
        return NAME2FILE[name]
    if name in FILE2NAME:
        return name
    return name  # fallback: try as-is

def load_all():
    with open(os.path.join(DATA, '_all.json'), encoding='utf-8') as f:
        return json.load(f)

def load_char(name):
    fn = resolve_file(name)
    with open(os.path.join(DATA, f'{fn}.json'), encoding='utf-8') as f:
        return json.load(f)

def list_chars():
    out = []
    for fn in sorted(os.listdir(DATA)):
        if fn.startswith('_') or not fn.endswith('.json'):
            continue
        path = os.path.join(DATA, fn)
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        stem = fn[:-5]
        display = FILE2NAME.get(stem, stem)
        out.append((display, len(data)))
    out.sort(key=lambda x: -x[1])
    for name, n in out:
        print(f'{name}\t{n}')

def normalize(s):
    return re.sub(r'[\s　，。！？、,.!?…~～\-—\"\'`()（）《》]+', '', s)

def find(text, limit=20):
    all_ = load_all()
    nt = normalize(text)
    if not nt:
        return
    exact, sub, fuzzy = [], [], []
    char_set = set(nt)
    for e in all_:
        et = normalize(e['t'])
        if not et:
            continue
        if et == nt:
            exact.append(e)
        elif nt in et and len(nt) >= 2:
            sub.append(e)
        elif len(et) >= 4 and et in nt:
            sub.append(e)
        else:
            # fuzzy: bigram overlap + char-level Jaccard
            score = 0
            if len(nt) >= 3 and len(et) >= 3:
                bg1 = set(nt[i:i+2] for i in range(len(nt)-1))
                bg2 = set(et[i:i+2] for i in range(len(et)-1))
                bg_inter = len(bg1 & bg2)
                bg_union = len(bg1 | bg2) or 1
                bg_jacc = bg_inter / bg_union
                # char-level overlap (lenient)
                cs = set(et)
                ch_inter = len(char_set & cs)
                ch_min = min(len(char_set), len(cs)) or 1
                ch_ratio = ch_inter / ch_min
                # combined score
                score = bg_inter * 2 + ch_inter
                # accept if either: ≥2 shared bigrams, OR char overlap ≥60% with ≥3 shared chars
                if bg_inter >= 2 or (ch_ratio >= 0.6 and ch_inter >= 3):
                    fuzzy.append((score, e))
            elif len(nt) >= 2 and len(et) >= 2:
                # short queries: rely on char overlap
                cs = set(et)
                ch_inter = len(char_set & cs)
                if ch_inter >= 2 and ch_inter / (min(len(char_set), len(cs)) or 1) >= 0.6:
                    fuzzy.append((ch_inter, e))
    fuzzy.sort(key=lambda x: -x[0])
    fuzzy = [e for _, e in fuzzy]
    pool = exact + sub + fuzzy
    print(f'EXACT={len(exact)}  SUBSTR={len(sub)}  FUZZY={len(fuzzy)}')
    for e in pool[:limit]:
        np = e.get('np') or '(末尾)'
        print(f"[{e['i']}] {e['c']}：{e['t']}  →  {np}")

def show_next(idx, n=3):
    all_ = load_all()
    idx = int(idx)
    for j in range(idx, min(idx + 1 + n, len(all_))):
        e = all_[j]
        marker = '★' if j == idx else ' '
        print(f"{marker}[{e['i']}] {e['c']}：{e['t']}")

def show_around(idx, n=3):
    all_ = load_all()
    idx = int(idx)
    for j in range(max(0, idx - n), min(idx + n + 1, len(all_))):
        e = all_[j]
        marker = '★' if j == idx else ' '
        print(f"{marker}[{e['i']}] {e['c']}：{e['t']}")

def char_dump(name, keyword=None):
    data = load_char(name)
    nk = normalize(keyword) if keyword else None
    for e in data:
        if nk and nk not in normalize(e['text']):
            continue
        print(f"[{e['i']}] {e['text']}")

def char_sample(name, keyword):
    data = load_char(name)
    nk = normalize(keyword)
    for e in data:
        if nk in normalize(e['text']):
            prev = e.get('prev') or '(开头)'
            nx = e.get('next') or '(末尾)'
            print(f"[{e['i']}] PREV: {prev}")
            print(f"        SELF: {e['text']}  (len={len(e['text'])})")
            print(f"        NEXT: {nx}")

def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    cmd = sys.argv[1]
    if cmd == 'chars':
        list_chars()
    elif cmd == 'find':
        find(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 20)
    elif cmd == 'next':
        show_next(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3)
    elif cmd == 'around':
        show_around(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3)
    elif cmd == 'char':
        char_dump(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == 'sample':
        char_sample(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)

if __name__ == '__main__':
    main()
