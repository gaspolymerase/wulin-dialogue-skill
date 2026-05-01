#!/usr/bin/env python3
"""武林外传 dialogue skill helper.

Usage:
  helper.py chars                       List characters and line counts.
  helper.py find "<text>"               Find lines whose text contains/matches <text>.
                                        Returns up to 20 candidates with index, char, text, next-line.
  helper.py oracle "<prompt>" [seed]    "Book of Answers" mode. Pick ONE line from
                                        the entire script as a fortune-style reply
                                        to the prompt. Weighted random over a
                                        relevance-scored pool, so repeated calls
                                        give variety. Pass an integer seed for a
                                        reproducible pick.
  helper.py pool "<prompt>" [n]         Print top-n (default 12) oracle-scored
                                        candidates without picking. Use when you
                                        want to choose among broader interpretations
                                        (direct answer / extension / restatement /
                                        vibes-match) instead of a single random pick.
  helper.py next <idx> [n]              Show line at idx and next n lines (default n=3).
  helper.py around <idx> [n]            Show n lines before and after idx (default n=3).
  helper.py char <name> [keyword]       Dump lines for character; optional keyword filter.
                                        Without keyword, prints all (large for main characters).
  helper.py sample <name> <keyword>     Sample lines containing keyword for given character,
                                        with prev/next context.
"""
import json, sys, os, re, random, math

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

def _search(text):
    """Categorize matches against `text`. Returns (exact, sub, fuzzy_with_scores).
    `exact` and `sub` are lists of entry dicts; `fuzzy_with_scores` is a list of
    (score, entry) tuples sorted by descending score.
    """
    all_ = load_all()
    nt = normalize(text)
    if not nt:
        return [], [], []
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
            if len(nt) >= 3 and len(et) >= 3:
                bg1 = set(nt[i:i+2] for i in range(len(nt)-1))
                bg2 = set(et[i:i+2] for i in range(len(et)-1))
                bg_inter = len(bg1 & bg2)
                cs = set(et)
                ch_inter = len(char_set & cs)
                ch_min = min(len(char_set), len(cs)) or 1
                ch_ratio = ch_inter / ch_min
                score = bg_inter * 2 + ch_inter
                if bg_inter >= 2 or (ch_ratio >= 0.6 and ch_inter >= 3):
                    fuzzy.append((score, e))
            elif len(nt) >= 2 and len(et) >= 2:
                cs = set(et)
                ch_inter = len(char_set & cs)
                if ch_inter >= 2 and ch_inter / (min(len(char_set), len(cs)) or 1) >= 0.6:
                    fuzzy.append((ch_inter, e))
    fuzzy.sort(key=lambda x: -x[0])
    return exact, sub, fuzzy


def find(text, limit=20):
    exact, sub, fuzzy_scored = _search(text)
    fuzzy = [e for _, e in fuzzy_scored]
    pool = exact + sub + fuzzy
    print(f'EXACT={len(exact)}  SUBSTR={len(sub)}  FUZZY={len(fuzzy)}')
    for e in pool[:limit]:
        np = e.get('np') or '(末尾)'
        print(f"[{e['i']}] {e['c']}：{e['t']}  →  {np}")


# Lines this short are usually filler ("啊", "嗯", "对") — exclude from oracle picks.
ORACLE_MIN_LEN = 5
# Cap pool size; relevance plummets after the top ~50 fuzzy hits.
ORACLE_POOL_CAP = 60


def _oracle_candidates(prompt):
    """Return a list of (weight, entry) sorted by descending weight, using
    relevance × length-boost × tier-weight scoring.
    - tier-weight: EXACT=8, SUBSTR=5, FUZZY=fuzzy_score_normalized to 0..1
    - length-boost: log10(len)+1, so 30-char金句 beats 5-char短句 ~2×
    Filler lines (< ORACLE_MIN_LEN) are dropped.
    """
    exact, sub, fuzzy_scored = _search(prompt)
    candidates = []
    for e in exact:
        if len(e['t']) >= ORACLE_MIN_LEN:
            candidates.append((8.0 * (math.log10(len(e['t'])) + 1), e))
    for e in sub:
        if len(e['t']) >= ORACLE_MIN_LEN:
            candidates.append((5.0 * (math.log10(len(e['t'])) + 1), e))
    if fuzzy_scored:
        max_fz = max(s for s, _ in fuzzy_scored) or 1
        for score, e in fuzzy_scored[:ORACLE_POOL_CAP]:
            if len(e['t']) >= ORACLE_MIN_LEN:
                norm = score / max_fz
                candidates.append((norm * (math.log10(len(e['t'])) + 1), e))
    candidates.sort(key=lambda x: -x[0])
    return candidates


def oracle(prompt, seed=None):
    """Pick ONE line from the entire script as a 'book of answers' reply.
    Weighted random over the scored candidate pool, so the same prompt yields
    different draws across calls. Falls back to a random金句-length line when
    no semantic match exists.
    """
    rng = random.Random(seed)
    candidates = _oracle_candidates(prompt)
    if not candidates:
        all_ = load_all()
        long_lines = [e for e in all_ if 12 <= len(e['t']) <= 80]
        chosen = rng.choice(long_lines) if long_lines else rng.choice(all_)
    else:
        weights = [w for w, _ in candidates]
        chosen = rng.choices([e for _, e in candidates], weights=weights, k=1)[0]
    print(f"[{chosen['i']}] {chosen['c']}：{chosen['t']}")


def pool(prompt, n=12):
    """Print the top-N oracle-scored candidates without picking one. Lets the
    caller (typically the LLM running the skill) read multiple options and
    choose based on broader semantic interpretation — direct answer,
    extension of the topic, restatement, or vibes-match.
    """
    candidates = _oracle_candidates(prompt)
    if not candidates:
        print(f"(no candidates for {prompt!r})")
        return
    for _, e in candidates[:n]:
        print(f"[{e['i']}] {e['c']}：{e['t']}")

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
    elif cmd == 'oracle':
        seed = int(sys.argv[3]) if len(sys.argv) > 3 else None
        oracle(sys.argv[2], seed)
    elif cmd == 'pool':
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 12
        pool(sys.argv[2], n)
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
