#!/usr/bin/env python3
"""Turn the project's `blender` MCP server on or off for this machine.

Edits .claude/settings.local.json (gitignored); Claude Code hot-reloads it, so the
server connects or disconnects in the running session. Usage: mcp_toggle.py on|off|status
"""
import json, os, subprocess, sys

NAME = "blender"

def root():
    d = os.environ.get("CLAUDE_PROJECT_DIR")
    if d:
        return d
    return subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                          text=True, check=True).stdout.strip()

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "status"
    base = root()
    if not os.path.exists(os.path.join(base, ".mcp.json")):
        return
    path = os.path.join(base, ".claude", "settings.local.json")
    s = json.load(open(path)) if os.path.exists(path) else {}
    on = s.setdefault("enabledMcpjsonServers", [])
    off = s.setdefault("disabledMcpjsonServers", [])
    if mode == "status":
        print(f"{NAME} MCP: {'on' if NAME in on and NAME not in off else 'off'}")
        return
    if mode not in ("on", "off"):
        sys.exit("usage: mcp_toggle.py on|off|status")
    add, remove = (on, off) if mode == "on" else (off, on)
    changed = NAME not in add or NAME in remove
    if NAME not in add:
        add.append(NAME)
    while NAME in remove:
        remove.remove(NAME)
    for k in ("enabledMcpjsonServers", "disabledMcpjsonServers"):
        if not s[k]:
            del s[k]
    if changed:
        with open(path, "w") as fh:
            json.dump(s, fh, indent=2)
            fh.write("\n")
    if "--quiet" not in sys.argv:
        print(f"{NAME} MCP: {mode}")

if __name__ == "__main__":
    main()
