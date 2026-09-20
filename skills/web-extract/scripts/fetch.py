#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx", "readabilipy", "markdownify", "protego"]
# ///
"""Standalone port of the reference Fetch MCP server (modelcontextprotocol/servers, src/fetch).

Same behaviour, no MCP process: fetch a URL, honour robots.txt, strip the page to its readable
content with readability, convert to markdown, and page through it with --start-index.
Fallback for when Firecrawl is down or the credits are gone.

Usage:
  fetch.py <url> [--raw] [--max-length N] [--start-index N] [--ignore-robots] [--manual]

Exit codes: 0 content · 1 robots.txt refused · 2 fetch or parse error.
"""
import argparse
import sys
from urllib.parse import urlparse, urlunparse

import httpx
import markdownify
import readabilipy.simple_json
from protego import Protego

UA_AUTONOMOUS = "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)"
UA_MANUAL = "ModelContextProtocol/1.0 (User-Specified; +https://github.com/modelcontextprotocol/servers)"
BLOCKED_HOSTS = {"linkedin.com", "reddit.com"}


def html_to_markdown(html: str) -> str:
    ret = readabilipy.simple_json.simple_json_from_html_string(html, use_readability=True)
    if not ret["content"]:
        return "<error>Page failed to be simplified from HTML</error>"
    return markdownify.markdownify(ret["content"], heading_style=markdownify.ATX)


def robots_url(url: str) -> str:
    p = urlparse(url)
    return urlunparse((p.scheme, p.netloc, "/robots.txt", "", "", ""))


def blocked_host(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    return any(host == blocked or host.endswith(f".{blocked}") for blocked in BLOCKED_HOSTS)


def robots_allows(client: httpx.Client, url: str, ua: str) -> tuple[bool, str]:
    r_url = robots_url(url)
    try:
        r = client.get(r_url, follow_redirects=True, headers={"User-Agent": ua})
    except httpx.HTTPError:
        return False, f"could not fetch {r_url} (connection issue)"
    if r.status_code in (401, 403):
        return False, f"{r_url} returned {r.status_code}; treating autonomous fetching as not allowed"
    if 400 <= r.status_code < 500:
        return True, ""
    body = "\n".join(l for l in r.text.splitlines() if not l.strip().startswith("#"))
    if Protego.parse(body).can_fetch(url, ua):
        return True, ""
    return False, f"{r_url} disallows autonomous fetching of this page for {ua}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--raw", action="store_true", help="skip readability + markdown, print raw body")
    ap.add_argument("--max-length", type=int, default=5000)
    ap.add_argument("--start-index", type=int, default=0)
    ap.add_argument("--ignore-robots", action="store_true", help="user asked for this exact page; never overrides blocked hosts")
    ap.add_argument("--manual", action="store_true", help="use the user-specified user agent")
    ap.add_argument("--proxy", default=None)
    a = ap.parse_args()
    if blocked_host(a.url):
        print("VERDICT: blocked\nHINT: LinkedIn and Reddit are off-limits even for manual requests or --ignore-robots.", file=sys.stderr)
        return 1
    ua = UA_MANUAL if (a.manual or a.ignore_robots) else UA_AUTONOMOUS

    with httpx.Client(proxy=a.proxy, timeout=30) as client:
        if not a.ignore_robots:
            ok, why = robots_allows(client, a.url, ua)
            if not ok:
                print(f"VERDICT: blocked\nHINT: {why}. Re-run with --ignore-robots only if the owner asked for this exact page.", file=sys.stderr)
                return 1
        try:
            r = client.get(a.url, follow_redirects=True, headers={"User-Agent": ua})
        except httpx.HTTPError as e:
            print(f"VERDICT: error\nHINT: failed to fetch {a.url}: {e!r}", file=sys.stderr)
            return 2
        if r.status_code >= 400:
            print(f"VERDICT: error\nHINT: {a.url} returned status {r.status_code}", file=sys.stderr)
            return 2

    raw = r.text
    ctype = r.headers.get("content-type", "")
    is_html = "<html" in raw[:100].lower() or "text/html" in ctype or not ctype
    prefix = ""
    if is_html and not a.raw:
        content = html_to_markdown(raw)
    else:
        content = raw
        prefix = f"Content type {ctype} cannot be simplified to markdown, raw content follows.\n"

    total = len(content)
    if a.start_index >= total:
        body = "<error>No more content available.</error>"
    else:
        body = content[a.start_index : a.start_index + a.max_length]
        if not body:
            body = "<error>No more content available.</error>"
        elif len(body) == a.max_length and a.start_index + a.max_length < total:
            body += f"\n\n<error>Content truncated. Call again with --start-index {a.start_index + a.max_length} to get more.</error>"

    final = f"\nFINAL_URL: {r.url}" if str(r.url) != a.url else ""
    print(f"VERDICT: ok\nURL: {a.url}{final}\nHTTP: {r.status_code}\nCHARS: {total}\n----- CONTENT -----\n{prefix}{body}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
