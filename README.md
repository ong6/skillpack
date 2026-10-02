# skills

My public agent skills for Claude Code and Codex. Each skill is one folder under `skills/`, and its
`SKILL.md` says when it fires and what it does. Every skill belongs to exactly one category in
`catalog.yaml`. Nothing here holds personal data: guard, lint and CI run before every push.

## Install

**One skill:** link or copy its folder into a repo. Nothing depends on the rest of the tree.

```sh
git clone https://github.com/ong6/skills.git
ln -s "$PWD/skills/skills/handoff" /path/to/repo/.claude/skills/handoff   # Claude Code
ln -s "$PWD/skills/skills/handoff" /path/to/repo/.agents/skills/handoff   # Codex
```

**Everything, per machine:** clone into a root folder, then let `bin/skills` link what the
machine's profile enables and keep it current.

```sh
git clone https://github.com/ong6/skills.git <root>/skills
<root>/skills/bin/skills up --repo <repo> --machines <machines.json>
```

**As a Claude Code plugin:** `/plugin marketplace add ong6/skills`, then
`/plugin install skills@ong6-skills`.

## bin/skills

A single-file, stdlib-only Python CLI (3.7+). It never starts a model session.

| Command | Does |
|---|---|
| `up --repo R --machines M [--hook claude\|codex] [--wait]` | match the profile; clone missing checkouts and fetch + fast-forward clean ones in the background; link; register Claude local-scope MCP servers; print one status line (plus `reloadSkills` hook output when links changed) |
| `link` / `unlink --repo R --machines M` | create the enabled links and remove stale ones / remove every link into the checkouts |
| `doctor --repo R --machines M [--json]` | report profile, links, dangling links, dirty checkouts, last fetch; exit 1 on problems |
| `guard [PATH...]` | public-safety scan; exit 2 on hits |
| `publish --checkout C -m MSG` | lock, guard (public checkout), lint changed skills, commit, push |

The profile is the `skills` object of the first machine in the registry whose `match` fields all
equal this host's (`os`, `model`, `hostname` prefix, `wsl`, `user`):

```json
{"machines": [{"match": {"os": "Linux", "hostname": "devbox"}, "name": "Dev box",
  "skills": {"scope": "project", "root": "~/src", "private": false,
             "repos": ["~/src/notes"], "enable": ["*"], "disable": ["category:design"],
             "mcp": []}}]}
```

- `scope: project` links into `<repo>/.claude/skills` and `<repo>/.agents/skills` for `--repo` and
  each of `repos`, and removes our links from `~/.claude/skills` and `~/.agents/skills`.
  `scope: user` links into those two home folders instead.
- `root` holds the checkouts `<root>/skills` and `<root>/skills-private` (default `~/Sideproject`). <!-- public-guard: allow -->
- `enable` and `disable` take skill names, globs and `category:<key>`.
- No matching machine means project scope, `--repo` only, public skills only.
- Only symlinks that point into the two checkouts are ever created or removed. Anything else in a
  link folder is left alone and reported as a conflict.
- A Claude Code SessionStart hook can run
  `bin/skills up --repo "$CLAUDE_PROJECT_DIR" --machines <file> --hook claude`.
  `up` never prompts and always exits 0, and it returns in well under a second when nothing changed.

## Public and private

- **Public** (this repo): shareable skills with no personal information.
- **Private** (`skills-private`, a separate private repo): skills that name their owner's paths,
  accounts or voice, plus `mcp/servers.json` and `guard-terms.txt`. Private skills may compose
  public ones by name. Public skills never reference private ones.
- When both repos have a skill of the same name, the private one wins on machines that link private.
- `bin/skills guard` blocks home-directory paths, personal email addresses, phone numbers, NRIC/FIN
  numbers, private keys, tokens, the owner terms in `skills-private/guard-terms.txt` and AI-CLI
  launches (`codex exec`, `claude -p`) from skill code. To keep a deliberate line, add
  `public-guard: allow` to it.
