#!/usr/bin/env bash
# Sandbox test for sync.sh: consumer repos and bare upstreams, no network.
# Run: bash scripts/test-sync.sh   (exit 0 = all scenarios pass)
set -eu
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
# Never inherit a consumer's hooks or signing setup into these temporary repos.
unset GIT_CONFIG_PARAMETERS GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR
mkdir "$T/git-template"
export GIT_CONFIG_COUNT=3 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/dev/null
export GIT_CONFIG_KEY_1=commit.gpgSign GIT_CONFIG_VALUE_1=false
export GIT_CONFIG_KEY_2=init.templateDir GIT_CONFIG_VALUE_2="$T/git-template"
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

# A clean consumer with tracked files outside the subtree. Each regression
# starts here, with a recorded sync point and no SessionStart background fetch.
fixture() {
  local repo=$1
  mk "$repo"
  git -C "$repo" subtree add -q --squash --prefix="$P" "$T/upstream.git" main 2>/dev/null
  printf 'base\n' > "$repo/outside.txt"
  printf 'base\n' > "$repo/unstaged.txt"
  git -C "$repo" add -A
  git -C "$repo" commit -qm "consumer files"
  sync "$repo" --fetch
  sync "$repo" --merge 2>/dev/null
}
snapshot_outside() {
  local repo=$1 dest=$2
  mkdir -p "$dest"
  git -C "$repo" diff --cached --binary -- outside.txt unstaged.txt > "$dest/staged"
  git -C "$repo" diff --binary -- outside.txt unstaged.txt > "$dest/unstaged"
  git -C "$repo" status --porcelain --untracked-files=all -- outside.txt unstaged.txt untracked.txt > "$dest/status"
  cp "$repo/outside.txt" "$dest/outside"
  cp "$repo/unstaged.txt" "$dest/other"
  [ ! -f "$repo/untracked.txt" ] || cp "$repo/untracked.txt" "$dest/untracked"
}

# A start/merge may combine local edits with upstream without uploading them.
# The recorded tree must describe upstream, so the following stop still pushes.
repo="$T/pending-local"
fixture "$repo"
fixture "$T/remote-writer"
printf 'local pending upload\n' > "$repo/$P/pending-local.md"
printf 'remote edit\n' > "$T/remote-writer/$P/remote-edit.md"
sync "$T/remote-writer" --stop 2>/dev/null
sync "$repo" --fetch
sync "$repo" --merge 2>/dev/null
check "merge receives upstream and preserves uncommitted local edits" \
  "[ -f '$repo/$P/pending-local.md' ] && [ -f '$repo/$P/remote-edit.md' ] && [ -z \"\$(git -C '$repo' status --porcelain)\" ]"
check "merged local edits are not recorded as already uploaded" \
  "[ \"\$(sed -n 's/^tree=//p' '$repo/.git/skills-sync')\" = \"\$(git -C '$T/upstream.git' rev-parse 'main^{tree}')\" ]"
sync "$repo" --stop 2>/dev/null
check "stop uploads local edits after a start-time merge" \
  "git -C '$T/upstream.git' show main:pending-local.md 2>/dev/null | grep -q 'local pending upload'"

# Status advertises itself as read-only even before a remote has been installed.
repo="$T/status-only"
mk "$repo"
mkdir -p "$repo/$P"
cp -R "$HERE/scripts" "$repo/$P/"
git -C "$repo" add -A
git -C "$repo" commit -qm "install scripts"
cp "$repo/.git/config" "$T/status-config-before"
sync "$repo" --status >/dev/null
check "status does not install a remote" "cmp -s '$T/status-config-before' '$repo/.git/config'"

