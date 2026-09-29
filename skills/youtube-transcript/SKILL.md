---
name: youtube-transcript
description: Fetch clean transcripts or captions from YouTube URLs or video IDs. Use when the user shares a YouTube link or asks to transcribe, summarize, cite, or read a video.
---

# YouTube Transcript

Turn a YouTube link into readable text. Works for normal videos, Shorts, and
auto-generated captions.

## Quick start

Paths are relative to this skill's folder.

```bash
# fetch transcript as a single clean block (first run auto-installs into a private venv):
python3 scripts/yt_transcript.py "<url-or-id>"

# with timestamps (good for citing a moment), or a specific language:
python3 scripts/yt_transcript.py "<url>" --timestamps
python3 scripts/yt_transcript.py "<url>" es
```

No setup needed: on first run the script creates its own venv next to itself and
installs `youtube-transcript-api` (handles macOS/Homebrew PEP 668). It accepts full
URLs (`watch?v=`, `youtu.be/`, `/shorts/`, `/embed/`) or a bare 11-char ID, prints
plain text to stdout, and uses clear error codes: `MISSING_DEP` (auto-install failed;
the message gives the manual command) and `FETCH_FAILED` (try a fallback below).

## Fallbacks (in order)

1. **Primary:** the script above (`youtube-transcript-api`): fastest, clean text, no ffmpeg.
2. **`yt-dlp`**, when the API is IP-blocked or captions only exist as a downloadable track:
   ```bash
   command -v yt-dlp || brew install yt-dlp
   yt-dlp --skip-download --write-auto-subs --write-subs --sub-langs "en.*" \
          --sub-format vtt -o "%(id)s.%(ext)s" "<url>"
   ```
   Then read the `.vtt`, strip the timestamp/`WEBVTT` lines, and dedupe rolling caption lines.
3. **Browser automation** (last resort): open the watch page, click "Show transcript", read the panel. Fragile; only if 1 and 2 both fail.

## Rules
- If a video has **no captions at all**, say so; don't fabricate. (Audio-only transcription is out of scope here.)
- Long transcripts: summarize or extract the asked-for parts rather than dumping the whole wall of text, unless the user wants the full text.
- Note when captions are **auto-generated** (punctuation, names, and numbers are unreliable).
- When using a transcript as a research source, attribute it to the video (title + channel + URL).

## Response contract

Name the source that actually succeeded: YouTube captions API, `yt-dlp` subtitle track, or browser
transcript panel. If an earlier method failed, say which fallback supplied the text. For
auto-generated captions, label them before the summary or transcript and preserve uncertainty in
names, numbers, and quotations. If every caption method fails, return `No captions available` plus
the methods tried; never turn page descriptions, comments, or inferred speech into a transcript.
