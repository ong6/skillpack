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
| [`save-video`](skills/save-video/SKILL.md) | File a YouTube video as a searchable note with takeaways, category and tags. |
| [`datastore`](skills/datastore/SKILL.md) | Keep structured records as append-only JSONL with a local SQLite cache for SQL. |
| [`refine`](skills/refine/SKILL.md) | Review and improve the work until its constraints and requested score pass. |
| [`handoff`](skills/handoff/SKILL.md) | Leave a compact continuation brief for the next agent or session. |
| [`write-a-brief`](skills/write-a-brief/SKILL.md) | Write or tighten a one-to-two-page brief for a meeting with a professional. |
| [`review-a-quote`](skills/review-a-quote/SKILL.md) | Review a vendor or construction quote line by line and separate what to ask now. |
| [`markdown-to-pdf`](skills/markdown-to-pdf/SKILL.md) | Turn a Markdown note into a checked, print-ready A4 PDF. |
| [`system-diagram`](skills/system-diagram/SKILL.md) | Turn a real system flow into a polished, readable SVG figure. |
| [`ux-design`](skills/ux-design/SKILL.md) | Audit or design a page's UX against a usability checklist before visual polish. |
| [`3d-design`](skills/3d-design/SKILL.md) | Choose the right authoring and browser workflow for a 3D object or animation. |
| [`blender-authoring`](skills/blender-authoring/SKILL.md) | Build, animate, render and export Blender scenes with Python. |
| [`trip-planner`](skills/trip-planner/SKILL.md) | Plan or replan a trip with live research on routes, hours, parking and food. |
| [`product-shopping`](skills/product-shopping/SKILL.md) | Decide what to buy, or find the best legitimate price for a chosen model. |
| [`compare-price`](skills/compare-price/SKILL.md) | Compare one product's landed cost across countries in a single currency. |
| [`evaluate-condo`](skills/evaluate-condo/SKILL.md) | Evaluate a Singapore condo listing or development and file a cited verdict. |
| [`teach`](skills/teach/SKILL.md) | Run a stateful, multi-session course on a topic in a learning workspace. |
| [`interview-prep`](skills/interview-prep/SKILL.md) | Mock interviews from your own resume, with spoken-plan grading, drills, debriefs, system design. |
| [`create-fde-deck`](skills/create-fde-deck/SKILL.md) | Write evidence-labelled field-engineering decks: discovery, architecture, pilot readout. |
| [`review-fde-deck`](skills/review-fde-deck/SKILL.md) | Audit a field-engineering deck for logic, evidence, honesty, density and next steps. |
| [`track-pilot-evidence`](skills/track-pilot-evidence/SKILL.md) | Track pilot criteria, evidence and risks where agents propose and humans decide. |
| [`skillsmith`](skills/skillsmith/SKILL.md) | Make a skill from the repo, then keep it only if it beats the same model without it. |
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
| [`save-video`](skills/save-video/SKILL.md) | Save a YouTube video into the video library of the host repo as a note with overview, key takeaways, category and tags, indexed for later search. Use for "save this video", "add this to my videos", a YouTube link with "keep/remember/save", or "what videos do I have on X" (search the library). Not for a one-off summary the owner only wants to read now (youtube-transcript alone). |
| [`datastore`](skills/datastore/SKILL.md) | Keep structured, queryable records in a git repository as a SQLite-backed dataset: append-only JSONL logs committed to git are the truth, and a local SQLite cache gives fast SQL. Use when data is many rows with the same fields that will be filtered, joined, deduplicated or trended over time ("track X over time", "store these as a table", "query my jobs/prices/workouts", a script that ingests records daily), or when a workflow needs durable machine state. Not for prose notes, one-off lists that fit in a Markdown table, or secrets. |

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
| [`write-a-brief`](skills/write-a-brief/SKILL.md) | Write or tighten a one-to-two-page meeting brief for a professional (contractor, consultant, doctor, vendor). Use for "meeting brief", "prep doc", "questions to ask", or fixing a brief that is too long or AI-sounding; not for email drafts or general notes. |
| [`review-a-quote`](skills/review-a-quote/SKILL.md) | Review and file a vendor or construction quotation, assess commercial terms and line items, and separate immediate asks from parked items. Use for "check/review this quote" or quote PDFs. |
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
| [`ux-design`](skills/ux-design/SKILL.md) | Audit or design the user experience of a web page or app: navigation, states, touch targets, focus, contrast, motion, responsive layout, copy in the interface. Runs a checklist pass against its bundled UX guidelines, then hands the visual direction to the frontend-design plugin skill. Use for "UX pass", "audit the UX", "does this page feel right", "make this usable on mobile", "accessibility check", or any new UI before it ships. Not for the aesthetic alone (frontend-design), charts (dataviz), diagrams (system-diagram), or adding a case-study page. |
| [`3d-design`](skills/3d-design/SKILL.md) | Choose and use a 3D design workflow for UI illustrations, modeled objects, character animation, interactive scenes and web delivery. Use for "3D design", "3D animation", "model this", "Blender or Three.js", "make the movement natural", "seamless loop", "continuous pan", or selecting and switching 3D tools. Covers authoring, runtime, export and visual verification; not ordinary page layout, 2D architecture diagrams or unrelated Blender installation troubleshooting. |
| [`blender-authoring`](skills/blender-authoring/SKILL.md) | Create, edit, animate, export and render Blender scenes using headless Python (bpy). Use after 3d-design selects Blender, or when the user explicitly requests Blender or a blend file. Covers geometry, materials, rigging, animation, lighting and export. Not for choosing between 3D tools, Three.js playback or ordinary page layout. |