- Skills are location-independent. They refer to other skills by name and never resolve their own
  symlink to find siblings.

## Included skills

The skill index and catalog below are generated from `catalog.yaml` and each skill's frontmatter.
CI fails when they drift.

<!-- SKILL INDEX START -->
| Skill | What I use it for |
|---|---|
| [`web-extract`](skills/web-extract/SKILL.md) | Read, search and scrape difficult web pages through Firecrawl. |
| [`youtube-transcript`](skills/youtube-transcript/SKILL.md) | Fetch clean captions from a YouTube video. |
| [`refine`](skills/refine/SKILL.md) | Review and improve the work until its constraints and requested score pass. |
| [`handoff`](skills/handoff/SKILL.md) | Leave a compact continuation brief for the next agent or session. |
| [`markdown-to-pdf`](skills/markdown-to-pdf/SKILL.md) | Turn a Markdown note into a checked, print-ready A4 PDF. |
| [`system-diagram`](skills/system-diagram/SKILL.md) | Turn a real system flow into a polished, readable SVG figure. |
| [`3d-design`](skills/3d-design/SKILL.md) | Choose the right authoring and browser workflow for a 3D object or animation. |
| [`blender-authoring`](skills/blender-authoring/SKILL.md) | Build, animate, render and export Blender scenes with Python. |
| [`feedback-loop`](skills/feedback-loop/SKILL.md) | Record feedback and patch the skill or rule that caused it in the same session. |
<!-- SKILL INDEX END -->

## Catalog

<!-- CATALOG START -->
### Research

_Getting text and data out of the web and video._

| Skill | Does |
|---|---|
| [`web-extract`](skills/web-extract/SKILL.md) | Read or extract a web page with a local readability fetch first, escalating to Firecrawl only for JavaScript shells, blocked/thin results, public PDFs, structured extraction or browser interaction. Also use for live web searches that need Firecrawl. Not for YouTube (youtube-transcript) or LinkedIn (off-limits). |
| [`youtube-transcript`](skills/youtube-transcript/SKILL.md) | Fetch clean transcripts or captions from YouTube URLs or video IDs. Use when the user shares a YouTube link or asks to transcribe, summarize, cite, or read a video. |

Elsewhere:

