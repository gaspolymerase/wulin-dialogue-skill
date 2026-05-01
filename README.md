# 武林外传台词互动 · Wulin-dialogue Skill

> 一个 [Claude Code](https://claude.com/claude-code) / [Claude Agent SDK](https://docs.anthropic.com/en/docs/claude-code/skills) skill：让 Claude 用《武林外传》全三季原剧台词跟你对话，或者跟你"对台词"接龙。
>
> A Claude Code skill that lets Claude chat with you using only original lines from the Chinese sitcom *Wǔlín Wàizhuàn (武林外传)*, or play a "finish-the-line" game with you across the entire script.

[简体中文](#-简体中文) · [English](#-english)

---

## 🀄 简体中文

### 这是什么？

一个把"和武林外传角色聊天"做成 Claude skill 的小项目。所有的回复都来自原剧台词库，**不是 LLM 生成的、不是模仿语气编造的**——Claude 只负责"在七万多句台词里挑一句最贴切的回给你"。

两种玩法：

- **聊天模式**：选一个角色（佟湘玉、白展堂、吕秀才、郭芙蓉、李大嘴、莫小贝、燕小六、祝无双、邢捕头、众人……近百位有 ≥10 句台词的角色都行），然后你说什么，"他/她"就用原剧台词回你什么。语义不一定百分百对得上，但那种"歪打正着"的喜感正是好玩的地方。
- **对台词模式**：你随便念一句剧里的台词（哪怕记得不太准，模糊匹配也能搜到），Claude 给你接下一句，可以一直接龙下去。

### 数据

- 收录：《武林外传》全三季 81 回剧本，约 39,847 句对白。
- 角色：97 位有 ≥10 句台词的角色，包括所有主角、常驻配角、客串。
- 来源：网络流传的剧本文字版（GB18030 编码原始 txt 已收录在 `武林外传全剧本/` 下，方便复现数据流程）。

### 安装

需要本机已经装好 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 或任何支持 Skills 的 Claude 客户端。

```bash
git clone https://github.com/<your-username>/wulin-dialogue.git
cd wulin-dialogue
./install.sh
```

`install.sh` 会把 `wulin-dialogue/` 整个软链接到 `~/.claude/skills/wulin-dialogue/`。装好后在任意 Claude Code 会话里输入：

```
/wulin-dialogue
```

或者直接说"我想和佟湘玉聊聊"、"咱们对个台词"，Claude 也会自动加载这个 skill。

> 不想装也行——直接把 `SKILL.md` 的内容贴给任何会调用本地 Python 和读 JSON 的 LLM agent，都能跑。

### 使用示例

```
你：聊天 佟湘玉
Claude：佟湘玉：额滴个神啊~~~ 你说这日子可咋过吧

你：我饿了
Claude：佟湘玉：大嘴，给客人下碗面去

你：对台词
Claude：好，您先来一句。

你：葵花点穴手
Claude：白展堂：你信不信我对你使葵花点穴手
       白展堂：(指)定！
```

### 项目结构

```
wulin-dialogue/                  ← repo 根目录
├── wulin-dialogue/              ← 实际安装的 skill 目录
│   ├── SKILL.md                 ← skill 入口与行为说明
│   ├── helper.py                ← 检索/搜索 CLI
│   └── data/
│       ├── _all.json            ← 全剧台词扁平索引（39,847 条）
│       ├── _chars.json          ← 中文名 ↔ 拼音 文件名映射
│       └── <pinyin>.json        ← 每个主要角色一份
├── scripts/
│   └── prepare_data.py          ← 从原始 txt 重新生成 data/
├── 武林外传全剧本/              ← 原始剧本（GB18030 txt）
├── install.sh                   ← 一键软链接到 ~/.claude/skills/
├── uninstall.sh
├── LICENSE
└── README.md
```

### 自己动手扩数据

如果你想加一位 skill 还没单独建文件的小配角，或者发现台词归类有误，可以改完原始 txt 之后跑：

```bash
python3 scripts/prepare_data.py
```

会重建 `wulin-dialogue/data/` 下的全部 JSON。

### `helper.py` 命令速查

| 命令 | 用途 |
| --- | --- |
| `helper.py chars` | 列出所有角色和台词数（按数量排序） |
| `helper.py find "<text>" [n]` | 在全剧搜某句话，分 EXACT/SUBSTR/FUZZY 三档返回（默认 20 条） |
| `helper.py next <idx> [n]` | 从某句开始往后看 n 条 |
| `helper.py around <idx> [n]` | 看某句前后各 n 条上下文 |
| `helper.py char <name> [keyword]` | 列出某角色全部台词（可加关键词过滤） |
| `helper.py sample <name> <keyword>` | 列出某角色含关键词的台词 + 上下文 |

角色名可以用中文（"佟湘玉"）也可以用拼音 slug（"tong_xiangyu"）。

### License

- 代码：MIT。
- 剧本台词：版权归原作者（编剧 宁财神 等）和制作方所有。本仓库收录原始剧本文字版仅供学术研究、个人学习与技术 demo 使用。如版权方有异议请提 issue，会立即下线相应数据。

---

## 🌐 English

### What is this?

A small Claude skill that lets you chat with characters from the classic Chinese sitcom **武林外传 (Wǔlín Wàizhuàn / *My Own Swordsman*)** — but every reply Claude gives is **a verbatim line from the original script**, not LLM-generated text. Claude's job is just to pick the most fitting line out of 39,847 lines of dialogue.

Two modes:

- **Chat mode** — Pick a character (any of ~97 characters with ≥10 lines), and Claude replies in their voice using only their actual lines from the show. Semantic match isn't always perfect — but that "almost right but hilariously off" vibe is the whole point.
- **Finish-the-line mode** — Quote a line from the show (fuzzy matching tolerates misremembered words, dropped characters, scrambled order), and Claude continues with the next line. Keeps going as long as you do.

### Data

- 81 episodes across all 3 seasons, ~39,847 lines of dialogue.
- 97 characters with ≥10 lines (mains, recurring side characters, guest stars).
- Source: a publicly circulating GB18030 text version of the script, included under `武林外传全剧本/` for reproducibility.

### Install

You need [Claude Code](https://docs.anthropic.com/en/docs/claude-code) or any Claude client that supports Skills.

```bash
git clone https://github.com/<your-username>/wulin-dialogue.git
cd wulin-dialogue
./install.sh
```

This symlinks `wulin-dialogue/` into `~/.claude/skills/wulin-dialogue/`. Then in Claude Code:

```
/wulin-dialogue
```

Or just say "I want to chat with 佟湘玉" / "let's play finish-the-line" and Claude will load it.

### Project layout

```
wulin-dialogue/                  ← repo root
├── wulin-dialogue/              ← the skill that gets installed
│   ├── SKILL.md
│   ├── helper.py
│   └── data/
├── scripts/prepare_data.py      ← rebuild data/ from the raw txt
├── 武林外传全剧本/              ← raw script (GB18030)
├── install.sh / uninstall.sh
├── LICENSE
└── README.md
```

### License

- Code: MIT.
- Script dialogue: copyright belongs to the original author(s) (screenwriter 宁财神 et al.) and producers. Included here for personal/educational use and as a tech demo. Will be removed promptly on rights-holder request.

### Credits

- Original screenplay: 宁财神 et al.
- Skill design & implementation: this repo's contributors.
- Built for the [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code/skills) ecosystem.
