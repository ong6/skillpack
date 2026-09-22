# Upstream

Source: https://github.com/MartinRapcan/blender-claude-skill
Commit: `964cfe73bb1d15ff5b1603c625ecf067fb8d11bc`
License: MIT; see LICENSE.

Local changes: renamed skill to blender-authoring, narrowed its trigger to Blender-selected work,
and connected it to the shared 3d-design decision and animation review. No upstream scripts
were executed during installation.

Patched the animation reference to iterate layered action channel bags on Blender 4.4+/5, with a legacy F-curve fallback. The tennis generator uses the layered form; the complete upstream reference collection has not been runtime-tested.

Added `scripts/mcp_toggle.py` and the Live Blender section: switches a project's official Blender MCP server on for live-scene work and off otherwise.
