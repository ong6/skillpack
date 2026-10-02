#!/usr/bin/env python3
"""Turn the `blender` MCP server on or off for the current project.

Usage: mcp_toggle.py on|off|status [--quiet]

If the project's `.mcp.json` defines `blender`, this flips it in `.claude/settings.local.json`
(gitignored), which Claude Code hot-reloads, so the server connects or disconnects in the running
session. Otherwise it adds or removes a local-scope server with `claude mcp add|remove -s local`
(stored in ~/.claude.json for this project path, never in the repo); run `/mcp` or start a new
session for the change to connect. Off by default: nothing registers it until you turn it on.
"""
import json
import os
import shutil
import subprocess
import sys

NAME = "blender"
SERVER = ["uvx", "--from", "git+https://projects.blender.org/lab/blender_mcp.git@dbbf836ad4b1025f14a2b3b504c43903f39e0b04#subdirectory=mcp",
          "blender-mcp"]


def root():
    d = os.environ.get("CLAUDE_PROJECT_DIR")
    if d:
        return d
    return subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                          text=True, check=True).stdout.strip()


def project_server(base):
    try:
        with open(os.path.join(base, ".mcp.json")) as fh:
            return NAME in json.load(fh).get("mcpServers", {})
    except (OSError, ValueError):
        return False


def toggle_project(base, mode):
    """Flip a `.mcp.json` server through the gitignored settings.local.json lists."""
    path = os.path.join(base, ".claude", "settings.local.json")
    s = json.load(open(path)) if os.path.exists(path) else {}
    on = s.setdefault("enabledMcpjsonServers", [])
    off = s.setdefault("disabledMcpjsonServers", [])
    if mode == "status":
        return "on" if NAME in on and NAME not in off else "off"
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
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(s, fh, indent=2)
            fh.write("\n")
    return mode


def toggle_local(base, mode):
    """Add or remove a local-scope server; the repo itself is never touched."""
    if not shutil.which("claude"):
        sys.exit("mcp_toggle: `claude` is not on PATH; install Claude Code or add the server by hand")
    run = lambda *a: subprocess.run(["claude", "mcp", *a], cwd=base, capture_output=True, text=True)
    present = run("get", NAME).returncode == 0
    if mode == "status":
        return "on" if present else "off"
    if mode == "on" and not present:
        r = run("add", "-s", "local", NAME, "--", *SERVER)
        if r.returncode:
            sys.exit("mcp_toggle: claude mcp add failed: " + (r.stderr or r.stdout).strip())
    if mode == "off" and present:
        run("remove", "-s", "local", NAME)
    return mode


def main():
    args = [a for a in sys.argv[1:] if a != "--quiet"]
    mode = args[0] if args else "status"
    if mode not in ("on", "off", "status"):
        sys.exit("usage: mcp_toggle.py on|off|status [--quiet]")
    base = root()
    state = toggle_project(base, mode) if project_server(base) else toggle_local(base, mode)
    if mode == "status" or "--quiet" not in sys.argv:
        print(f"{NAME} MCP: {state}")


if __name__ == "__main__":
    main()
