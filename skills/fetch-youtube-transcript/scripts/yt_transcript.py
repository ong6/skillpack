#!/usr/bin/env python3
"""Fetch a YouTube transcript as clean text.

Usage:
    yt_transcript.py <url|id> [lang] [--timestamps]

On first run it auto-creates a private venv next to this script and installs
`youtube-transcript-api` there (works around PEP 668 externally-managed Python),
then re-executes itself inside that venv. No manual setup needed.

Exit codes: 2 bad args | 3 dependency unavailable | 1 fetch failed
"""
import os
import re
import subprocess
import sys


def ensure_dep():
    """Import the lib; if missing, bootstrap a local venv and re-exec inside it."""
    try:
        import youtube_transcript_api  # noqa: F401
        return
    except ImportError:
        pass

    if os.environ.get("YT_BOOTSTRAPPED"):  # already re-exec'd once; give up cleanly
        print(
            "MISSING_DEP: auto-install did not provide youtube-transcript-api. "
            "Install manually: pip3 install --break-system-packages youtube-transcript-api",
            file=sys.stderr,
        )
        sys.exit(3)

    here = os.path.dirname(os.path.abspath(__file__))
    venv = os.path.join(here, ".venv")
    vpy = os.path.join(venv, "bin", "python3")
    try:
        if not os.path.exists(vpy):
            subprocess.run([sys.executable, "-m", "venv", venv], check=True)
        subprocess.run(
            [vpy, "-m", "pip", "install", "-q", "--disable-pip-version-check",
             "--upgrade", "youtube-transcript-api"],
            check=True,
            capture_output=True,
        )
    except Exception as e:  # noqa: BLE001
        print(
            f"MISSING_DEP: auto-install failed ({e}). "
            "Install manually: pip3 install --break-system-packages youtube-transcript-api",
            file=sys.stderr,
        )
        sys.exit(3)

    env = dict(os.environ, YT_BOOTSTRAPPED="1")
    os.execve(vpy, [vpy, os.path.abspath(__file__), *sys.argv[1:]], env)


def video_id(s):
    s = s.strip()
    if re.fullmatch(r"[0-9A-Za-z_-]{11}", s):
        return s
    m = re.search(r"(?:v=|/shorts/|/embed/|youtu\.be/)([0-9A-Za-z_-]{11})", s)
    if m:
        return m.group(1)
    m = re.search(r"([0-9A-Za-z_-]{11})", s)  # last-ditch
    return m.group(1) if m else None


def stamp(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"[{h:d}:{m:02d}:{s:02d}]" if h else f"[{m:d}:{s:02d}]"


def main():
    args = sys.argv[1:]
    show_ts = "--timestamps" in args
    args = [a for a in args if a != "--timestamps"]
    if not args:
        print("usage: yt_transcript.py <url|id> [lang] [--timestamps]", file=sys.stderr)
        sys.exit(2)

    vid = video_id(args[0])
    if not vid:
        print("could not parse a video id from input", file=sys.stderr)
        sys.exit(2)
    langs = [args[1]] if len(args) > 1 else ["en", "en-US", "en-GB"]

    ensure_dep()
    from youtube_transcript_api import YouTubeTranscriptApi

    rows = None
    # New API (>= 1.0): instance.fetch(...) -> iterable of snippet objects
    try:
        fetched = YouTubeTranscriptApi().fetch(vid, languages=langs)
        rows = [{"text": sn.text, "start": sn.start} for sn in fetched]
    except Exception:
        # Old API (< 1.0): static get_transcript -> list of dicts
        try:
            data = YouTubeTranscriptApi.get_transcript(vid, languages=langs)
            rows = [{"text": r["text"], "start": r["start"]} for r in data]
        except Exception as e:  # noqa: BLE001
            print(f"FETCH_FAILED: {e}", file=sys.stderr)
            sys.exit(1)

    out = []
    for r in rows:
        text = " ".join(r["text"].split())
        if not text:
            continue
        out.append(f"{stamp(r['start'])} {text}" if show_ts else text)

    if not out:
        print("FETCH_FAILED: transcript was empty", file=sys.stderr)
        sys.exit(1)
    print("\n".join(out) if show_ts else " ".join(out))


if __name__ == "__main__":
    main()