# Each individual kind of unrelated work defers push, while the skills commit
# still happens. The mixed case preserves staging and worktree bytes separately.
for kind in staged unstaged untracked mixed; do
  repo="$T/dirty-$kind"
  fixture "$repo"
  case "$kind" in
    staged|mixed)
      printf 'staged\n' > "$repo/outside.txt"
      git -C "$repo" add outside.txt ;;
  esac
  case "$kind" in
    unstaged|mixed)
      printf 'working tree\n' > "$repo/outside.txt"
      printf 'other working tree\n' > "$repo/unstaged.txt" ;;
  esac
  case "$kind" in
    untracked|mixed) printf 'untracked\n' > "$repo/untracked.txt" ;;
  esac
  printf 'changed skill\n' >> "$repo/$P/README.md"
  printf 'new skill\n' > "$repo/$P/added-$kind.md"
  git -C "$repo" rm -q -- "$P/new-file.md"
  snapshot_outside "$repo" "$T/$kind-before"
  cp "$repo/.git/skills-sync" "$T/$kind-state"
  upstream_before="$(git -C "$T/upstream.git" rev-parse main)"
  rc=0; out="$(sync "$repo" --stop 2>&1)" || rc=$?
  snapshot_outside "$repo" "$T/$kind-after"
  check "$kind work defers with exit 0" "[ $rc -eq 0 ] && echo \"$out\" | grep -q 'unrelated work present; sync deferred'"
  check "$kind outside staging and bytes survive" "diff -r '$T/$kind-before' '$T/$kind-after' >/dev/null"
  check "$kind sync hashes and upstream remain unchanged" \
    "cmp -s '$T/$kind-state' '$repo/.git/skills-sync' && [ '$upstream_before' = \"\$(git -C '$T/upstream.git' rev-parse main)\" ]"
  check "$kind commit contains only added, modified and deleted skills" \
    "[ \"\$(git -C '$repo' diff-tree --no-commit-id --name-only -r HEAD)\" = \"$P/README.md
$P/added-$kind.md
$P/new-file.md\" ] && git -C '$repo' diff --quiet HEAD -- '$P'"

  # No new skill edit on the next run: still no commit, sync or outside changes.
  head_before="$(git -C "$repo" rev-parse HEAD)"
  sync "$repo" --push 2>/dev/null
  check "$kind retry without skill edits preserves HEAD and sync state" \
    "[ '$head_before' = \"\$(git -C '$repo' rev-parse HEAD)\" ] && cmp -s '$T/$kind-state' '$repo/.git/skills-sync'"
  git -C "$repo" add -A
  git -C "$repo" commit -qm "finish consumer work"
  sync "$repo" --stop 2>/dev/null
  check "$kind deferred edits sync once consumer work is committed" \
    "[ \"\$(git -C '$repo' rev-parse 'HEAD:$P')\" = \"\$(git -C '$T/upstream.git' rev-parse 'main^{tree}')\" ] && [ -z \"\$(git -C '$repo' status --porcelain)\" ]"
  # Restore this fixture's deleted file upstream for the next independent case.
  printf 'fixture file\n' > "$repo/$P/new-file.md"
  sync "$repo" --stop 2>/dev/null
done

# A changed upstream must not be merged over unrelated work, through either
# merge entry point. Fetching may update refs; the recorded sync point must not.
for mode in --merge --start; do
  repo="$T/dirty-${mode#--}"
  fixture "$repo"
  cp "$repo/.git/skills-sync" "$T/${mode#--}-state"
  printf 'pending local skill\n' >> "$repo/$P/README.md"
  printf 'pending outside\n' > "$repo/outside.txt"
  git -C "$repo" add outside.txt
  snapshot_outside "$repo" "$T/${mode#--}-before"
  printf 'new upstream %s\n' "$mode" > "$T/dirty-mixed/$P/remote-only.md"
  sync "$T/dirty-mixed" --stop 2>/dev/null
  sync "$repo" --fetch
  rc=0; out="$(sync "$repo" "$mode" 2>&1)" || rc=$?
  snapshot_outside "$repo" "$T/${mode#--}-after"
  check "$mode preserves consumer work and defers an upstream merge" \
    "[ $rc -eq 0 ] && echo \"$out\" | grep -q 'sync deferred' && diff -r '$T/${mode#--}-before' '$T/${mode#--}-after' >/dev/null && cmp -s '$T/${mode#--}-state' '$repo/.git/skills-sync' && [ ! -e '$repo/.git/MERGE_HEAD' ]"
