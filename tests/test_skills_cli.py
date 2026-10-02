#!/usr/bin/env python3
"""Tests for bin/skills: stdlib unittest, Python 3.7+. Run: python3 tests/test_skills_cli.py

Every test builds its own temp HOME, checkouts, bare git remotes and a fake `claude` on PATH.
Fixture strings that look like personal data are assembled at runtime so this file stays
clean under `bin/skills guard`.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import datetime
import importlib.machinery
import importlib.util
import re
import tempfile
import time
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(REPO, "bin", "skills")
AT = "@"
EMAIL = "jane.doe" + AT + "gm" + "ail.com"
HOME_PATH = "/" + "Users/janedoe/notes"
NRIC = "S" + "1234567" + "D"
PRIVATE_KEY = "-----BEGIN " + "OPENSSH PRIVATE KEY-----"
TOKEN = "gh" + "p_" + "A1b2" * 9
PHONE = "+65 " + "91" + "23 4567"
SIDEPROJECT = "~/" + "Sideproject/notes"
FACTS = {"os": "TestOS", "model": "TestModel", "hostname": "testhost-01", "user": "tester", "wsl": False}
PUBLIC_SKILLS = {"web-extract": "research", "youtube-transcript": "research", "handoff": "writing",
                 "system-diagram": "design", "feedback-loop": "skill-building"}
PRIVATE_SKILLS = {"cv": "career", "handoff": "writing", "where-to-shop": "life"}

FAKE_CLAUDE = '''#!{python}
import json, os, sys
args = sys.argv[1:]
with open(os.environ["FAKE_CLAUDE_LOG"], "a") as fh:
    fh.write(json.dumps({{"args": args, "cwd": os.getcwd()}}) + "\\n")
if "-p" in args or "--print" in args:
    sys.exit(97)
path = os.path.join(os.environ["HOME"], ".claude.json")
try:
    with open(path) as fh:
        cfg = json.load(fh)
except Exception:
    cfg = {{}}
servers = cfg.setdefault("projects", {{}}).setdefault(os.getcwd(), {{}}).setdefault("mcpServers", {{}})
if args[:2] == ["mcp", "get"]:
    sys.exit(0 if args[2] in servers or args[2] in cfg.get("mcpServers", {{}}) else 1)
if args[:2] == ["mcp", "add"]:
    rest = args[2:]
    head, cmd = rest[:rest.index("--")], rest[rest.index("--") + 1:]
    env, name, i = {{}}, None, 0
    while i < len(head):
        if head[i] in ("-s", "--scope"):
            i += 2
        elif head[i] in ("-e", "--env"):
            key, value = head[i + 1].split("=", 1)
            env[key] = value
            i += 2
        else:
            name = head[i]
            i += 1
    servers[name] = {{"type": "stdio", "command": cmd[0], "args": cmd[1:], "env": env}}
    with open(path, "w") as fh:
        json.dump(cfg, fh)
    sys.exit(0)
sys.exit(2)
'''

FAKE_LINTER = '''import sys
text = open(sys.argv[1] + "/SKILL.md").read()
if "LINT-FAIL" in text:
    sys.stderr.write("error: bad skill\\n")
    sys.exit(1)
print("lint passed")
'''


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


class Sandbox(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp(prefix="skills-cli-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.home = os.path.join(self.tmp, "home")
        self.root = os.path.join(self.home, "Sideproject")
        self.public = os.path.join(self.root, "skills")
        self.private = os.path.join(self.root, "skills-private")
        self.store = os.path.join(self.tmp, "store")
        self.fakebin = os.path.join(self.tmp, "fakebin")
        self.machines = os.path.join(self.tmp, "machines.json")
        self.claude_log = os.path.join(self.tmp, "claude.log")
        for d in (self.home, self.root, self.store, self.fakebin):
            os.makedirs(d, exist_ok=True)
        env = dict(os.environ)
        for key in ("CLAUDE_CONFIG_DIR", "SKILLS_ROOT", "HOST_REPO", "SKILLS_PUBLIC_URL",
                    "SKILLS_PRIVATE_URL", "SKILLS_FETCH_INTERVAL", "GIT_DIR", "GIT_WORK_TREE"):
            env.pop(key, None)
        env.update({
            "HOME": self.home, "XDG_CONFIG_HOME": os.path.join(self.home, ".config"),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.com",
            "SKILLS_NO_FETCH": "1", "SKILLS_FACTS": json.dumps(FACTS),
            "PATH": self.fakebin + os.pathsep + env.get("PATH", ""), "FAKE_CLAUDE_LOG": self.claude_log,
        })
        self.env = env
        write(os.path.join(self.fakebin, "claude"), FAKE_CLAUDE.format(python=sys.executable))
        os.chmod(os.path.join(self.fakebin, "claude"), 0o755)
        self.git(self.store, "init", "-q")
        self.make_checkout(self.public, PUBLIC_SKILLS)
        write(os.path.join(self.public, "skills", "notes-only", "README.md"), "Not a skill.\n")
        self.git(self.public, "add", "-A")
        self.git(self.public, "commit", "-q", "-m", "notes")
        self.make_checkout(self.private, PRIVATE_SKILLS, block=True)
        self.write_machines(None)

    # helpers -------------------------------------------------------------------------------

    def git(self, cwd, *args):
        r = subprocess.run(["git"] + list(args), cwd=cwd, env=self.env, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, universal_newlines=True)
        if r.returncode != 0:
            raise AssertionError("git {} failed: {}".format(" ".join(args), r.stderr))
        return r.stdout.strip()

    def make_checkout(self, path, skills, block=False):
        lines = ["skill_summaries:"] + ["  {}: Summary.".format(n) for n in sorted(skills)]
        lines.append("categories:")
        for cat in sorted(set(skills.values())):
            names = sorted(n for n, c in skills.items() if c == cat)
            lines += ["  - key: {}".format(cat), "    title: {}".format(cat.title()), "    blurb: Blurb."]
            if block:
                lines += ["    skills:"] + ["      - {}".format(n) for n in names]
            else:
                lines.append("    skills: [{}]".format(", ".join(names)))
            lines += ["    links:", "      - repo: someone/thing", "        note: Elsewhere."]
        write(os.path.join(path, "catalog.yaml"), "\n".join(lines) + "\n")
        for name in skills:
            self.add_skill(path, name)
        self.git(path, "init", "-q")
        self.git(path, "symbolic-ref", "HEAD", "refs/heads/main")
        self.git(path, "add", "-A")
        self.git(path, "commit", "-q", "-m", "seed")

    def add_skill(self, checkout, name, body="Body.\n"):
        write(os.path.join(checkout, "skills", name, "SKILL.md"),
              "---\nname: {}\ndescription: Does {}.\n---\n{}".format(name, name, body))

    def make_remote(self, checkout, name):
        bare = os.path.join(self.tmp, "remotes", name + ".git")
        os.makedirs(bare)
        self.git(bare, "init", "-q", "--bare")
        self.git(bare, "symbolic-ref", "HEAD", "refs/heads/main")
        self.git(checkout, "remote", "add", "origin", bare)
        self.git(checkout, "push", "-q", "-u", "origin", "main")
        return bare

    def write_machines(self, skills, match=None, name="Test box"):
        """skills=None writes a registry that matches no machine (the unmatched default)."""
        registry = {"machines": [{"match": {"os": "TestOS", "model": "Other"}, "name": "Other box",
                                  "skills": {"scope": "user"}}]}
        if skills is not None:
            registry["machines"].append({"match": match or {"os": "TestOS", "model": "TestModel"},
                                         "name": name, "skills": skills})
        write(self.machines, json.dumps(registry))

    def cli(self, *args, **kw):
        env = dict(self.env)
        env.update(kw.get("env") or {})
        return subprocess.run([sys.executable, CLI] + list(args), cwd=kw.get("cwd", self.tmp), env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
                              timeout=120)

    def up(self, *extra, **kw):
        return self.cli("up", "--repo", self.store, "--machines", self.machines, *extra, **kw)

    def links(self, d):
        if not os.path.isdir(d):
            return {}
        return {n: os.readlink(os.path.join(d, n)) for n in sorted(os.listdir(d))
                if os.path.islink(os.path.join(d, n))}

    def store_links(self, sub=".claude/skills"):
        return self.links(os.path.join(self.store, sub))

    def target(self, checkout, name):
        return os.path.join(checkout, "skills", name)

    def claude_calls(self):
        if not os.path.exists(self.claude_log):
            return []
        with open(self.claude_log) as fh:
            return [json.loads(line) for line in fh if line.strip()]


class ProfileTests(Sandbox):
    def test_unmatched_profile_links_public_into_the_repo_only(self):
        r = self.up()
        self.assertEqual(r.returncode, 0, r.stderr)
        expected = {n: self.target(self.public, n) for n in PUBLIC_SKILLS}
        self.assertEqual(self.store_links(), expected)
        self.assertEqual(self.store_links(".agents/skills"), expected)
        self.assertNotIn("notes-only", self.store_links())
        self.assertEqual(self.links(os.path.join(self.home, ".claude/skills")), {})
        self.assertIn("5 linked (unregistered machine, project)", r.stdout)
        missing = self.cli("up", "--repo", self.store, "--machines", os.path.join(self.tmp, "absent.json"))
        self.assertEqual(missing.returncode, 0)
        self.assertIn("unregistered machine", missing.stdout)

    def test_project_scope_with_private_links_every_repo_and_private_wins(self):
        other = os.path.join(self.tmp, "other")
        os.makedirs(other)
        self.git(other, "init", "-q")
        self.write_machines({"scope": "project", "root": self.root, "private": True, "repos": [other]})
        r = self.up()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(Test box, project)", r.stdout)
        self.assertIn("private overrides public: handoff", r.stdout)
        for repo in (self.store, other):
            for sub in (".claude/skills", ".agents/skills"):
                got = self.links(os.path.join(repo, sub))
                self.assertEqual(got["handoff"], self.target(self.private, "handoff"))
                self.assertEqual(got["cv"], self.target(self.private, "cv"))
                self.assertEqual(got["web-extract"], self.target(self.public, "web-extract"))
        with open(os.path.join(other, ".git", "info", "exclude")) as fh:
            self.assertIn("/.claude/skills/cv", fh.read())
        self.assertNotIn(".claude", self.git(other, "status", "--porcelain"))
        self.assertNotIn(".agents", self.git(other, "status", "--porcelain"))
        unlinked = self.cli("unlink", "--repo", self.store, "--machines", self.machines)
        self.assertEqual(unlinked.returncode, 0, unlinked.stderr)
        self.assertEqual(self.links(os.path.join(other, ".claude/skills")), {})
        with open(os.path.join(other, ".git", "info", "exclude")) as fh:
            self.assertNotIn("skills links", fh.read())

    def test_user_scope_links_home_and_clears_project_links(self):
        self.up()
        self.assertTrue(self.store_links())
        self.write_machines({"scope": "user", "root": self.root})
        r = self.up()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(Test box, user)", r.stdout)
        expected = {n: self.target(self.public, n) for n in PUBLIC_SKILLS}
        self.assertEqual(self.links(os.path.join(self.home, ".claude/skills")), expected)
        self.assertEqual(self.links(os.path.join(self.home, ".agents/skills")), expected)
        self.assertEqual(self.store_links(), {})

    def test_machine_matching_uses_first_rule_hostname_prefix_and_user(self):
        registry = {"machines": [
            {"match": {"user": "agent"}, "name": "Agent box", "skills": {"scope": "user"}},
            {"match": {"os": "TestOS", "hostname": "testhost"}, "name": "Prefix box",
             "skills": {"scope": "project", "root": self.root}},
            {"match": {"os": "TestOS"}, "name": "Later box", "skills": {"scope": "user"}},
        ]}
        write(self.machines, json.dumps(registry))
        report = json.loads(self.cli("doctor", "--json", "--repo", self.store, "--machines", self.machines).stdout)
        self.assertEqual(report["machine"], "Prefix box")
        as_agent = dict(FACTS, user="agent")
        r = self.cli("doctor", "--json", "--repo", self.store, "--machines", self.machines,
                     env={"SKILLS_FACTS": json.dumps(as_agent)})
        self.assertEqual(json.loads(r.stdout)["machine"], "Agent box")

    def test_enable_and_disable_by_category(self):
        self.write_machines({"root": self.root, "private": True,
                             "enable": ["category:research", "handoff"], "disable": ["youtube-transcript"]})
        self.up()
        self.assertEqual(sorted(self.store_links()), ["handoff", "web-extract"])
        self.write_machines({"root": self.root, "private": True, "enable": ["*"],
                             "disable": ["category:design", "category:career", "category:nope"]})
        r = self.up()
        self.assertEqual(sorted(self.store_links()),
                         ["feedback-loop", "handoff", "web-extract", "where-to-shop", "youtube-transcript"])
        self.assertIn("3 added, 0 removed", r.stdout)
        doctor = self.cli("doctor", "--repo", self.store, "--machines", self.machines)
        self.assertIn("matches nothing: category:nope", doctor.stdout)


class LinkSafetyTests(Sandbox):
    def test_stale_and_dangling_links_into_our_checkouts_are_removed(self):
        self.up()
        d = os.path.join(self.store, ".claude/skills")
        os.symlink(self.target(self.public, "ghost"), os.path.join(d, "ghost"))
        os.symlink(os.path.relpath(self.target(self.public, "web-extract"), d), os.path.join(d, "old-name"))
        self.write_machines({"root": self.root, "disable": ["handoff"]})
        r = self.up("--hook", "claude")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(sorted(self.store_links()),
                         ["feedback-loop", "system-diagram", "web-extract", "youtube-transcript"])
        payload = json.loads(r.stdout)
        self.assertTrue(payload["hookSpecificOutput"]["reloadSkills"])

    def test_foreign_entries_are_never_touched(self):
        d = os.path.join(self.store, ".claude/skills")
        elsewhere = os.path.join(self.tmp, "elsewhere", "web-extract")
        write(os.path.join(elsewhere, "SKILL.md"), "foreign\n")
        write(os.path.join(d, "handoff", "SKILL.md"), "real dir\n")
        write(os.path.join(d, "notes.txt"), "a file\n")
        os.symlink(elsewhere, os.path.join(d, "web-extract"))
        os.symlink(os.path.join(self.tmp, "nowhere"), os.path.join(d, "zombie"))
        r = self.up()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("2 conflict(s)", r.stdout)
        with open(os.path.join(d, "handoff", "SKILL.md")) as fh:
            self.assertEqual(fh.read(), "real dir\n")
        self.assertEqual(os.readlink(os.path.join(d, "web-extract")), elsewhere)
        self.assertEqual(os.readlink(os.path.join(d, "zombie")), os.path.join(self.tmp, "nowhere"))
        self.assertTrue(os.path.isfile(os.path.join(d, "notes.txt")))
        self.assertEqual(os.readlink(os.path.join(d, "feedback-loop")),
                         self.target(self.public, "feedback-loop"))
        self.assertEqual(self.cli("link", "--repo", self.store, "--machines", self.machines).returncode, 1)
        doctor = self.cli("doctor", "--repo", self.store, "--machines", self.machines)
        self.assertEqual(doctor.returncode, 1)
        self.assertIn("not ours", doctor.stdout)
        self.assertIn("foreign dangling", doctor.stdout)
        self.cli("unlink", "--repo", self.store, "--machines", self.machines)
        self.assertEqual(os.readlink(os.path.join(d, "web-extract")), elsewhere)
        self.assertTrue(os.path.islink(os.path.join(d, "zombie")))

    def test_scope_guard_removes_only_our_links_from_home(self):
        claude_home = os.path.join(self.home, ".claude/skills")
        agents_home = os.path.join(self.home, ".agents/skills")
        company = os.path.join(self.tmp, "company", "skill")
        os.makedirs(company)
        write(os.path.join(claude_home, "synced", "x.md"), "claude.ai sync\n")
        os.symlink(self.target(self.public, "handoff"), os.path.join(claude_home, "handoff"))
        os.symlink(company, os.path.join(claude_home, "company-skill"))
        os.makedirs(agents_home)
        os.symlink(self.target(self.private, "cv"), os.path.join(agents_home, "cv"))
        r = self.up()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.links(claude_home), {"company-skill": company})
        self.assertTrue(os.path.isdir(os.path.join(claude_home, "synced")))
        self.assertEqual(self.links(agents_home), {})

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root ignores directory modes")
    def test_scope_guard_skips_a_read_only_home_dir_quietly(self):
        claude_home = os.path.join(self.home, ".claude/skills")
        os.makedirs(claude_home)
        os.symlink(self.target(self.public, "handoff"), os.path.join(claude_home, "handoff"))
        os.chmod(claude_home, 0o555)
        self.addCleanup(os.chmod, claude_home, 0o755)
        r = self.up()
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stderr, "")
        self.assertNotIn("not writable", r.stdout)
        self.assertTrue(os.path.islink(os.path.join(claude_home, "handoff")))
        doctor = self.cli("doctor", "--repo", self.store, "--machines", self.machines)
        self.assertIn("holds our links: handoff", doctor.stdout)


class UpTests(Sandbox):
    def test_up_is_quiet_and_fast_when_nothing_changed(self):
        first = self.up("--hook", "claude")
        payload = json.loads(first.stdout)["hookSpecificOutput"]
        self.assertEqual(payload["hookEventName"], "SessionStart")
        self.assertTrue(payload["reloadSkills"])
        self.assertTrue(payload["additionalContext"].startswith("skills: 5 linked"))
        start = time.time()
        second = self.up("--hook", "claude")
        elapsed = time.time() - start
        self.assertEqual(second.returncode, 0)
        self.assertEqual(second.stderr, "")
        self.assertEqual(len(second.stdout.splitlines()), 1)
        self.assertTrue(second.stdout.startswith("skills: 5 linked (unregistered machine, project)"))
        self.assertNotIn("reloadSkills", second.stdout)
        self.assertLess(elapsed, 1.0)
        codex = self.up("--hook", "codex")
        self.assertTrue(codex.stdout.startswith("skills: "))

    def test_up_always_exits_zero(self):
        write(self.machines, "{not json")
        self.assertEqual(self.up().returncode, 0)
        shutil.rmtree(self.root)
        r = self.up()
        self.assertEqual(r.returncode, 0)
        self.assertIn("0 linked", r.stdout)

    def test_background_fetch_never_blocks_up(self):
        self.make_remote(self.public, "skills")
        env = {"SKILLS_NO_FETCH": ""}
        start = time.time()
        r = self.up(env=env)
        self.assertLess(time.time() - start, 1.0)
        self.assertEqual(r.returncode, 0, r.stderr)
        stamp = os.path.join(self.home, ".cache", "skills", "fetched")
        deadline = time.time() + 20
        while not os.path.exists(stamp) and time.time() < deadline:
            time.sleep(0.1)
        self.assertTrue(os.path.exists(stamp), "background fetch did not finish")
        self.assertIn("fetched just now", self.up(env=env).stdout)

    def test_wait_clones_missing_checkouts_and_fast_forwards_clean_ones(self):
        public_bare = self.make_remote(self.public, "skills")
        private_bare = self.make_remote(self.private, "skills-private")
        shutil.rmtree(self.public)
        shutil.rmtree(self.private)
        self.write_machines({"root": self.root, "private": True})
        env = {"SKILLS_PUBLIC_URL": public_bare, "SKILLS_PRIVATE_URL": private_bare}
        r = self.up("--wait", env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("cv", self.store_links())
        self.assertIn("web-extract", self.store_links())
        for bare, name in ((public_bare, "new-public"), (private_bare, "new-private")):
            work = os.path.join(self.tmp, "work-" + name)
            self.git(self.tmp, "clone", "-q", bare, work)
            self.add_skill(work, name)
            self.git(work, "add", "-A")
            self.git(work, "commit", "-q", "-m", "add " + name)
            self.git(work, "push", "-q", "origin", "HEAD:main")
        write(os.path.join(self.private, "scratch.txt"), "uncommitted\n")
        private_head = self.git(self.private, "rev-parse", "HEAD")
        r = self.up("--wait", env=env)
        self.assertIn("new-public", self.store_links())
        self.assertNotIn("new-private", self.store_links())
        self.assertEqual(self.git(self.private, "rev-parse", "HEAD"), private_head)

    def test_private_checkout_is_not_cloned_when_profile_says_public_only(self):
        private_bare = self.make_remote(self.private, "skills-private")
        shutil.rmtree(self.private)
        r = self.up("--wait", env={"SKILLS_PRIVATE_URL": private_bare})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(self.private))


class McpTests(Sandbox):
    def test_mcp_registration_is_idempotent_and_never_launches_a_model(self):
        write(os.path.join(self.private, "mcp", "servers.json"), json.dumps({
            "demo": {"command": "{store}/bin/server", "args": ["--root", "{store}"],
                     "env": {"DEMO_HOME": "{store}/data"}},
            "unused": {"command": "true"},
        }))
        self.write_machines({"root": self.root, "private": True, "mcp": ["demo", "undefined-one"]})
        first = self.up()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("mcp added: demo", first.stdout)
        calls = self.claude_calls()
        self.assertEqual([c["args"][:2] for c in calls], [["mcp", "get"], ["mcp", "add"]])
        self.assertEqual(calls[1]["args"], ["mcp", "add", "-s", "local", "demo", "-e",
                                            "DEMO_HOME={}/data".format(self.store), "--",
                                            "{}/bin/server".format(self.store), "--root", self.store])
        self.assertEqual(calls[1]["cwd"], self.store)
        with open(os.path.join(self.home, ".claude.json")) as fh:
            self.assertIn("demo", json.load(fh)["projects"][self.store]["mcpServers"])
        second = self.up()
        self.assertNotIn("mcp added", second.stdout)
        self.assertEqual(len(self.claude_calls()), 2)
        for call in self.claude_calls():
            self.assertNotIn("-p", call["args"])
            self.assertNotIn("--print", call["args"])
        doctor = self.cli("doctor", "--repo", self.store, "--machines", self.machines)
        self.assertIn("mcp undefined-one is not defined", doctor.stdout)

    def test_existing_user_scope_server_is_not_duplicated(self):
        write(os.path.join(self.private, "mcp", "servers.json"), json.dumps({"demo": {"command": "x"}}))
        write(os.path.join(self.home, ".claude.json"), json.dumps({"mcpServers": {"demo": {"command": "x"}}}))
        self.write_machines({"root": self.root, "private": True, "mcp": ["demo"]})
        self.up()
        self.assertEqual(self.claude_calls(), [])


class GuardTests(Sandbox):
    def guard(self, *paths, **kw):
        return self.cli("guard", *paths, **kw)

    def test_builtin_patterns_terms_and_allow_markers(self):
        d = os.path.join(self.tmp, "scan")
        risky = [EMAIL, HOME_PATH, NRIC, PRIVATE_KEY, TOKEN, PHONE, SIDEPROJECT, "C:\\" + "Users\\janedoe\\x",
                 "/mnt/c/" + "Users/janedoe/x"]
        write(os.path.join(d, "a.md"), "\n".join("line " + x for x in risky) + "\n")
        write(os.path.join(d, "b.md"), "\n".join(x + " <!-- public-guard: allow -->" for x in risky) + "\n")
        write(os.path.join(d, "fine.md"), "See /Users/you/x, /home/user/y, version 1.2.3, 2026-10-02.\n")
        write(os.path.join(self.private, "guard-terms.txt"), "# owner terms\nsecret-?codename\n")
        write(os.path.join(d, "c.md"), "The Secret-Codename project.\n")
        write(os.path.join(d, "LICENSE"), "Copyright Secret Codename\n")
        write(os.path.join(d, ".claude-plugin", "plugin.json"), '{"author": "secretcodename"}\n')
        write(os.path.join(d, "skills", "x", "SKILL.md"), "---\nname: x\n---\n")
        write(os.path.join(d, "skills", "x", "LICENSE"), "Copyright secretcodename\n")
        r = self.guard(d)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        hits = set(tuple(line.rsplit(": ", 1)) for line in r.stdout.splitlines())
        names = [h[1] for h in hits if h[0].startswith(os.path.join(d, "a.md"))]
        for name in ("personal-email", "home-path", "sg-nric", "private-key", "token", "phone",
                     "sideproject-path"):
            self.assertIn(name, names)
        self.assertEqual(len([n for n in names if n == "home-path"]), 3)
        self.assertNotIn("b.md", r.stdout)
        self.assertNotIn("fine.md", r.stdout)
        self.assertIn((os.path.join(d, "c.md") + ":1", "guard-terms:2"), hits)
        self.assertIn((os.path.join(d, "skills", "x", "LICENSE") + ":1", "guard-terms:2"), hits)
        self.assertNotIn(os.path.join(d, "LICENSE:"), r.stdout)
        self.assertNotIn("plugin.json", r.stdout)
        self.assertNotIn("codename", (r.stdout + r.stderr).lower())
        clean = os.path.join(self.tmp, "clean")
        write(os.path.join(clean, "ok.md"), "Nothing to see.\n")
        self.assertEqual(self.guard(clean).returncode, 0)

    def test_ai_cli_launches_in_code_are_flagged_but_prohibitions_are_not(self):
        d = os.path.join(self.tmp, "launch")
        skill = os.path.join(d, "skills", "demo")
        write(os.path.join(skill, "SKILL.md"), "\n".join([
            "---", "name: demo", "---",
            "Never run `claude -p` from a skill.",
            "Do not delegate with",
            "`codex exec` either.",
            "Delegate with `codex exec \"task\"`.",
        ]) + "\n")
        write(os.path.join(skill, "scripts", "run.py"), "\n".join([
            "import subprocess",
            "from subprocess import Popen as P",
            "# never call claude -p here",
            "HELP = 'claude -p is forbidden'",
            "subprocess.run(['claude', '-p', 'hi'])",
            "P(['codex', 'exec', 'go'])",
            "subprocess.run(['claude', 'mcp', 'get', 'x'])",
        ]) + "\n")
        write(os.path.join(skill, "scripts", "go.sh"), "\n".join([
            "#!/bin/sh", "# do not run claude -p here", "codex exec \"$TASK\"",
            "claude -p x  # public-guard: allow",
        ]) + "\n")
        write(os.path.join(skill, "scripts", "same.sh"), "#!/bin/sh\n# harness: codex\ncodex exec go\n")
        r = self.guard(d)
        self.assertEqual(r.returncode, 2)
        rel = lambda *p: os.path.join(skill, *p)  # noqa: E731
        hits = set(line for line in r.stdout.splitlines())
        self.assertEqual(hits, {
            rel("SKILL.md") + ":7: ai-cli-launch:codex",
            rel("scripts", "go.sh") + ":3: ai-cli-launch:codex",
            rel("scripts", "run.py") + ":5: ai-cli-launch:claude",
            rel("scripts", "run.py") + ":6: ai-cli-launch:codex",
        })

    def test_this_repository_is_guard_clean(self):
        r = self.guard(REPO, "--terms", os.path.join(self.tmp, "no-terms.txt"))
        self.assertEqual(r.returncode, 0, r.stdout)


class PublishTests(Sandbox):
    def test_publish_refuses_guard_hits_then_lints_commits_and_pushes(self):
        bare = self.make_remote(self.public, "skills")
        write(os.path.join(self.public, "skills", "skillsmith", "scripts", "lint_skill.py"), FAKE_LINTER)
        self.git(self.public, "add", "-A")
        self.git(self.public, "commit", "-q", "-m", "linter")
        self.git(self.public, "push", "-q")
        head = self.git(self.public, "rev-parse", "HEAD")
        self.add_skill(self.public, "leaky", "Mail " + EMAIL + " for help.\n")
        r = self.cli("publish", "--checkout", self.public, "-m", "Add leaky")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("personal-email", r.stdout)
        self.assertEqual(self.git(self.public, "rev-parse", "HEAD"), head)
        self.assertEqual(self.git(bare, "rev-parse", "main"), head)
        self.add_skill(self.public, "leaky", "LINT-FAIL\n")
        r = self.cli("publish", "--checkout", self.public, "-m", "Add leaky")
        self.assertEqual(r.returncode, 1)
        self.assertIn("lint failed: leaky", r.stderr)
        self.add_skill(self.public, "leaky", "Ask the maintainers for help.\n")
        r = self.cli("publish", "--checkout", self.public, "-m", "Add a helpful skill")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.git(bare, "rev-parse", "main"), self.git(self.public, "rev-parse", "HEAD"))
        self.assertEqual(self.git(self.public, "log", "-1", "--format=%s"), "Add a helpful skill")
        self.assertEqual(self.git(self.public, "status", "--porcelain"), "")
        again = self.cli("publish", "--checkout", self.public, "-m", "noop")
        self.assertIn("nothing to publish", again.stdout)

    def test_private_checkout_publishes_without_the_public_guard(self):
        bare = self.make_remote(self.private, "skills-private")
        self.add_skill(self.private, "mailer", "Write from " + EMAIL + ".\n")
        r = self.cli("publish", "--checkout", self.private, "-m", "Add mailer")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.git(bare, "rev-parse", "main"), self.git(self.private, "rev-parse", "HEAD"))


class DoctorTests(Sandbox):
    def test_doctor_reports_profile_links_and_dirty_checkouts(self):
        self.up()
        ok = self.cli("doctor", "--repo", self.store, "--machines", self.machines)
        self.assertEqual(ok.returncode, 0, ok.stdout)
        self.assertIn("doctor: ok", ok.stdout)
        self.assertIn("never fetched", ok.stdout)
        write(os.path.join(self.public, "skills", "handoff", "extra.md"), "wip\n")
        os.unlink(os.path.join(self.store, ".claude/skills", "web-extract"))
        bad = self.cli("doctor", "--json", "--repo", self.store, "--machines", self.machines)
        self.assertEqual(bad.returncode, 1)
        report = json.loads(bad.stdout)
        self.assertEqual(report["scope"], "project")
        self.assertEqual(report["checkouts"]["public"]["dirty"], 1)
        self.assertTrue(any("dirty" in p for p in report["problems"]))
        self.assertTrue(any("missing link" in p and "web-extract" in p for p in report["problems"]))



def load_cli():
    loader = importlib.machinery.SourceFileLoader("skills_cli", CLI)
    spec = importlib.util.spec_from_loader("skills_cli", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def day(offset, base=None):
    return ((base or datetime.date.today()) + datetime.timedelta(days=offset)).isoformat()


def jsonl(path, records):
    write(path, "".join(json.dumps(r) + "\n" for r in records))


def claude_tool(when, *uses):
    return {"type": "assistant", "timestamp": when + "T01:00:00Z",
            "message": {"content": [{"type": "tool_use", "name": n, "input": i} for n, i in uses]}}


class YamlTests(unittest.TestCase):
    def test_subset_parser_matches_pyyaml_on_the_catalogs(self):
        cli = load_cli()
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        with open(os.path.join(REPO, "catalog.yaml"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertEqual(cli.load_yaml(text), yaml.safe_load(text))
        sample = ("pinned: [a, 'b, c']\ncats:\n  - key: x  # comment\n    links:\n      - url: https://e.com/#f\n"
                  "        note: \"Colon: inside\"\n        tags: [ui]\n    skills:\n    - one\n    - two\n")
        self.assertEqual(cli.load_yaml(sample), yaml.safe_load(sample))

    def test_categories_come_from_flow_and_block_lists(self):
        cli = load_cli()
        data = cli.load_yaml("categories:\n  - key: a\n    skills: [x, y]\n  - key: b\n    skills:\n      - z\n")
        self.assertEqual(cli.catalog_categories(data), {"a": {"x", "y"}, "b": {"z"}})
        with self.assertRaises(ValueError):
            cli.load_yaml("a: 1\n   b: 2\n")


class AutosyncTests(Sandbox):
    def setUp(self):
        super().setUp()
        self.public_bare = self.make_remote(self.public, "skills")
        self.private_bare = self.make_remote(self.private, "skills-private")
        self.write_machines({"root": self.root, "private": True})

    def autosync(self):
        return self.cli("autosync", "--repo", self.store, "--machines", self.machines)

    def test_dirty_checkouts_commit_with_generated_message_and_push(self):
        write(os.path.join(self.public, "skills", "handoff", "notes.md"), "More.\n")
        write(os.path.join(self.private, "skills", "cv", "extra.md"), "Private note.\n")
        r = self.autosync()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for checkout, bare in ((self.public, self.public_bare), (self.private, self.private_bare)):
            self.assertEqual(self.git(bare, "rev-parse", "main"), self.git(checkout, "rev-parse", "HEAD"))
            self.assertEqual(self.git(checkout, "status", "--porcelain"), "")
        self.assertEqual(self.git(self.public, "log", "-1", "--format=%s"), "Update handoff (auto-sync)")
        quiet = self.autosync()
        self.assertEqual((quiet.returncode, quiet.stdout, quiet.stderr), (0, "", ""))

    def test_guard_hit_blocks_the_public_checkout_with_exit_2(self):
        head = self.git(self.public, "rev-parse", "HEAD")
        self.add_skill(self.public, "leaky", "Mail " + EMAIL + ".\n")
        write(os.path.join(self.private, "skills", "cv", "extra.md"), "Fine.\n")
        r = self.autosync()
        self.assertEqual(r.returncode, 2)
        self.assertIn("personal-email", r.stderr)
        self.assertIn("another session's unfinished edit", r.stderr)
        self.assertEqual(self.git(self.public, "rev-parse", "HEAD"), head)
        self.assertEqual(self.git(self.private_bare, "rev-parse", "main"), self.git(self.private, "rev-parse", "HEAD"))

    def test_moved_remote_is_rebased_then_pushed(self):
        other = os.path.join(self.tmp, "other")
        self.git(self.tmp, "clone", "-q", self.public_bare, other)
        write(os.path.join(other, "skills", "web-extract", "more.md"), "Remote.\n")
        self.git(other, "add", "-A")
        self.git(other, "commit", "-q", "-m", "remote edit")
        self.git(other, "push", "-q", "origin", "HEAD:main")
        write(os.path.join(self.public, "skills", "handoff", "notes.md"), "Local.\n")
        r = self.autosync()
        self.assertEqual(r.returncode, 0, r.stderr)
        log = self.git(self.public_bare, "log", "--format=%s", "main")
        self.assertIn("remote edit", log)
        self.assertIn("Update handoff (auto-sync)", log)

    def test_conflict_keeps_the_local_commit_and_exits_2(self):
        other = os.path.join(self.tmp, "other")
        self.git(self.tmp, "clone", "-q", self.public_bare, other)
        self.add_skill(other, "handoff", "Remote body.\n")
        self.git(other, "commit", "-qam", "remote body")
        self.git(other, "push", "-q", "origin", "HEAD:main")
        self.add_skill(self.public, "handoff", "Local body.\n")
        r = self.autosync()
        self.assertEqual(r.returncode, 2)
        self.assertIn("conflicts", r.stderr)
        self.assertEqual(self.git(self.public, "log", "-1", "--format=%s"), "Update handoff (auto-sync)")
        self.assertFalse(os.path.exists(os.path.join(self.public, ".git", "rebase-merge")))


class PullFlowTests(Sandbox):
    def test_clean_checkout_rebases_local_commits_and_pushes_them(self):
        bare = self.make_remote(self.public, "skills")
        other = os.path.join(self.tmp, "other")
        self.git(self.tmp, "clone", "-q", bare, other)
        write(os.path.join(other, "skills", "web-extract", "more.md"), "Remote.\n")
        self.git(other, "add", "-A")
        self.git(other, "commit", "-q", "-m", "remote edit")
        self.git(other, "push", "-q", "origin", "HEAD:main")
        write(os.path.join(self.public, "skills", "handoff", "notes.md"), "Local.\n")
        self.git(self.public, "add", "-A")
        self.git(self.public, "commit", "-q", "-m", "local edit")
        r = self.up("--wait")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.git(bare, "rev-parse", "main"), self.git(self.public, "rev-parse", "HEAD"))
        self.assertEqual(self.git(bare, "log", "--format=%s", "-2", "main").splitlines(), ["local edit", "remote edit"])

    def test_unpushed_commits_that_fail_the_guard_are_not_pushed(self):
        bare = self.make_remote(self.public, "skills")
        head = self.git(bare, "rev-parse", "main")
        self.add_skill(self.public, "leaky", "Mail " + EMAIL + ".\n")
        self.git(self.public, "add", "-A")
        self.git(self.public, "commit", "-q", "-m", "leak")
        r = self.up("--wait")
        self.assertEqual(r.returncode, 0)
        self.assertIn("fail the guard", r.stderr)
        self.assertEqual(self.git(bare, "rev-parse", "main"), head)


class TidyRaceTests(Sandbox):
    def test_a_conflicting_tidy_commit_is_dropped_for_the_upstream_one(self):
        bare = self.make_remote(self.public, "skills")
        other = os.path.join(self.tmp, "other")
        self.git(self.tmp, "clone", "-q", bare, other)
        self.add_skill(other, "handoff", "Remote body.\n")
        self.git(other, "commit", "-qam", "remote body")
        self.git(other, "push", "-q", "origin", "HEAD:main")
        self.add_skill(self.public, "handoff", "Local body.\n")
        self.git(self.public, "commit", "-qam", "Shelve handoff (unused 30+ days)")
        r = self.up("--wait")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.git(self.public, "rev-parse", "HEAD"), self.git(bare, "rev-parse", "main"))
        self.assertEqual(r.stderr, "")


class UsageTests(Sandbox):
    def setUp(self):
        super().setUp()
        self.write_machines({"root": self.root, "private": True, "repos": [self.store]})
        self.projects = os.path.join(self.home, ".claude", "projects")
        self.slug = re.sub(r"[^A-Za-z0-9]", "-", self.store)

    def usage(self, *extra):
        r = self.cli("usage", "--repo", self.store, "--machines", self.machines, "--json", *extra)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_uses_count_but_edits_searches_mentions_and_maintenance_do_not(self):
        t = "2026-09-20"
        jsonl(os.path.join(self.projects, self.slug, "s1.jsonl"), [
            {"type": "user", "timestamp": t + "T00:00:00Z", "message": {"content": "<command-name>/cv</command-name>"}},
            claude_tool(t, ("Skill", {"skill": "handoff"}),
                        ("Read", {"file_path": self.store + "/.claude/skills/web-extract/SKILL.md"}),
                        ("Bash", {"command": "python3 .claude/skills/youtube-transcript/scripts/get.py URL"}),
                        ("Edit", {"file_path": ".claude/skills/system-diagram/SKILL.md"}),
                        ("Grep", {"path": ".claude/skills/feedback-loop/references/x.md"}),
                        ("Bash", {"command": "cat <<EOF\nRead .claude/skills/where-to-shop/SKILL.md\nEOF"})),
        ])
        session = os.path.join(self.projects, self.slug + "-learning-x", "s2")
        jsonl(session + ".jsonl", [claude_tool(t, ("Skill", {"skill": "system-diagram"}))])
        for i, name in enumerate(["web-extract", "handoff", "cv", "where-to-shop", "feedback-loop", "youtube-transcript"]):
            jsonl(os.path.join(session, "subagents", "agent-{}.jsonl".format(i)),
                  [claude_tool("2026-09-25", ("Read", {"file_path": ".claude/skills/{}/SKILL.md".format(name)}))])
        jsonl(os.path.join(self.projects, "-elsewhere", "s3.jsonl"), [claude_tool(t, ("Skill", {"skill": "feedback-loop"}))])
        jsonl(os.path.join(self.home, ".codex", "sessions", "2026", "09", "21", "rollout-1.jsonl"), [
            {"type": "session_meta", "payload": {"cwd": self.store}},
            {"type": "response_item", "timestamp": "2026-09-21T01:00:00Z",
             "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "use $where-to-shop, costs $5"}]}},
            {"type": "response_item", "timestamp": "2026-09-22T01:00:00Z",
             "payload": {"type": "function_call", "name": "exec_command",
                         "arguments": json.dumps({"cmd": "sed -n 1,80p .agents/skills/feedback-loop/SKILL.md"})}},
            {"type": "response_item", "timestamp": "2026-09-22T01:00:00Z",
             "payload": {"type": "custom_tool_call", "name": "apply_patch", "input": "*** Update File: .agents/skills/cv/SKILL.md"}},
        ])
        report = self.usage("--scan")
        last = {n: r["last"] for n, r in report["skills"].items()}
        self.assertEqual(last["cv"], t)
        self.assertEqual(last["handoff"], t)
        self.assertEqual(last["web-extract"], t)
        self.assertEqual(last["youtube-transcript"], t)
        self.assertEqual(last["system-diagram"], t)  # explicit use survives the maintenance session
        self.assertEqual(last["where-to-shop"], "2026-09-21")
        self.assertEqual(last["feedback-loop"], "2026-09-22")  # Codex read, not the other project
        path = os.path.join(self.private, "usage", "test-box.json")
        with open(path) as fh:
            data = json.load(fh)
        self.assertEqual(data["machine"], "Test box")
        self.assertTrue(data["tracked_since"])
        self.assertEqual(report["machines"], ["Test box"])

    def test_user_scope_reads_every_project_and_rescans_are_incremental(self):
        self.write_machines({"root": self.root, "private": True, "scope": "user"})
        jsonl(os.path.join(self.projects, "-elsewhere", "s3.jsonl"), [claude_tool("2026-09-23", ("Skill", {"skill": "cv"}))])
        self.assertEqual(self.usage("--scan")["skills"]["cv"]["last"], "2026-09-23")
        jsonl(os.path.join(self.projects, "-elsewhere", "s4.jsonl"), [claude_tool("2026-09-24", ("Skill", {"skill": "cv"}))])
        report = self.usage("--scan")
        self.assertEqual(report["skills"]["cv"]["last"], "2026-09-24")
        self.assertEqual(report["skills"]["cv"]["days_used"], 2)


class TidyTests(Sandbox):
    """Commits are dated today, so SKILLS_TODAY sits 60 days later: every skill is past its grace."""

    def setUp(self):
        super().setUp()
        self.public_bare = self.make_remote(self.public, "skills")
        self.private_bare = self.make_remote(self.private, "skills-private")
        self.write_machines({"root": self.root, "private": True, "repos": [self.store]})
        self.today = day(60)
        self.env["SKILLS_TODAY"] = self.today
        with open(os.path.join(self.public, "catalog.yaml"), "a") as fh:
            fh.write("pinned: [feedback-loop]\n")
        self.add_skill(self.public, "web-extract", "For video pages use the `youtube-transcript` skill.\n")
        self.git(self.public, "commit", "-qam", "pin and refer")
        self.git(self.public, "push", "-q")

    def record(self, skills, tracked_offset=-90, machine="other-box"):
        path = os.path.join(self.private, "usage", machine + ".json")
        write(path, json.dumps({"machine": machine, "tracked_since": day(60 + tracked_offset),
                                "skills": {n: [day(60 + o)] for n, o in skills.items()}}))
        self.git(self.private, "add", "-A")
        self.git(self.private, "commit", "-q", "-m", "usage")
        self.git(self.private, "push", "-q")

    def tidy(self, *extra):
        return self.cli("tidy", "--repo", self.store, "--machines", self.machines, *extra)

    def test_idle_skills_move_to_the_shelf_and_stop_being_linked(self):
        self.record({"web-extract": -3, "where-to-shop": -40})
        plan = self.tidy("--dry-run")
        self.assertEqual(plan.returncode, 0, plan.stderr)
        shelved = sorted(re.findall(r"^shelve\s+(\S+)", plan.stdout, re.M))
        self.assertEqual(shelved, ["cv", "handoff", "system-diagram", "where-to-shop"])
        self.assertTrue(os.path.isdir(os.path.join(self.public, "skills", "system-diagram")))
        r = self.tidy()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for checkout, name in ((self.public, "system-diagram"), (self.public, "handoff"), (self.private, "handoff"),
                               (self.private, "cv"), (self.private, "where-to-shop")):
            self.assertTrue(os.path.isfile(os.path.join(checkout, "rarely-used", name, "SKILL.md")), name)
        for checkout, bare in ((self.public, self.public_bare), (self.private, self.private_bare)):
            self.assertEqual(self.git(bare, "rev-parse", "main"), self.git(checkout, "rev-parse", "HEAD"))
        self.assertIn("Shelve", self.git(self.public, "log", "-1", "--format=%s"))
        self.up()
        self.assertEqual(sorted(self.store_links()), ["feedback-loop", "web-extract", "youtube-transcript"])
        found = self.cli("find", "--machines", self.machines, "--json", "system", "diagram")
        self.assertEqual(json.loads(found.stdout)[0]["tier"], "rarely used")

    def test_a_use_brings_a_shelved_skill_back(self):
        self.record({"web-extract": -3})
        self.assertEqual(self.tidy().returncode, 0)
        self.assertTrue(os.path.isdir(os.path.join(self.public, "rarely-used", "system-diagram")))
        self.record({"web-extract": -3, "system-diagram": -1}, machine="third-box")
        r = self.tidy()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("restore  system-diagram", r.stdout)
        self.assertTrue(os.path.isfile(os.path.join(self.public, "skills", "system-diagram", "SKILL.md")))

    def test_nothing_moves_without_a_month_of_data_or_inside_the_grace(self):
        self.record({}, tracked_offset=-10)
        self.assertIn("nothing to move", self.tidy("--dry-run").stdout)
        self.record({}, tracked_offset=-90)
        self.env["SKILLS_TODAY"] = day(0)
        self.assertIn("nothing to move", self.tidy("--dry-run").stdout)

    def test_background_sync_records_usage_tidies_and_pushes(self):
        self.record({"web-extract": -3}, tracked_offset=-90)
        r = self.cli("_sync", "--repo", self.store, "--machines", self.machines,
                     env={"SKILLS_MAINTAIN_INTERVAL": "0"})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isdir(os.path.join(self.public, "rarely-used", "system-diagram")))
        self.assertEqual(self.git(self.public_bare, "rev-parse", "main"), self.git(self.public, "rev-parse", "HEAD"))
        self.assertTrue(os.path.exists(os.path.join(self.private, "usage", "test-box.json")))
        self.assertEqual(self.git(self.private_bare, "rev-parse", "main"), self.git(self.private, "rev-parse", "HEAD"))

    def test_shelve_and_restore_by_hand(self):
        r = self.cli("shelve", "handoff", "--machines", self.machines)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isdir(os.path.join(self.private, "rarely-used", "handoff")))
        self.assertEqual(self.git(self.private, "log", "-1", "--format=%s"), "Shelve handoff (by hand)")
        r = self.cli("restore", "handoff", "nope", "--machines", self.machines)
        self.assertEqual(r.returncode, 1)
        self.assertIn("no rarely used skill named nope", r.stderr)
        self.assertTrue(os.path.isdir(os.path.join(self.private, "skills", "handoff")))


class StubTests(Sandbox):
    def shelve(self, checkout, name):
        os.makedirs(os.path.join(checkout, "rarely-used"), exist_ok=True)
        os.rename(os.path.join(checkout, "skills", name), os.path.join(checkout, "rarely-used", name))

    def test_shelved_skills_get_on_call_stubs_that_swap_with_links(self):
        self.up()
        self.shelve(self.public, "system-diagram")
        r = self.up()
        self.assertIn("on call", r.stdout)
        target = os.path.join(self.public, "rarely-used", "system-diagram")
        claude = os.path.join(self.store, ".claude", "skills", "system-diagram")
        codex = os.path.join(self.store, ".agents", "skills", "system-diagram")
        for stub in (claude, codex):
            self.assertTrue(os.path.isdir(stub) and not os.path.islink(stub))
        with open(os.path.join(claude, "SKILL.md")) as fh:
            text = fh.read()
        self.assertIn("name: system-diagram", text)
        self.assertIn("disable-model-invocation: true", text)
        self.assertIn("Does system-diagram.", text)
        self.assertIn(os.path.join(target, "SKILL.md"), text)
        with open(os.path.join(codex, "SKILL.md")) as fh:
            self.assertNotIn("disable-model-invocation", fh.read())
        with open(os.path.join(codex, "agents", "openai.yaml")) as fh:
            self.assertIn("allow_implicit_invocation: false", fh.read())
        self.assertNotIn("system-diagram", self.store_links())
        quiet = self.up()
        self.assertNotIn("stub", quiet.stdout)
        doctor = self.cli("doctor", "--repo", self.store, "--machines", self.machines)
        self.assertIn("1 stub(s) ok", doctor.stdout)
        os.rename(target, os.path.join(self.public, "skills", "system-diagram"))
        self.up()
        self.assertTrue(os.path.islink(claude))
        self.assertEqual(self.store_links()["system-diagram"], self.target(self.public, "system-diagram"))

    def test_foreign_folders_are_left_alone_and_unlink_removes_stubs(self):
        self.shelve(self.public, "system-diagram")
        self.shelve(self.public, "handoff")
        foreign = os.path.join(self.store, ".claude", "skills", "handoff")
        write(os.path.join(foreign, "SKILL.md"), "mine\n")
        r = self.up()
        self.assertIn("conflict", r.stdout)
        with open(os.path.join(foreign, "SKILL.md")) as fh:
            self.assertEqual(fh.read(), "mine\n")
        stub = os.path.join(self.store, ".claude", "skills", "system-diagram")
        self.assertTrue(os.path.isdir(stub))
        r = self.cli("unlink", "--repo", self.store, "--machines", self.machines)
        self.assertIn("stub(s) removed", r.stdout)
        self.assertFalse(os.path.exists(stub))
        self.assertTrue(os.path.isdir(foreign))

    def test_disabled_shelved_skills_get_no_stub(self):
        self.write_machines({"root": self.root, "disable": ["system-diagram"]})
        self.shelve(self.public, "system-diagram")
        self.up()
        self.assertFalse(os.path.exists(os.path.join(self.store, ".claude", "skills", "system-diagram")))


class FindTests(Sandbox):
    def setUp(self):
        super().setUp()
        self.write_machines({"root": self.root, "private": True})
        with open(os.path.join(self.public, "catalog.yaml")) as fh:
            text = fh.read()
        text = text.replace(
            "      - repo: someone/thing\n        note: Elsewhere.\n",
            "      - url: https://example.com/motion\n        name: motion-kit\n        note: Animate interfaces.\n"
            "        tags: [motion, animation]\n        from: \"A design video\"\n        from_url: https://example.com/v\n", 1)
        write(os.path.join(self.public, "catalog.yaml"), text)
        write(os.path.join(self.private, "archive", "skills", "old-slides", "SKILL.md"),
              "---\nname: old-slides\ndescription: Build slide decks the old way.\n---\n")
        os.makedirs(os.path.join(self.public, "rarely-used"))
        os.rename(os.path.join(self.public, "skills", "system-diagram"), os.path.join(self.public, "rarely-used", "system-diagram"))

    def find(self, *query):
        return self.cli("find", "--machines", self.machines, *query)

    def test_ranks_names_first_and_labels_each_tier(self):
        r = self.find("--json", "transcript")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)[0]["name"], "youtube-transcript")
        hits = {e["name"]: e for e in json.loads(self.find("--json", "--limit", "50").stdout)}
        self.assertEqual(hits["system-diagram"]["tier"], "rarely used")
        self.assertEqual(hits["old-slides"]["tier"], "retired")
        self.assertEqual(hits["motion-kit"]["tier"], "external")
        self.assertEqual(hits["cv"]["kind"], "private")
        animate = json.loads(self.find("--json", "animation").stdout)
        self.assertEqual(animate[0]["name"], "motion-kit")
        self.assertEqual(animate[0]["source"], "A design video")
        text = self.find("diagram").stdout
        self.assertIn("rarely used = not linked", text)
        self.assertEqual(self.find("zebra", "quantum").returncode, 1)
        cli = load_cli()
        self.assertTrue(cli.term_hits("planning", "Plan or replan a trip"))
        self.assertTrue(cli.term_hits("decks", "a deck reviewer"))
        self.assertFalse(cli.term_hits("plan", "ong6/groundplane library"))
        self.assertFalse(cli.term_hits("ui", "build the suite"))


if __name__ == "__main__":
    unittest.main()
