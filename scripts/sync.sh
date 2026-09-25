#!/usr/bin/env bash
# Keep this skills collection in sync with its upstream repository from inside a
# consumer repo, using `git subtree`. The folder is the canonical copy in every
# consumer; this script moves changes in both directions.
#
#   sync.sh --start   SessionStart: merge whatever the last background fetch
#                     brought in (local, no network), then fetch again in the
#                     background for the next session.
#   sync.sh --stop    Stop: if the folder changed locally since the last sync,
#                     push it upstream (merging upstream first if it moved).
#   sync.sh --status  Human-readable state. No changes.
#
# Configuration (env, all optional):
#   SKILLS_SYNC_URL     upstream URL    (default https://github.com/ong6/skillpack.git)
#   SKILLS_SYNC_REMOTE  remote name     (default skills)
#   SKILLS_SYNC_BRANCH  upstream branch (default main)
#
# The first start fetches synchronously; later starts use the cached ref. A
# missing network, unrelated work or an in-progress Git operation defers sync
# with exit 0. A merge conflict exits 2 so the hook can wake the agent.
set -u
export GIT_TERMINAL_PROMPT=0
export GIT_LITERAL_PATHSPECS=1

URL="${SKILLS_SYNC_URL:-https://github.com/ong6/skillpack.git}"
REMOTE="${SKILLS_SYNC_REMOTE:-skills}"
BRANCH="${SKILLS_SYNC_BRANCH:-main}"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
ROOT="$(git -C "$SKILL_DIR" rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$ROOT" || exit 0
PREFIX="${SKILL_DIR#"$ROOT"/}"
[ "$PREFIX" != "$SKILL_DIR" ] && [ -n "$PREFIX" ] || exit 0
STATE="$(git rev-parse --git-path skills-sync)"
LOCK="$(git rev-parse --git-path skills-sync.lock)"
REF="refs/remotes/$REMOTE/$BRANCH"
# A saved tree applies only to this subtree and destination. Hash without -w
# keeps --status read-only and avoids putting URLs into the state file.
TARGET="$(printf '%s\n' "$PREFIX" "$REMOTE" "$BRANCH" "$(git remote get-url "$REMOTE" 2>/dev/null || printf '%s' "$URL")" "$(git remote get-url --push --all "$REMOTE" 2>/dev/null || printf '%s' "$URL")" | git hash-object --stdin)"

say() { printf 'skills-sync: %s\n' "$*" >&2; }

ensure_remote() {
  local existing
  if existing="$(git remote get-url "$REMOTE" 2>/dev/null)"; then
    if [ -n "${SKILLS_SYNC_URL:-}" ] && { [ "$existing" != "$URL" ] || [ "$(git remote get-url --push --all "$REMOTE")" != "$URL" ]; }; then
      say "configured remote $REMOTE differs from SKILLS_SYNC_URL; sync deferred. Select a matching remote or update its URL explicitly."
      return 1
    fi
  else
    git remote add "$REMOTE" "$URL" 2>/dev/null || return 1
  fi
}

local_tree() { git rev-parse -q --verify "HEAD:$PREFIX" 2>/dev/null || echo none; }
remote_sha() { git rev-parse -q --verify "$REF" 2>/dev/null || echo none; }
state_get() {
  [ -f "$STATE" ] || return 0
  [ "$(sed -n 's/^target=//p' "$STATE")" = "$TARGET" ] || return 0
  sed -n "s/^$1=//p" "$STATE"
}
state_set() { printf 'tree=%s\nremote=%s\ntarget=%s\n' "$1" "$2" "$TARGET" > "$STATE"; }

# Do not commit into, abort or reset an operation the owner already started.
operation_idle() {
  local marker
  for marker in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD rebase-merge rebase-apply sequencer; do
    if [ -e "$(git rev-parse --git-path "$marker")" ]; then
      say "Git operation in progress; sync deferred."
      return 1
    fi
  done
  if [ -n "$(git ls-files --unmerged)" ]; then
    say "unmerged index entries; sync deferred."
    return 1
  fi
}