done

# Operation markers cover merges, cherry-picks/reverts and both rebase backends.
# Every history-changing entry point must leave HEAD, index, worktree and state.
repo="$T/operation"
fixture "$repo"
printf 'pending skill\n' >> "$repo/$P/README.md"
cp "$repo/.git/skills-sync" "$T/operation-state"
head_before="$(git -C "$repo" rev-parse HEAD)"
git -C "$repo" diff --binary > "$T/operation-worktree"
for marker in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD rebase-merge rebase-apply sequencer; do
  case "$marker" in
    rebase-*|sequencer) mkdir "$repo/.git/$marker" ;;
    *) printf '%s\n' "$head_before" > "$repo/.git/$marker" ;;
  esac
  for mode in --start --stop --merge --push; do
    rc=0; out="$(sync "$repo" "$mode" 2>&1)" || rc=$?
    check "$marker defers $mode before mutation" \
      "[ $rc -eq 0 ] && echo \"$out\" | grep -q 'Git operation in progress' && [ '$head_before' = \"\$(git -C '$repo' rev-parse HEAD)\" ] && git -C '$repo' diff --cached --quiet && cmp -s '$T/operation-state' '$repo/.git/skills-sync' && [ -e '$repo/.git/$marker' ]"
  done
  case "$marker" in rebase-*|sequencer) rmdir "$repo/.git/$marker" ;; *) rm "$repo/.git/$marker" ;; esac
done
git -C "$repo" diff --binary > "$T/operation-worktree-after"
check "all operation guards preserve pending skill bytes" "cmp -s '$T/operation-worktree' '$T/operation-worktree-after'"

# An unmerged index without an operation marker still blocks the prefix commit.
blob="$(git -C "$repo" rev-parse HEAD:outside.txt)"
printf '0 %040d\toutside.txt\n100644 %s 1\toutside.txt\n100644 %s 2\toutside.txt\n100644 %s 3\toutside.txt\n' 0 "$blob" "$blob" "$blob" | git -C "$repo" update-index --index-info
git -C "$repo" ls-files --stage > "$T/unmerged-before"
rc=0; out="$(sync "$repo" --stop 2>&1)" || rc=$?
git -C "$repo" ls-files --stage > "$T/unmerged-after"
check "unmerged index defers without clearing staged conflict entries" \
  "[ $rc -eq 0 ] && echo \"$out\" | grep -q 'unmerged index entries' && cmp -s '$T/unmerged-before' '$T/unmerged-after' && cmp -s '$T/operation-state' '$repo/.git/skills-sync' && [ '$head_before' = \"\$(git -C '$repo' rev-parse HEAD)\" ]"

