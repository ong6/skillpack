#!/usr/bin/env bash
# Sandbox test for sync.sh: two consumer repos, one bare upstream, no network.
# Run: bash scripts/test-sync.sh   (exit 0 = all scenarios pass)
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
export SKILLS_SYNC_URL="$T/upstream.git" SKILLS_SYNC_REMOTE=skills SKILLS_SYNC_BRANCH=main
P=.claude/shared-skills
pass=0; fail=0
check() { if eval "$2"; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: $1" >&2; fi; }
mk() { git init -q -b main "$1"; git -C "$1" commit -q --allow-empty -m init; }
sync() { local repo=$1; shift; bash "$repo/$P/scripts/sync.sh" "$@"; }

git init -q --bare -b main "$T/upstream.git"

# A: folder created by hand, no subtree history yet -> bootstrap.
mk "$T/A"; mkdir -p "$T/A/$P"; cp -R "$HERE/scripts" "$T/A/$P/"; echo "# skills" > "$T/A/$P/README.md"
git -C "$T/A" add -A; git -C "$T/A" commit -q -m "add skill"
sync "$T/A" --stop 2>/dev/null
check "bootstrap creates upstream main" "git -C '$T/upstream.git' rev-parse -q --verify main >/dev/null"
check "bootstrap leaves a squash baseline" "git -C '$T/A' log --grep='git-subtree-dir' --oneline | grep -q ."
check "bootstrap is a no-op second time" "[ -z \"\$(sync '$T/A' --stop 2>&1)\" ]"

# B: installed the documented way.
mk "$T/B"; git -C "$T/B" subtree add -q --squash --prefix="$P" "$T/upstream.git" main 2>/dev/null
sync "$T/B" --start 2>/dev/null; sleep 1
check "fresh install records synced state" "grep -q '^remote=' '$T/B/.git/skills-sync'"

# B edits and pushes; A merges at next start.
echo "from B" >> "$T/B/$P/README.md"; git -C "$T/B" commit -qam "B edit"
sync "$T/B" --stop 2>/dev/null
check "B push reaches upstream" "git -C '$T/upstream.git' log -1 --format=%s main | grep -q 'B edit'"
sync "$T/A" --fetch; sync "$T/A" --merge 2>/dev/null
check "A receives B's edit" "grep -q 'from B' '$T/A/$P/README.md'"
check "A merge leaves tree clean" "[ -z \"\$(git -C '$T/A' status --porcelain)\" ]"

# A edits (uncommitted) and pushes at stop; B merges at start.
echo "from A" > "$T/A/$P/new-file.md"
sync "$T/A" --stop 2>/dev/null
check "A commits then pushes uncommitted skill edit" "git -C '$T/upstream.git' ls-tree --name-only main | grep -q new-file.md"
sync "$T/B" --fetch; sync "$T/B" --merge 2>/dev/null
check "B receives A's new file" "[ -f '$T/B/$P/new-file.md' ]"

# Both edit different files: push merges upstream first, then pushes.
echo "B2" >> "$T/B/$P/new-file.md"; git -C "$T/B" commit -qam "B2"; sync "$T/B" --stop 2>/dev/null
echo "A2" >> "$T/A/$P/README.md"; git -C "$T/A" commit -qam "A2"; sync "$T/A" --stop 2>/dev/null
check "non-conflicting concurrent edits both land upstream" \
  "git -C '$T/upstream.git' show main:new-file.md | grep -q B2 && git -C '$T/upstream.git' show main:README.md | grep -q A2"

# Same line on both sides: conflict reported, tree left clean, exit 2.
echo "B3" > "$T/B/$P/new-file.md"; git -C "$T/B" commit -qam "B3"; sync "$T/B" --stop 2>/dev/null
echo "A3" > "$T/A/$P/new-file.md"; git -C "$T/A" commit -qam "A3"
rc=0; out="$(sync "$T/A" --stop 2>&1)" || rc=$?
check "conflict exits 2 with a message" "[ $rc -eq 2 ] && echo \"$out\" | grep -q CONFLICT"
check "conflict leaves no merge in progress" "[ ! -e '$T/A/.git/MERGE_HEAD' ]"

# A subtree-add consumer pointed at a brand-new empty upstream bootstraps it too.
git init -q --bare -b main "$T/upstream2.git"
mk "$T/C"; git -C "$T/C" subtree add -q --squash --prefix="$P" "$T/upstream.git" main 2>/dev/null
echo "from C" >> "$T/C/$P/README.md"; git -C "$T/C" commit -qam "C edit"
SKILLS_SYNC_URL="$T/upstream2.git" SKILLS_SYNC_REMOTE=fl2 sync "$T/C" --stop 2>/dev/null
check "subtree-add consumer bootstraps an empty upstream" "git -C '$T/upstream2.git' show main:README.md 2>/dev/null | grep -q 'from C'"
echo "C2" >> "$T/C/$P/README.md"; git -C "$T/C" commit -qam "C2"
SKILLS_SYNC_URL="$T/upstream2.git" SKILLS_SYNC_REMOTE=fl2 sync "$T/C" --stop 2>/dev/null
check "and keeps pushing afterwards" "git -C '$T/upstream2.git' show main:README.md 2>/dev/null | grep -q C2"

# Unreachable upstream never fails the hook.
rc=0; SKILLS_SYNC_URL=/nonexistent bash -c "cd '$T/B' && git remote set-url skills /nonexistent && echo x >> $P/README.md && git commit -qam x && bash $P/scripts/sync.sh --stop" 2>/dev/null || rc=$?
check "unreachable upstream exits 0" "[ $rc -eq 0 ]"

echo "sync tests: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