- [firecrawl/firecrawl-claude-plugin](https://github.com/firecrawl/firecrawl-claude-plugin) — Firecrawl's official plugin. web-extract wraps the same CLI.
- [tavily-ai/skills](https://github.com/tavily-ai/skills) — Search, extract, crawl and deep research over the Tavily API.
- [exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server) — Neural web search and page fetch as an MCP server.

### Writing

_How replies, briefs and documents read, and how sessions hand off._

| Skill | Does |
|---|---|
| [`refine`](skills/refine/SKILL.md) | Explicit-only. Improve the latest deliverable (draft, code, plan, note, design) through fresh independent reviewer agents until it meets the requested score and all explicit constraints, or three refinement rounds pass. Use for "/refine", "refine this", "run the refine loop", "auto-improve this". Not for a single quick edit, a PR or diff review (code-review), or feedback about agent behaviour (feedback-loop). |
| [`handoff`](skills/handoff/SKILL.md) | Compact the current conversation into a handoff document. Use when the user asks for a handoff, continuation brief, or context package for another session or agent. |
| [`markdown-to-pdf`](skills/markdown-to-pdf/SKILL.md) | Convert a markdown note into a verified, print-ready A4 PDF. Use for printable notes, meeting handouts, or rebuilding generated PDFs; not for editing existing PDFs or building a LaTeX document. |

Elsewhere:

- [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) — Compressed "caveman" prose for agents; cuts output tokens by about two thirds while keeping code and commands exact.
- [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) — Stops the agent burying the answer.
- [anthropics/skills](https://github.com/anthropics/skills) — Anthropic's docx, pdf, pptx and xlsx skills live here (source-available, not open source).

### Design

_Diagrams, interfaces, 3D and visual judgment._

| Skill | Does |
|---|---|
| [`system-diagram`](skills/system-diagram/SKILL.md) | Draw a polished system or architecture diagram as hand-authored inline SVG: request flows, RAG and agent pipelines, ingest queues, service maps, before/after comparisons. Use for "system diagram", "architecture diagram", "draw the flow", "diagram how X works", or a figure for a website, a case study, a README, or a research note. Not for charts of data (dataviz), UI mockups (design), or a one-hop relationship that a sentence explains faster. |
| [`3d-design`](skills/3d-design/SKILL.md) | Choose and use a 3D design workflow for UI illustrations, modeled objects, character animation, interactive scenes and web delivery. Use for "3D design", "3D animation", "model this", "Blender or Three.js", "make the movement natural", "seamless loop", "continuous pan", or selecting and switching 3D tools. Covers authoring, runtime, export and visual verification; not ordinary page layout, 2D architecture diagrams or unrelated Blender installation troubleshooting. |
| [`blender-authoring`](skills/blender-authoring/SKILL.md) | Create, edit, animate, export and render Blender scenes using headless Python (bpy). Use after 3d-design selects Blender, or when the user explicitly requests Blender or a blend file. Covers geometry, materials, rigging, animation, lighting and export. Not for choosing between 3D tools, Three.js playback or ordinary page layout. |

Elsewhere:

- [tt-a1i/archify](https://github.com/tt-a1i/archify) — Turns a codebase or a description into interactive architecture and sequence diagrams as self-contained HTML.
- [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) — UI and UX guidance for agents building interfaces. Large; its 119-rule usability list is the useful part.
- [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) — Aesthetic judgment for generated frontends.

### Life

_Trips, shopping, property and learning._

### Career

_Interview drilling and job-search practice._

Elsewhere:

- [kirilxd/swe-interview-coach](https://github.com/kirilxd/swe-interview-coach) — Behavioural and system-design prep for Claude Code.

### Field engineering

_Customer-facing decks and pilot evidence for forward-deployed work._

### Skill building

_Making, testing and improving the skills themselves._

| Skill | Does |
|---|---|
| [`feedback-loop`](skills/feedback-loop/SKILL.md) | Capture the owner's feedback about how the agent, a skill, a hook, a rule, or a reply behaved, log it in feedback.md, and patch whatever it targets in the same session so the behaviour changes by default. Fires on "don't do X", "stop doing", "why does it", "next time", "I prefer", "that was wrong", "that's annoying", "can I turn this off", "always" or "never" about agent behaviour, or a correction to a reply; not for feedback on the owner's own writing, on other people, or a one-off instruction for the current task. |

Elsewhere:

- [anthropics/skills](https://github.com/anthropics/skills) — The official reference set and the Agent Skills spec.
- [mattpocock/skills](https://github.com/mattpocock/skills) — Matt Pocock's engineering set. grill-me, tdd, to-spec, implement, code-review, diagnosing-bugs.
- [obra/superpowers](https://github.com/obra/superpowers) — Brainstorm, plan, TDD, review as one methodology.
- [dietrichgebert/ponytail](https://github.com/dietrichgebert/ponytail) — Pushes the agent to reuse the standard library and platform features before adding code or dependencies.
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — Production-grade engineering discipline for coding agents.
- [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) — One CLAUDE.md distilled from Karpathy's notes on LLM coding pitfalls.
- [ong6/groundplane](https://github.com/ong6/groundplane) — My deterministic-boundary library for agent output. Not a skill, but the reference for what an agent may generate versus what code must produce.
- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) — Curated index of Claude skills and tooling.
<!-- CATALOG END -->

## Licence

MIT for everything here. Linked repos carry their own licences. Contributions are welcome; see
[CONTRIBUTING.md](CONTRIBUTING.md). Report security issues privately as described in [SECURITY.md](SECURITY.md).