# Ignored local files must survive incoming additions, including file/directory
# collisions. Unrelated ignored caches must not prevent a safe merge.
fixture "$T/ignored-writer"
for kind in file directory parent-file; do
  repo="$T/ignored-$kind"
  fixture "$repo"
  mkdir -p "$repo/.git/info"
  printf '*.local\n*.cache\n' > "$repo/.git/info/exclude"
  printf 'harmless cache\n' > "$repo/$P/scripts/unrelated.cache"
  collision="ignored-$kind.local"
  case "$kind" in
    directory)
      mkdir "$repo/$P/$collision"
      printf 'owner bytes\n' > "$repo/$P/$collision/child"
      printf 'upstream bytes\n' > "$T/ignored-writer/$P/$collision" ;;
    parent-file)
      printf 'owner bytes\n' > "$repo/$P/$collision"
      mkdir "$T/ignored-writer/$P/$collision"
      printf 'upstream bytes\n' > "$T/ignored-writer/$P/$collision/child" ;;
    *)
      printf 'owner bytes\n' > "$repo/$P/$collision"
      printf 'upstream bytes\n' > "$T/ignored-writer/$P/$collision" ;;
  esac
  cp -R "$repo/$P/$collision" "$T/ignored-$kind-before"
  sync "$T/ignored-writer" --stop 2>/dev/null
  sync "$repo" --fetch
  cp "$repo/.git/skills-sync" "$T/ignored-$kind-state"
  head_before="$(git -C "$repo" rev-parse HEAD)"
  rc=0; out="$(sync "$repo" --merge 2>&1)" || rc=$?
  check "ignored $kind collision defers with bytes and state intact" \
    "[ $rc -eq 0 ] && echo \"$out\" | grep -q 'ignored local path overlaps' && diff -r '$T/ignored-$kind-before' '$repo/$P/$collision' >/dev/null && cmp -s '$T/ignored-$kind-state' '$repo/.git/skills-sync' && [ '$head_before' = \"\$(git -C '$repo' rev-parse HEAD)\" ]"
  rm -rf "$repo/$P/$collision"
  sync "$repo" --merge 2>/dev/null
  check "unrelated ignored cache permits $kind merge" \
    "[ \"\$(git -C '$repo' rev-parse 'HEAD:$P')\" = \"\$(git -C '$T/upstream.git' rev-parse 'main^{tree}')\" ] && grep -q 'harmless cache' '$repo/$P/scripts/unrelated.cache'"
done

# An explicit URL cannot be silently ignored in favor of an existing fetch or
# push URL. Reject before committing local edits or touching either destination.
for kind in fetch push; do
  repo="$T/url-$kind"
  fixture "$repo"
  git init -q --bare -b main "$T/url-$kind-intended.git"
  expected_url="$T/url-$kind-intended.git"
  if [ "$kind" = push ]; then
    git -C "$repo" remote set-url --push skills "$expected_url"
    expected_url="$T/upstream.git"
  fi
  printf 'pending local\n' > "$repo/$P/url-local.md"
  head_before="$(git -C "$repo" rev-parse HEAD)"
  upstream_before="$(git -C "$T/upstream.git" rev-parse main)"
  rc=0; out="$(SKILLS_SYNC_URL="$expected_url" sync "$repo" --stop 2>&1)" || rc=$?
  check "explicit URL mismatch in $kind destination defers before mutation" \
    "[ $rc -eq 0 ] && echo \"$out\" | grep -q 'differs from SKILLS_SYNC_URL' && [ '$head_before' = \"\$(git -C '$repo' rev-parse HEAD)\" ] && [ '$upstream_before' = \"\$(git -C '$T/upstream.git' rev-parse main)\" ] && ! git -C '$T/url-$kind-intended.git' rev-parse --verify main >/dev/null 2>&1"
done

repo="$T/changed-target"
fixture "$repo"
git init -q --bare -b main "$T/changed-target.git"
SKILLS_SYNC_URL="$T/changed-target.git" SKILLS_SYNC_REMOTE=alternate sync "$repo" --stop 2>/dev/null
check "unchanged tree still bootstraps a newly selected destination" \
  "[ \"\$(git -C '$repo' rev-parse 'HEAD:$P')\" = \"\$(git -C '$T/changed-target.git' rev-parse 'main^{tree}')\" ]"

repo="$T/retargeted-remote"
fixture "$repo"
git init -q --bare -b main "$T/retargeted-remote.git"
git -C "$repo" remote set-url skills "$T/retargeted-remote.git"
cp "$repo/.git/skills-sync" "$T/retarget-state-before"
SKILLS_SYNC_URL="$T/retargeted-remote.git" sync "$repo" --start 2>/dev/null
check "failed fetch after URL change cannot adopt the old cached ref" \
  "cmp -s '$T/retarget-state-before' '$repo/.git/skills-sync'"
SKILLS_SYNC_URL="$T/retargeted-remote.git" sync "$repo" --merge 2>/dev/null
check "direct merge cannot adopt a cached ref from the old URL" \
  "cmp -s '$T/retarget-state-before' '$repo/.git/skills-sync'"
