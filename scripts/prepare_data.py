#!/usr/bin/env python3
"""Rebuild wulin-dialogue/data/ from the raw GB18030 script files.

Usage:
  python3 scripts/prepare_data.py                  # write into wulin-dialogue/data/
  python3 scripts/prepare_data.py --out ./newdata  # write somewhere else (safer)
  python3 scripts/prepare_data.py --min-lines 1    # include every named character

This is a reference implementation for how the bundled JSON dataset was built
from the raw script. The bundled `wulin-dialogue/data/` is the authoritative
copy — running this script should reproduce something close to it but is not
guaranteed to be byte-identical (the alias map below is hand-curated and may
miss minor speakers; PRs welcome).

Pipeline:
  1. Decode each `武林外传全剧本/*.txt` as gb18030.
  2. Walk lines: skip stage directions ("（...)"), pick up episode headers
     ("第X回 ..."), parse "speaker：text" pairs.
  3. Map alias speaker names → canonical character names via ALIASES.
  4. Build a global flat list (`_all.json`) and per-character files keyed by
     pinyin slug. Drop characters with fewer than --min-lines (default 10).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "武林外传全剧本"
DEFAULT_OUT = REPO_ROOT / "wulin-dialogue" / "data"

# Speaker alias → canonical display name. Order matters only for documentation;
# duplicates would be an error. Add aliases as you find them in the raw text.
ALIASES: dict[str, str] = {
    # 主角
    "掌柜": "佟湘玉", "掌柜的": "佟湘玉", "佟": "佟湘玉", "湘玉": "佟湘玉",
    "老白": "白展堂", "白": "白展堂", "展堂": "白展堂",
    "秀才": "吕秀才", "吕": "吕秀才", "吕轻侯": "吕秀才", "吕轻候": "吕秀才",
    "小郭": "郭芙蓉", "郭": "郭芙蓉", "芙蓉": "郭芙蓉",
    "大嘴": "李大嘴", "李": "李大嘴", "嘴": "李大嘴",
    "小贝": "莫小贝", "贝": "莫小贝", "莫": "莫小贝",
    "小六": "燕小六", "六": "燕小六", "燕": "燕小六",
    "无双": "祝无双", "双": "祝无双", "祝": "祝无双",
    # 常驻配角
    "老邢": "邢捕头", "邢": "邢捕头", "刑捕头": "邢捕头", "刑": "邢捕头",
    "包大人": "包大仁",
    "蕙兰": "杨蕙兰", "杨": "杨蕙兰",
    # 客串/小众（按需补充）
}

# Pinyin slug overrides for canonical names where pinyin would be ambiguous.
# Generated slugs use a simple pinyin transliteration if `pypinyin` is
# available; otherwise we fall back to the manual map below for known names.
SLUG_OVERRIDES: dict[str, str] = {
    # Main cast — pinyin overrides where the auto-generated slug would be ambiguous,
    # ugly, or differ from what's already shipped.
    "佟湘玉": "tong_xiangyu", "白展堂": "bai_zhantang", "吕秀才": "lv_xiucai",
    "郭芙蓉": "guo_furong", "李大嘴": "li_dazui", "莫小贝": "mo_xiaobei",
    "燕小六": "yan_xiaoliu", "祝无双": "zhu_wushuang", "邢捕头": "xing_butou",
    "众人": "zhongren", "包大仁": "bao_daren", "杨蕙兰": "yang_huilan",
    # Disambiguation for similar names that would otherwise collide
    "莫小宝": "mo_xiaobao",
    "金湘玉": "jin_xiangyu",
    "假老白": "jia_laobai", "真老白": "zhen_laobai", "黑衣老邢": "heiyi_laoxing",
}


def to_slug(name: str) -> str:
    if name in SLUG_OVERRIDES:
        return SLUG_OVERRIDES[name]
    try:
        from pypinyin import lazy_pinyin  # type: ignore
    except ImportError:
        sys.exit("pypinyin is required for slug generation. install with: pip install pypinyin")
    parts = lazy_pinyin(name)
    s = "_".join(p for p in parts if p)
    s = re.sub(r"[^a-z0-9_]", "", s.lower())
    return s or "unknown"


def parse_scripts() -> list[dict]:
    """Return a flat list of dialogue entries: {i, c, t, ep}."""
    out: list[dict] = []
    line_re = re.compile(r"^([^：:]{1,8})[：:](.*)$")
    ep_re = re.compile(r"^第[一二三四五六七八九十百零\d]+回")
    idx = 0

    if not RAW_DIR.exists():
        sys.exit(f"raw script directory not found: {RAW_DIR}")

    for path in sorted(RAW_DIR.glob("*.txt")):
        text = path.read_bytes().decode("gb18030", errors="replace")
        current_ep = ""
        for raw in text.split("\n"):
            line = raw.strip().rstrip()
            if not line:
                continue
            if line.startswith(("（", "(")):
                continue
            if ep_re.match(line):
                current_ep = line.split()[0]
                continue
            m = line_re.match(line)
            if not m:
                continue
            speaker, content = m.group(1).strip(), m.group(2).strip()
            if not content:
                continue
            speaker = ALIASES.get(speaker, speaker)
            out.append({"i": idx, "c": speaker, "t": content, "ep": current_ep})
            idx += 1
    return out


def build_outputs(entries: list[dict], min_lines: int) -> tuple[list[dict], dict, dict]:
    """Return (all_json, chars_json, per_char_json)."""
    # _all.json: flat list with i, c, t, np (next-person:line)
    all_list = []
    for k, e in enumerate(entries):
        nxt = entries[k + 1] if k + 1 < len(entries) else None
        np_str = f"{nxt['c']}：{nxt['t']}" if nxt else ""
        all_list.append({"i": e["i"], "c": e["c"], "t": e["t"], "np": np_str})

    # Per-character: keep entries with ≥ min_lines
    by_char: dict[str, list[dict]] = defaultdict(list)
    for k, e in enumerate(entries):
        prev = entries[k - 1] if k > 0 else None
        nxt = entries[k + 1] if k + 1 < len(entries) else None
        by_char[e["c"]].append({
            "i": e["i"],
            "ep": e["ep"],
            "text": e["t"],
            "prev": f"{prev['c']}：{prev['t']}" if prev else "",
            "next": f"{nxt['c']}：{nxt['t']}" if nxt else "",
        })

    chars_meta: dict[str, dict] = {}
    per_char: dict[str, list[dict]] = {}
    for name, lines in by_char.items():
        if len(lines) < min_lines:
            continue
        slug = to_slug(name)
        chars_meta[name] = {"slug": slug, "count": len(lines)}
        per_char[slug] = lines

    return all_list, chars_meta, per_char


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help=f"output directory (default: {DEFAULT_OUT})")
    ap.add_argument("--min-lines", type=int, default=5, help="characters with fewer lines are dropped (default 5)")
    args = ap.parse_args()

    entries = parse_scripts()
    print(f"parsed {len(entries)} dialogue lines", file=sys.stderr)

    all_list, chars_meta, per_char = build_outputs(entries, args.min_lines)
    print(f"kept {len(per_char)} characters with ≥{args.min_lines} lines", file=sys.stderr)

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "_all.json").write_text(
        json.dumps(all_list, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    (args.out / "_chars.json").write_text(
        json.dumps(chars_meta, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    for slug, lines in per_char.items():
        (args.out / f"{slug}.json").write_text(
            json.dumps(lines, ensure_ascii=False, indent=1), encoding="utf-8"
        )

    print(f"wrote {len(per_char) + 2} JSON files into {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
