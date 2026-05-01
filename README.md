# 武林外传台词互动 · Wulin-dialogue Skill

> 一个 [Claude Code](https://claude.com/claude-code) / [Claude Agent SDK](https://docs.anthropic.com/en/docs/claude-code/skills) skill：让 Claude 用《武林外传》全八十一回原剧台词跟你对话，或者跟你"对台词"接龙。
>
> A Claude Code skill that lets Claude chat with you using only original lines from the Chinese sitcom *Wǔlín Wàizhuàn (武林外传)* — all 81 episodes — or play a "finish-the-line" game with you across the entire script.

[简体中文](#-简体中文) · [English](#-english)

---

## 🀄 简体中文

### 这是什么？

一个把"和武林外传角色聊天"做成 Claude skill 的小项目。所有的回复都来自原剧台词库，**不是 LLM 生成的、不是模仿语气编造的**——Claude 只负责"在七万多句台词里挑一句最贴切的回给你"。

两种玩法：

- **聊天模式**：选一个角色（佟湘玉、白展堂、吕秀才、郭芙蓉、李大嘴、莫小贝、燕小六、祝无双、邢捕头、众人……近百位有 ≥10 句台词的角色都行），然后你说什么，"他/她"就用原剧台词回你什么。语义不一定百分百对得上，但那种"歪打正着"的喜感正是好玩的地方。
- **对台词模式**：你随便念一句剧里的台词（哪怕记得不太准，模糊匹配也能搜到），Claude 给你接下一句，可以一直接龙下去。

### 数据

- 收录：《武林外传》全 81 回剧本，约 39,847 句对白。
- 角色：97 位有 ≥10 句台词的角色，包括所有主角、常驻配角、客串。
- 来源：网络流传的剧本文字版（GB18030 编码原始 txt 已收录在 `武林外传全剧本/` 下，方便复现数据流程）。`武林外传全剧本/` 里那三个 txt 只是把全部 81 回随机切成了三份方便存放，**不对应播出时的三季**。

### 安装

根据你用哪种 Claude 客户端，挑下面一种装法：

#### 方法 A — Claude Code (CLI)

Claude Code 直接读本地文件夹，所以一行 `install.sh` 软链接过去就行：

```bash
git clone https://github.com/gaspolymerase/wulin-dialogue-skill.git
cd wulin-dialogue-skill
./install.sh
```

脚本会把 `wulin-dialogue/` 整个软链接到 `~/.claude/skills/wulin-dialogue/`（之后你在 repo 里改 `SKILL.md` 或 `helper.py`，Claude Code 立即生效，不用重装）。

装好后在任意 Claude Code 会话里输入：

```
/wulin-dialogue
```

或者直接说"我想和佟湘玉聊聊"、"咱们对个台词"，Claude 也会自动加载。

#### 方法 B — Claude 桌面端 / 网页版 (claude.ai)

桌面端和网页版只能上传 zip，所以先打个包：

```bash
git clone https://github.com/gaspolymerase/wulin-dialogue-skill.git
cd wulin-dialogue-skill
./scripts/build_zip.sh        # 生成 dist/wulin-dialogue.zip（约 3.8 MB）
```

然后在 Claude 客户端里：

1. 打开 **Settings → Customize → Skills**
2. 点右上角 **`+`** → **Create skill**
3. 把刚生成的 `dist/wulin-dialogue.zip` 拖进去（或选择文件上传）
4. 等 Claude 提示 skill 已就绪即可在对话里使用

> 没装 git 也行——可以从 GitHub 仓库右上角 **Code → Download ZIP** 下载整个仓库，解压后跑 `./scripts/build_zip.sh`。  
> 或者直接到本仓库的 [Releases](https://github.com/gaspolymerase/wulin-dialogue-skill/releases) 页面下载预打包好的 `wulin-dialogue.zip`（如有）。

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
│   ├── prepare_data.py          ← 从原始 txt 重新生成 data/
│   └── build_zip.sh             ← 打包成 zip 给桌面端/网页端上传
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

- All 81 episodes, ~39,847 lines of dialogue.
- 97 characters with ≥10 lines (mains, recurring side characters, guest stars).
- Source: a publicly circulating GB18030 text version of the script, included under `武林外传全剧本/` for reproducibility. The three `.txt` files inside that folder are just an arbitrary split of the 81 episodes for storage — they do **not** correspond to the show's three broadcast seasons.

### Install

Pick the path that matches your Claude client:

#### Option A — Claude Code (CLI)

Claude Code reads skills straight from disk, so a one-line symlink does it:

```bash
git clone https://github.com/gaspolymerase/wulin-dialogue-skill.git
cd wulin-dialogue-skill
./install.sh
```

This symlinks `wulin-dialogue/` into `~/.claude/skills/wulin-dialogue/`. Edits in the repo are picked up immediately — no reinstall needed.

In any Claude Code session:

```
/wulin-dialogue
```

Or just say "I want to chat with 佟湘玉" / "let's play finish-the-line" and Claude will load it.

#### Option B — Claude Desktop app / Claude.ai web

The desktop and web clients only accept zip uploads, so build a zip first:

```bash
git clone https://github.com/gaspolymerase/wulin-dialogue-skill.git
cd wulin-dialogue-skill
./scripts/build_zip.sh        # writes dist/wulin-dialogue.zip (~3.8 MB)
```

Then in the Claude client:

1. Open **Settings → Customize → Skills**
2. Top-right **`+`** → **Create skill**
3. Drop `dist/wulin-dialogue.zip` in (or use the file picker)
4. Wait for Claude to confirm the skill is ready, then start a chat

> No git? Use **Code → Download ZIP** on the repo page, unzip, then run `./scripts/build_zip.sh`. Or grab a prebuilt `wulin-dialogue.zip` from [Releases](https://github.com/gaspolymerase/wulin-dialogue-skill/releases) when available.

### Project layout

```
wulin-dialogue/                  ← repo root
├── wulin-dialogue/              ← the skill that gets installed
│   ├── SKILL.md
│   ├── helper.py
│   └── data/
├── scripts/
│   ├── prepare_data.py          ← rebuild data/ from the raw txt
│   └── build_zip.sh             ← package into a zip for Desktop/web upload
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