SKILLS_SYNC_URL="$T/retargeted-remote.git" sync "$repo" --stop 2>/dev/null
check "stop bootstraps retargeted empty remote after start defers" \
  "[ \"\$(git -C '$repo' rev-parse 'HEAD:$P')\" = \"\$(git -C '$T/retargeted-remote.git' rev-parse 'main^{tree}')\" ]"

# Shell quoting does not make a Git pathspec literal. A glob in the installed
# folder name must not stage or commit a matching sibling's private files.
repo="$T/glob-prefix"
mk "$repo"
mkdir -p "$repo/pack*" "$repo/package-private"
cp -R "$HERE/scripts" "$repo/pack*/"
printf 'base\n' > "$repo/package-private/private.txt"
git -C "$repo" add -A
git -C "$repo" commit -qm "install glob prefix"
printf 'private staged change\n' > "$repo/package-private/private.txt"
git -C "$repo" add package-private/private.txt
printf 'skill edit\n' > "$repo/pack*/skill.txt"
git -C "$repo" diff --cached --binary > "$T/glob-index-before"
bash "$repo/pack*/scripts/sync.sh" --stop 2>/dev/null
git -C "$repo" diff --cached --binary > "$T/glob-index-after"
check "glob prefix commits only its own files and preserves outside staging" \
  "cmp -s '$T/glob-index-before' '$T/glob-index-after' && [ \"\$(git -C '$repo' diff-tree --no-commit-id --name-only -r HEAD)\" = 'pack*/skill.txt' ]"

# Upstream can advance after accepting our push but before the following fetch.
# A receive hook creates that race deterministically, without timing or network.
repo="$T/push-race"
fixture "$repo"
git clone -q --bare "$T/upstream.git" "$T/race-upstream.git"
git -C "$repo" remote set-url skills "$T/race-upstream.git"
git -C "$repo" config remote.skills.receivepack 'git -c core.hooksPath=hooks receive-pack'
# Record the new destination before adding the pending local edit.
SKILLS_SYNC_URL="$T/race-upstream.git" sync "$repo" --fetch
SKILLS_SYNC_URL="$T/race-upstream.git" sync "$repo" --merge 2>/dev/null
mkdir -p "$T/race-upstream.git/hooks"
cat > "$T/race-upstream.git/hooks/post-receive" <<'HOOK'
#!/usr/bin/env bash
set -eu
while read -r old new ref; do
  [ "$ref" = refs/heads/main ] || continue
  blob=$(printf 'upstream changed this after our push\n' | git hash-object -w --stdin)
  tree=$({ git ls-tree "$new" | grep -v $'\tpush-race.md$'; printf '100644 blob %s\tpush-race.md\n' "$blob"; } | git mktree)
  commit=$(printf 'concurrent upstream edit\n' | git commit-tree "$tree" -p "$new")
  git update-ref "$ref" "$commit" "$new"
done
HOOK
chmod +x "$T/race-upstream.git/hooks/post-receive"
printf 'our pending edit\n' > "$repo/$P/push-race.md"
cp "$repo/.git/skills-sync" "$T/race-state-before"
rc=0; out="$(SKILLS_SYNC_URL="$T/race-upstream.git" sync "$repo" --stop 2>&1)" || rc=$?
check "post-push conflict is reported instead of claiming success" \
  "[ $rc -eq 2 ] && echo \"$out\" | grep -q CONFLICT"
check "post-push conflict preserves state and local edit" \
  "cmp -s '$T/race-state-before' '$repo/.git/skills-sync' && grep -q 'our pending edit' '$repo/$P/push-race.md' && [ -z \"\$(git -C '$repo' status --porcelain)\" ] && [ ! -e '$repo/.git/MERGE_HEAD' ]"
rc=0; SKILLS_SYNC_URL="$T/race-upstream.git" sync "$repo" --merge >/dev/null 2>&1 || rc=$?
check "failed post-push merge remains pending on retry" "[ $rc -eq 2 ]"

echo "sync tests: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