Elsewhere:

- [tt-a1i/archify](https://github.com/tt-a1i/archify) — Turns a codebase or a description into interactive architecture and sequence diagrams as self-contained HTML.
- [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) — UI and UX guidance for agents building interfaces. Large; its 119-rule usability list is the useful part.
- [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) — Aesthetic judgment for generated frontends.

### Life

_Trips, shopping, property and learning._

| Skill | Does |
|---|---|
| [`trip-planner`](skills/trip-planner/SKILL.md) | Plan or replan trips using live research for routes, hours, parking, food, tolls, and pacing. Use for itineraries and on-the-road questions about stops, parking, or eating. |
| [`product-shopping`](skills/product-shopping/SKILL.md) | Recommend what product to buy, or find the best legitimate price for a chosen model in the buyer's own region. Use for comparisons, shortlists, "is X worth it", "which X should I get", cheapest price, deal checks, or price history; not for cross-country SG-vs-US comparisons in SGD (compare-price) or just listing which shops carry an item. |
| [`compare-price`](skills/compare-price/SKILL.md) | Compare what one product (or a tier spread of competing products) costs across Singapore, the US, and any other named country, reported in SGD with live FX and landed cost. Use for /compare-price, "where in the world is it cheapest", "SG vs US price", or "should I buy this overseas"; not for single-region deal hunting or picking which model to buy (product-shopping). |
| [`evaluate-condo`](skills/evaluate-condo/SKILL.md) | Evaluate a Singapore condo listing or development and file a cited Buy/Neutral/Avoid note. Use for PropertyGuru, 99.co, EdgeProp, "evaluate this condo", or "is this unit worth it". |
| [`teach`](skills/teach/SKILL.md) | Create a stateful, multi-session course in the learning workspace. Use only when the user invokes teach or asks to start structured learning of a topic. Explicit-only; not for one-off explanations or research reports. |

### Career

_Interview drilling and job-search practice._

| Skill | Does |
|---|---|
| [`interview-prep`](skills/interview-prep/SKILL.md) | Run interview practice grounded in the candidate's own resume and target-company notes: mock interviews, behavioral STAR answers, number defense, walkthroughs of systems they built, stakeholder simulations, reference system-design walkthroughs, timed DSA coding rounds and plan reps graded and scheduled by due pattern, and debriefs of real interviews that queue what broke. Use for "interview prep", "mock interview", "run a DSA rep", "give me a rep", "what's due", "walk me through a system design", "I just had an interview", "log my onsite"; not for editing a resume or cover letter, finding or applying to jobs, answering recruiters, or building a customer presentation. |

Elsewhere:

- [kirilxd/swe-interview-coach](https://github.com/kirilxd/swe-interview-coach) — Behavioural and system-design prep for Claude Code.

### Field engineering

_Customer-facing decks and pilot evidence for forward-deployed work._

| Skill | Does |
|---|---|
| [`create-fde-deck`](skills/create-fde-deck/SKILL.md) | Draft a customer-facing field-engineering deck from supplied evidence: a discovery narrative, a technical architecture walkthrough, or a pilot readout with a stop, extend or expand recommendation. Writes a Markdown slide deck (rendered to slides or HTML with whatever tool the host has) in which every claim is labelled evidence, assumption or proposal, held to slide-density limits and checked by a script. Use for "make a discovery deck", "turn these customer notes into slides", "architecture deck for the customer", "pilot readout slides", "POC results deck", "go/no-go deck"; not for critiquing a deck that already exists (review-fde-deck), keeping a pilot's criteria and evidence record (track-pilot-evidence), or interview practice. |
| [`review-fde-deck`](skills/review-fde-deck/SKILL.md) | Audit an existing customer-facing or field-engineering deck before it is shared: narrative logic, evidence quality, technical honesty, editorial density, accessibility and actionability, ranked into blockers, important fixes and polish with a slide-specific fix for each, then an optional revise-and-recheck loop. Works on a Markdown or HTML deck, a slide export or pasted slide text. Use for "review this deck", "check my slides before the customer meeting", "fact-check this pilot readout", "is this architecture deck honest", "pre-share deck QA"; not for drafting a new deck from notes (create-fde-deck), keeping a pilot's evidence record (track-pilot-evidence), or reviewing code, documents or emails that are not slides. |
| [`track-pilot-evidence`](skills/track-pilot-evidence/SKILL.md) | Keep a customer pilot or proof of concept's success record as plain files: charter, criteria with metric, baseline and threshold, evidence tied to criteria, risks, decisions and attachments verified by SHA-256, customer-visible versus internal flags, a coverage and freshness check, and a customer-safe handover. An agent may propose that a criterion is met, tied to the exact inputs it reviewed; only a person records a review or a proceed, hold or stop decision. Use for "set up success criteria for the pilot", "log this pilot evidence", "attach the benchmark results", "is the POC ready for the go/no-go", "prepare the customer handover"; not for building slides (create-fde-deck), reviewing a deck (review-fde-deck), or interview practice. |

### Skill building

_Making, testing and improving the skills themselves._

| Skill | Does |
|---|---|
| [`skillsmith`](skills/skillsmith/SKILL.md) | Make an agent skill grounded in the current repository, then prove it beats the same model without it: gate whether a skill is the right mechanism, inventory existing skills and conventions, draft and lint, run a blinded baseline-versus-skill evaluation, and keep or retire. Use whenever asked to add, create, write, revise, install, review, or prove a skill for Claude Code or Codex; not for typo-only edits, AGENTS.md rules, hooks, or prompts that do not change a skill. |
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
