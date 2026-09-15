---
name: handoff
description: Compact the current conversation into a handoff document. Use when the user asks for a handoff, continuation brief, or context package for another session or agent.
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the session scratchpad directory if one is set, else the OS temp directory; never the workspace.

Include a "suggested skills" section in the document, which suggests skills that the agent should invoke.

Run the document through [`unslop`](../unslop/SKILL.md) to ensure it reads clearly without AI tells.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
