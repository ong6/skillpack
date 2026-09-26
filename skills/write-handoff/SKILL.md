---
name: write-handoff
description: Compact the current conversation into a handoff document. Use when the user asks for a handoff, continuation brief, or context package for another session or agent.
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the session scratchpad directory if one is set, else the OS temp directory; never the workspace.

Include a "suggested skills" section in the document, which suggests skills that the agent should invoke.

Before saving, cut generic framing and recap, keep concrete state and next actions, and preserve
quoted facts, commands, paths, links, uncertainty, and owner-authored wording exactly.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
