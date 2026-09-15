---
name: web-extract
description: >-
  Read, scrape or search the web through Firecrawl (CLI or MCP): a URL the user shares, a page
  WebFetch returns empty or 403 on, a JavaScript or Cloudflare-walled site, a public PDF, or a
  live web search. Not for YouTube (youtube-transcript) or LinkedIn (the domain stays
  off-limits).
---

# Web Extract

Two surfaces, same account:

- **CLI** `firecrawl` (`npx firecrawl-cli`, then `firecrawl login`; the key lives in the CLI's own
  config, never in the repo). Prefer it from Bash.
- **MCP** server `firecrawl`, when the host project has one configured. Keep it local-scope so
  the key never travels with the repo.

**Credits.** The free tier is about 1,000 credits a cycle, 2 concurrent jobs; a scrape or a search
is a credit each. Check `firecrawl --status` before anything bulk, and never run `crawl`, `map`,
`agent` or `monitor` without the user asking. Native `WebFetch` and `WebSearch` cost nothing, so try them
first on plain pages and reach for Firecrawl when they come back thin, walled or blocked.

## Commands

```bash
firecrawl scrape "<url>" --only-main-content -o "$SCRATCHPAD/<name>.md"   # clean markdown
firecrawl scrape "<url>" -Q "<question>"                                   # answer from the page
firecrawl scrape "<url>" -f markdown,links --wait-for 5000                # JS-heavy page
firecrawl scrape "<url1>" "<url2>" -o "$SCRATCHPAD/"                       # batch, concurrent
firecrawl search "<query>" --limit 5                                       # web search
firecrawl parse ./file.pdf -o "$SCRATCHPAD/file.md"                        # local document
firecrawl interact "<what to do on the page>"                              # clicks, forms
firecrawl doctor <job-id>                                                  # a job failed
```

Public PDFs go through `scrape`, local ones through `parse`. Use `interact` only when the
content needs a click or a form; it costs more and is slower. Always write output to the
scratchpad with `-o`, never into the repo (gitignore `.firecrawl/`).

## Rules

- **Off-limits stays off-limits.** `linkedin.com` and `reddit.com` publish `Disallow: /`. Do not
  scrape them; Reddit goes through its API.
- **Report what came back.** A login shell, an interstitial or an empty render is a failure, not
  content. Say so and try Wayback (`https://web.archive.org/web/<url>`, note the snapshot date)
  or an official API or sitemap before anything else.
- **CAPTCHAs and hard paywalls go to the human.** Never solve or route around them.
- **Modest volume.** A personal reader, not a crawler. One warm session for a batch, not a loop.
- **Cite the source URL** in whatever the extraction feeds.

Keep per-site findings (which hosts need `--wait-for`, which publish JSON-LD) in a note in the host
project, not here.
