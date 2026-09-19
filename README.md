# skillpack

Agent skills I use across my repos, for Claude Code and Codex, plus links to other people's skills I
rate. One folder per skill under `skills/`, each with a `SKILL.md` that says when it fires and what
it does. The categories below are the map. A skill lives in exactly one.

This is the pack half of a small family of agent tools: forges make things, packs bundle them.
[groundplane](https://github.com/ong6/groundplane), [jobforge](https://github.com/ong6/jobforge),
[skillforge](https://github.com/ong6/skillforge), [deckforge](https://github.com/ong6/deckforge),
[proofpack](https://github.com/ong6/proofpack), [fieldpack](https://github.com/ong6/fieldpack) and
[uipack](https://github.com/ong6/uipack) all run these skills.

## Install

**As a plugin** (Claude Code):

```
/plugin marketplace add ong6/skillpack
/plugin install skillpack@skillpack
```

**As a subtree** (any repo, both agents, edits flow back):

```sh
git subtree add --squash --prefix=.claude/shared-skills https://github.com/ong6/skillpack.git main
```

Then link the folders you want into `.claude/skills/` (and `.agents/skills/` for Codex), and
register `scripts/sync.sh --start` at SessionStart and `scripts/sync.sh --stop` at Stop. The
script keeps every consumer equal to this repo in both directions. See [Sync](#sync).

**Copy a single skill:** take its folder. Nothing depends on the rest of the tree except where a
skill links to another (`handoff` runs `unslop` over its output).

## Catalog

<!-- CATALOG START -->
### Writing

_How replies and documents read._

| Skill | Does |
|---|---|
| [`unslop`](skills/unslop/SKILL.md) | Strip AI tells from written output and give it a voice. Use before delivering any written artifact, and whenever the user says something reads like AI, sounds generic, or is too long. |
| [`wait-what`](skills/wait-what/SKILL.md) | Re-explain the last answer in plain language. Use only when the user invokes wait-what or says the reply was confusing, unclear, too technical, or did not land. |

Elsewhere:

- [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) — Compressed "caveman" prose for agents; cuts output tokens by about two thirds while keeping code and commands exact.
- [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) — Stops the agent burying the answer. Same aim as unslop from a different angle.

### Research & scraping

_Getting text out of the web and video._

| Skill | Does |
|---|---|
| [`web-extract`](skills/web-extract/SKILL.md) | Read, scrape or search the web through Firecrawl (CLI or MCP): a URL the user shares, a page WebFetch returns empty or 403 on, a JavaScript or Cloudflare-walled site, a public PDF, or a live web search. Not for YouTube (youtube-transcript) or LinkedIn (the domain stays off-limits). |
| [`youtube-transcript`](skills/youtube-transcript/SKILL.md) | Fetch clean transcripts or captions from YouTube URLs or video IDs. Use when the user shares a YouTube link or asks to transcribe, summarize, cite, or read a video. |

Elsewhere:

- [firecrawl/firecrawl-claude-plugin](https://github.com/firecrawl/firecrawl-claude-plugin) — Firecrawl's official plugin. web-extract wraps the same CLI.
- [tavily-ai/skills](https://github.com/tavily-ai/skills) — Search, extract, crawl and deep research over the Tavily API.
- [exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server) — Neural web search and page fetch as an MCP server.

### Design

_Diagrams, interfaces, visual judgment._

| Skill | Does |
|---|---|
| [`system-diagram`](skills/system-diagram/SKILL.md) | Draw a polished system or architecture diagram as hand-authored inline SVG: request flows, RAG and agent pipelines, ingest queues, service maps, before/after comparisons. Use for "system diagram", "architecture diagram", "draw the flow", "diagram how X works", or a figure for a website, a case study, a README, or a research note. Not for charts of data (dataviz), UI mockups (design), or a one-hop relationship that a sentence explains faster. |
| [`3d-design`](skills/3d-design/SKILL.md) | Choose and use a 3D design workflow for UI illustrations, modeled objects, character animation, interactive scenes and web delivery. Use for "3D design", "3D animation", "model this", "Blender or Three.js", "make the movement natural", or selecting and switching 3D tools. Covers authoring, runtime, export and visual verification; not ordinary page layout, 2D architecture diagrams or unrelated Blender installation troubleshooting. |

Elsewhere:

- [tt-a1i/archify](https://github.com/tt-a1i/archify) — Turns a codebase or a description into interactive architecture and sequence diagrams as self-contained HTML.
- [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) — UI and UX guidance for agents building interfaces. Large; its 119-rule usability list is the useful part.
- [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) — Aesthetic judgment for generated frontends.

### Documents

_Producing files people print or send._

| Skill | Does |
|---|---|
| [`markdown-to-pdf`](skills/markdown-to-pdf/SKILL.md) | Convert a markdown note into a verified, print-ready A4 PDF. Use for printable notes, meeting handouts, or rebuilding generated PDFs; not for editing existing PDFs or building a LaTeX document. |

Elsewhere:

- [anthropics/skills](https://github.com/anthropics/skills) — Anthropic's docx, pdf, pptx and xlsx skills live here (source-available, not open source).

### Workflows & agents

_How sessions hand off, improve, and stay honest._

| Skill | Does |
|---|---|
| [`handoff`](skills/handoff/SKILL.md) | Compact the current conversation into a handoff document. Use when the user asks for a handoff, continuation brief, or context package for another session or agent. |
| [`feedback-loop`](skills/feedback-loop/SKILL.md) | Capture the owner's feedback about how the agent, a skill, a hook, a rule, or a reply behaved, log it in feedback.md, and patch whatever it targets in the same session so the behaviour changes by default. Fires on "don't do X", "stop doing", "why does it", "next time", "I prefer", "that was wrong", "that's annoying", "can I turn this off", "always" or "never" about agent behaviour, or a correction to a reply; not for feedback on the owner's own writing, on other people, or a one-off instruction for the current task. |

Elsewhere:

- [mattpocock/skills](https://github.com/mattpocock/skills) — Matt Pocock's engineering set. grill-me, tdd, to-spec, implement, code-review, diagnosing-bugs.
- [obra/superpowers](https://github.com/obra/superpowers) — Brainstorm, plan, TDD, review as one methodology.
- [dietrichgebert/ponytail](https://github.com/dietrichgebert/ponytail) — Pushes the agent to reuse the standard library and platform features before adding code or dependencies.
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — Production-grade engineering discipline for coding agents.
- [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) — One CLAUDE.md distilled from Karpathy's notes on LLM coding pitfalls.

### Career

_Interview drilling, resumes, job search. The private versions stay in my store; these are the public extractions._

Elsewhere:

- [ong6/jobforge](https://github.com/ong6/jobforge) — My interview-prep plugin. Grades the plan you say out loud before you code, records real interviews as state, schedules what broke. Six skills and a SessionStart drill banner.
- [ong6/groundplane](https://github.com/ong6/groundplane) — My deterministic-boundary library for agent output. Not a skill, but the reference for what an agent may generate versus what code must produce.
- [ong6/skillforge](https://github.com/ong6/skillforge) — My skill workbench. Discovers, versions and evaluates skills against a baseline; the place a skill from here gets measured before it stays.
- [ong6/fieldpack](https://github.com/ong6/fieldpack) — My local-first field suite. deckforge (presentations), skillforge (skill evaluation) and proofpack (pilot evidence) as one install.
- [kirilxd/swe-interview-coach](https://github.com/kirilxd/swe-interview-coach) — Behavioural and system-design prep for Claude Code. jobforge's harness and reference designs derive from it.

### Productivity

_Capture, scheduling, personal routines. Nothing published yet._

### Collections & indexes

_Where to look when none of the above fits._

Elsewhere:

- [anthropics/skills](https://github.com/anthropics/skills) — The official reference set and the Agent Skills spec.
- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) — Curated index of Claude skills and tooling.
<!-- CATALOG END -->

## Sync

`scripts/sync.sh` keeps a subtree copy and this repo equal, in both directions, from inside the
consumer repo.

| Mode | When | Does |
|---|---|---|
| `--start` | session start | merge the last background fetch (local); fetch again in the background |
| `--stop` | session end | commit folder edits, merge upstream if it moved, push, record the sync point |
| `--status` | by hand | print prefix, remote, local tree, last synced point |

State lives in `.git/skills-sync`, per clone. A conflict aborts the merge, leaves the tree clean and
exits 2 with the command to resolve it. A missing network or an empty upstream never fails a hook.
The first `--start` on a new clone fetches synchronously; subsequent starts use the cached ref.
Commits include only the skills folder, even if other files are staged. Unrelated staged, unstaged
or untracked work defers merging and pushing, leaving the recorded sync point unchanged. An
existing merge, rebase, cherry-pick, revert or unmerged index defers the whole sync before a commit.
The next run retries after that work is resolved.
The first `--stop` against an empty upstream creates it from the folder. Overrides:
`SKILLS_SYNC_URL`, `SKILLS_SYNC_REMOTE` (default `skills`), `SKILLS_SYNC_BRANCH` (default `main`).

`bash scripts/test-sync.sh` exercises temporary consumers and bare remotes without network access,
including bootstrap, conflicts, unrelated staged work and existing Git operations.

## Maintaining

- Add a skill: folder under `skills/`, add its name to a category in `catalog.yaml`, run
  `python3 scripts/build-catalog.py`. The build fails if the tree and the catalog disagree.
- Add a link: a `repo` and a one-line `note` under a category's `links`, then rebuild.
- Keep skills generic. Anything that names a private path, account or price stays in the consumer
  repo.

## Licence

MIT for everything here. Linked repos carry their own licences.