# Stage this folder, then explicitly exclude anything already staged elsewhere.
commit_prefix() {
  [ -n "$(git status --porcelain -- "$PREFIX")" ] || return 0
  git add -A -- "$PREFIX" || return 1
  git diff --cached --quiet -- "$PREFIX" && return 0
  git commit --only -q -m "skills-sync: commit skill edits before sync" -- "$PREFIX" || return 1
}

# Called after commit_prefix: remaining work belongs to the consumer. Subtree
# merge/rejoin needs a clean checkout; leave the index and worktree as they are.
checkout_clean() {
  if [ -n "$(git status --porcelain --untracked-files=all)" ]; then
    say "unrelated work present; sync deferred."
    return 1
  fi
}

# Git merge normally overwrites ignored, untracked files. Check only ignored
# paths that overlap upstream, so caches unrelated to an incoming path are fine.
ignored_paths_safe() {
  local upstream=$1 ignored relative original object_type
  while IFS= read -r -d '' ignored; do
    relative="${ignored#"$PREFIX"/}"
    original="$relative"
    while :; do
      if object_type="$(git cat-file -t "$upstream:$relative" 2>/dev/null)"; then
        if [ "$relative" = "$original" ] || [ "$object_type" != tree ]; then
          say "ignored local path overlaps upstream: $ignored; sync deferred."
          return 1
        fi
      fi
      case "$relative" in */*) relative="${relative%/*}" ;; *) break ;; esac
    done
  done < <(git ls-files --others --ignored --exclude-standard -z -- "$PREFIX")
}

fetch_bg() {
  # Stale lock (>10 min) from a killed job is reclaimed.
  if [ -d "$LOCK" ] && [ -n "$(find "$LOCK" -mmin +10 2>/dev/null)" ]; then rmdir "$LOCK" 2>/dev/null; fi
  mkdir "$LOCK" 2>/dev/null || return 0
  (
    trap 'rmdir "$LOCK" 2>/dev/null' EXIT
    git fetch -q "$REMOTE" "+refs/heads/$BRANCH:$REF" 2>/dev/null || true
  ) >/dev/null 2>&1 &
}

fetch_now() { git fetch -q "$REMOTE" "+refs/heads/$BRANCH:$REF" 2>/dev/null; }

has_squash_base() {
  git log --format=%B --fixed-strings --grep="git-subtree-dir: $PREFIX" HEAD 2>/dev/null |
    grep -F -x -e "git-subtree-dir: $PREFIX" -e "git-subtree-dir: $PREFIX/" >/dev/null
}

# Merge the fetched upstream ref into the folder. Returns 0 (merged or nothing
# to do), 2 on conflict (merge aborted).
merge_remote() {
  # Remote-tracking refs survive URL changes. Never adopt a cached ref under a
  # new target identity until a fetch from that destination has succeeded.
  if [ -z "$(state_get remote)" ] && ! fetch_now; then
    say "upstream ref unavailable for this destination; merge deferred."
    return 0
  fi
  local r; r="$(remote_sha)"
  [ "$r" != none ] || return 0
  [ "$r" != "$(state_get remote)" ] || return 0
  commit_prefix || { say "could not commit local skill edits; merge skipped."; return 0; }
  checkout_clean || return 0
  ignored_paths_safe "$r" || return 0
  if [ "$(state_get remote)" = "" ] && [ "$(git rev-parse -q --verify "$r^{tree}")" = "$(local_tree)" ]; then
    state_set "$(local_tree)" "$r"; return 0     # first run, already identical
  fi
  if ! has_squash_base; then
    say "no subtree baseline for $PREFIX; run: git subtree add --squash --prefix=$PREFIX $REMOTE $BRANCH"
    return 0
  fi
  if git subtree merge -q --squash --prefix="$PREFIX" "$r" -m "skills-sync: merge upstream $PREFIX" >/dev/null 2>&1; then
    # A merge can include local edits that have never reached upstream. Record
    # the upstream tree, otherwise --stop mistakes those edits for an upload.
    state_set "$(git rev-parse "$r^{tree}")" "$r"
    say "merged upstream changes into $PREFIX"
    return 0
  fi
  local files; files="$(git diff --name-only --diff-filter=U 2>/dev/null | tr '\n' ' ')"
  git merge --abort 2>/dev/null || git reset -q --merge 2>/dev/null
  say "CONFLICT merging upstream into $PREFIX (in: ${files:-unknown}). Resolve: git subtree merge --squash --prefix=$PREFIX $r, fix, commit, then rerun sync.sh --stop."
  return 2
}

push_local() {
  commit_prefix || { say "could not commit skill edits; push skipped."; return 0; }
  checkout_clean || return 0
  [ "$(local_tree)" != "$(state_get tree)" ] || return 0        # nothing new here
  [ "$(local_tree)" != none ] || return 0
  if ! fetch_now; then
    if git ls-remote "$REMOTE" >/dev/null 2>&1; then
      # Reachable but branch missing: brand-new upstream, bootstrap it. A folder
      # that was never `subtree add`ed needs --rejoin to gain a merge base; one
      # that was cannot rejoin (unrelated histories) and records the base below.
      if has_squash_base; then
        if push_and_record; then
          say "bootstrapped upstream $BRANCH from $PREFIX"
        else
          [ "$?" -ne 2 ] || return 2
        fi
      elif git subtree push -q --prefix="$PREFIX" --rejoin -m "skills-sync: bootstrap upstream from $PREFIX" "$REMOTE" "$BRANCH" >/dev/null 2>&1 && fetch_now; then
        merge_remote || return $?
        say "bootstrapped upstream $BRANCH from $PREFIX"
      else
        say "bootstrap push failed; will retry next session."
      fi
    else
      say "upstream unreachable; push deferred."
    fi
    return 0
  fi
  merge_remote; local rc=$?
  [ "$rc" -eq 0 ] || return "$rc"
  checkout_clean || return 0
  [ "$(local_tree)" != "$(git rev-parse -q --verify "$(remote_sha)^{tree}")" ] || { state_set "$(local_tree)" "$(remote_sha)"; return 0; }
  push_and_record && say "pushed $PREFIX to upstream"
}

# Push the folder's history upstream, then record the new upstream head as the
# merge base for next time. Upstream can advance between push and fetch, so use
# the normal merge path and never record a failed merge as a successful sync.
push_and_record() {
  if git subtree push -q --prefix="$PREFIX" "$REMOTE" "$BRANCH" >/dev/null 2>&1 && fetch_now; then
    merge_remote
    return $?
  fi
  say "push to upstream failed; will retry next session."
  return 1
}

case "${1:-}" in
  --start|--stop|--merge|--push)
    operation_idle || exit 0
    ensure_remote || exit 0 ;;
esac

case "${1:-}" in
  --start)
    merge_remote; rc=$?
    fetch_bg
    exit "$rc" ;;
  --stop)
    push_local; exit $? ;;
  --fetch)  ensure_remote && fetch_now; exit 0 ;;
  --merge)  merge_remote; exit $? ;;
  --push)   push_local; exit $? ;;
  --status)
    printf 'prefix   %s\nremote   %s (%s)\nlocal    %s\nsynced   tree=%s remote=%s\nfetched  %s\nsquash   %s\n' \
      "$PREFIX" "$REMOTE" "$(git remote get-url "$REMOTE" 2>/dev/null)" "$(local_tree)" \
      "$(state_get tree)" "$(state_get remote)" "$(remote_sha)" \
      "$(has_squash_base && echo yes || echo no)"
    exit 0 ;;
  *) printf 'usage: %s --start|--stop|--fetch|--merge|--push|--status\n' "$0" >&2; exit 2 ;;
esac
