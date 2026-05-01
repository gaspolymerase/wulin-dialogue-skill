# wulin-dialogue

一个 Claude skill：让 Claude 用《武林外传》全 81 回原剧台词跟你对话，或者陪你"对台词"接龙。所有回复都是从 39,847 句原剧台词里检索出来的——**不是 LLM 生成的，没有改写、没有拼接**。

A Claude skill that chats with you using only verbatim lines from all 81 episodes of the Chinese sitcom *Wǔlín Wàizhuàn (武林外传)*. Every reply is retrieved from a 39,847-line script index — nothing is generated, paraphrased, or stitched together.

---

## 中文

### 三种玩法

- **聊天模式**：选一个角色（佟湘玉、白展堂、吕秀才、郭芙蓉、李大嘴、莫小贝、燕小六、祝无双……共 125+ 位有 ≥5 句台词的角色，主角到客串都齐了），你说什么，"他/她"就用原剧台词回你什么。
- **对台词模式**：你随便念一句剧里的台词（记不准也没关系，模糊匹配），Claude 给你接下一句，可以一直接龙下去。
- **答案之书**：随便说一句话/问题/心情（不一定是剧里的），Claude 从全剧 39,847 句台词里挑一句最贴的回你。同一个问题再问会得到不同的"签"。

### 安装

#### 方法 A — Claude Code（CLI）

Claude Code 直接读本地文件夹：

```bash
git clone https://github.com/gaspolymerase/wulin-dialogue-skill.git
cd wulin-dialogue-skill
./install.sh
```

`install.sh` 会把 `wulin-dialogue/` 软链接到 `~/.claude/skills/wulin-dialogue/`。

之后在任意 Claude Code 会话里输入 `/wulin-dialogue`，或者直接说"我想和佟湘玉聊聊"、"咱们对个台词"，Claude 都会自动加载。

#### 方法 B — Claude 桌面端 / 网页版（claude.ai）

桌面端和网页版只能上传 zip。

1. 从 [Releases](https://github.com/gaspolymerase/wulin-dialogue-skill/releases/latest) 下载 `wulin-dialogue.zip`（约 3.8 MB）。
2. 打开 Claude 客户端 → **Settings → Customize → Skills**。
3. 点右上角 **`+` → Create skill**，把 zip 拖进去上传。
4. 上传完成后开始对话即可。

> 想自己改完再上传，可以 clone 仓库后跑 `./scripts/build_zip.sh` 重新打包。

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

### 数据来源

剧本文字版来自网络流传版本，编码为 GB18030，已收录在 `武林外传全剧本/` 下方便复现数据流程。**那三个 .txt 只是把全部 81 回随机切成了三份方便存放，不对应播出时的三季。**

要重建数据：

```bash
python3 scripts/prepare_data.py
```

### 项目结构

```
wulin-dialogue-skill/
├── wulin-dialogue/              实际安装的 skill 目录
│   ├── SKILL.md                 skill 行为说明
│   ├── helper.py                检索 CLI
│   └── data/
│       ├── _all.json            全剧台词扁平索引（39,847 条）
│       ├── _chars.json          中文名 ↔ 拼音 文件名映射
│       └── <pinyin>.json        每个主要角色一份
├── scripts/
│   ├── prepare_data.py          从原始 txt 重建 data/
│   └── build_zip.sh             打包 zip 给桌面端/网页端上传
├── 武林外传全剧本/              原始剧本（GB18030 txt）
├── install.sh / uninstall.sh    Claude Code 软链接安装
├── LICENSE
└── README.md
```

### License

代码采用 MIT 协议。剧本台词版权归原作者（编剧 宁财神 等）和制作方所有；本仓库收录仅供个人学习、学术研究和技术演示。如版权方有异议请提 issue，将立即下线。

---

## English

### Three modes

- **Chat mode** — Pick a character (125+ with ≥5 lines: 佟湘玉, 白展堂, 吕秀才, 郭芙蓉, 李大嘴, 莫小贝, 燕小六, 祝无双, plus the long tail of side characters and walk-ons). Whatever you say, Claude replies with one of their actual lines from the show.
- **Finish-the-line mode** — Quote a line you remember (fuzzy match tolerates dropped/wrong characters). Claude continues with the next line, and the next, as long as you keep going.
- **Book of Answers (答案之书)** — Say anything (a question, a feeling, a complaint — doesn't have to be a script line). Claude picks one line from across the full 39,847-line script as a fortune-style reply. Ask the same thing twice, get a different "draw."

### Install

#### Option A — Claude Code (CLI)

Claude Code reads skills straight from disk:

```bash
git clone https://github.com/gaspolymerase/wulin-dialogue-skill.git
cd wulin-dialogue-skill
./install.sh
```

This symlinks `wulin-dialogue/` into `~/.claude/skills/wulin-dialogue/`.

In any Claude Code session, type `/wulin-dialogue` or just say "let's play finish-the-line" / "chat as 佟湘玉".

#### Option B — Claude Desktop app / Claude.ai web

The GUI clients only accept zip uploads.

1. Download `wulin-dialogue.zip` (~3.8 MB) from the [latest release](https://github.com/gaspolymerase/wulin-dialogue-skill/releases/latest).
2. Open Claude → **Settings → Customize → Skills**.
3. Click the top-right **`+` → Create skill** and drop the zip in.
4. Wait for the upload to finish, then start a chat.

> To customize the skill before uploading, clone the repo and run `./scripts/build_zip.sh` to repackage.

### Data

The script text comes from a publicly circulating GB18030 version, included under `武林外传全剧本/` for reproducibility. The three `.txt` files there are an arbitrary storage split of all 81 episodes — they do **not** correspond to the show's three broadcast seasons.

Rebuild from source:

```bash
python3 scripts/prepare_data.py
```

### License

Code: MIT. Script dialogue: copyright belongs to the original screenwriter(s) (宁财神 et al.) and producers. Included here for personal/educational use only and removed promptly on rights-holder request.

### Credits

Original screenplay: 宁财神 et al. Built for the [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code/skills) ecosystem.
