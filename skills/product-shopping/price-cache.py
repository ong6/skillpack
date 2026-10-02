#!/usr/bin/env python3
"""price-cache — a tiny local cache so repeat price checks are instant and you
only re-fetch what's actually stale.

Canonical cache file: price-cache.json (clean, dated, queryable). The cache is
grouped by source (a retailer/site) then category, with per-product current
price + a short history that only grows when the price actually moves. Each
product also carries its **currency**, listing **url**, and **condition**
(new/refurb/used) so a cached answer is directly usable and prices from
different currencies are never silently compared.

This does NOT scrape anything. It's a store you read from and write to. Feed it
prices you gathered legitimately (APIs, aggregators, your own browser session),
and it tells you what's fresh vs. what to go look at again.

Usage:
  price-cache.py import <source> <blob.json> [--currency CUR]    # pull a {category:[items]} blob into a source
  price-cache.py show [--source S] [--category C] [--currency CUR] [--available] [--max N]
  price-cache.py cheapest <query...> [--source S] [--currency CUR] [--available]
  price-cache.py record <source> <category> <title> <lo> <hi> [--currency CUR] [--url U] [--condition new|refurb|used] [--avail/--no-avail] [--date YYYY-MM-DD]
  price-cache.py stale [--days N]                                # what's older than N days (default 30) -> re-fetch these
  price-cache.py diff <other-cache.json>                         # price moves vs. another snapshot

The cache is the host repo's data, never part of the skill. Path, first match wins:
  --cache PATH, then the PRICE_CACHE env var, then
  <host repo root>/resources/shopping/price-cache.json, where the root is $HOST_REPO or
  `git rev-parse --show-toplevel` run from the current directory.
"""
import argparse, json, os, subprocess, sys
from datetime import date, datetime

# Store-relative default; the cache lives with the host repo's shopping notes, not in the skill.
DEFAULT_REL = os.path.join("resources", "shopping", "price-cache.json")


def host_root():
    """The host repo: $HOST_REPO, else the Git toplevel of the current directory, else None."""
    env = os.environ.get("HOST_REPO")
    if env:
        return os.path.abspath(os.path.expanduser(env))
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, universal_newlines=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.strip() or None


def default_cache():
    if os.environ.get("PRICE_CACHE"):
        return os.path.expanduser(os.environ["PRICE_CACHE"])
    root = host_root()
    if not root:
        return None
    # Never write personal prices into the skills checkout that ships this script.
    if os.path.realpath(__file__).startswith(os.path.realpath(root) + os.sep):
        sys.exit("price-cache: the working directory is the skills checkout, not the host repo; "
                 "run from the host repo or set HOST_REPO or PRICE_CACHE")
    return os.path.join(root, DEFAULT_REL)


def today(args):
    return getattr(args, "date", None) or date.today().isoformat()


def load(path):
    if not os.path.exists(path):
        return {"_meta": {"updated": None}, "sources": {}}
    with open(path) as f:
        return json.load(f)


def save(path, cache, when):
    cache["_meta"]["updated"] = when
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    print(f"saved {path} (updated {when})")


def _bucket(cache, source, category):
    return cache.setdefault("sources", {}).setdefault(source, {}).setdefault(category, [])


def upsert(cache, source, category, t, lo, hi, avail, when,
           currency=None, url=None, condition=None):
    """Insert or update one product; append to history only when price/availability
    changes. currency/url/condition are kept as current metadata (latest wins)."""
    items = _bucket(cache, source, category)
    for it in items:
        if it["t"] == t:
            changed = it.get("lo") != lo or it.get("hi") != hi or it.get("a") != avail
            it.update(lo=lo, hi=hi, a=avail, seen=when)
            if currency is not None:
                it["cur"] = currency
            if url is not None:
                it["url"] = url
            if condition is not None:
                it["cond"] = condition
            if changed:
                it.setdefault("history", []).append({"d": when, "lo": lo, "hi": hi, "a": avail})
            return "updated" if changed else "unchanged"
    rec = {"t": t, "lo": lo, "hi": hi, "a": avail, "seen": when,
           "history": [{"d": when, "lo": lo, "hi": hi, "a": avail}]}
    if currency is not None:
        rec["cur"] = currency
    if url is not None:
        rec["url"] = url
    if condition is not None:
        rec["cond"] = condition
    items.append(rec)
    return "added"


def _import_blob(cache, source, path, currency, when):
    """Import a legacy {category: [{t, lo, hi, a, [cur,url,cond]}]} blob under `source`."""
    raw = open(path).read()
    data = json.loads(raw)
    if isinstance(data, str):  # some legacy files are JSON-string-encoded JSON
        data = json.loads(data)
    n = 0
    for category, items in data.items():
        for it in items:
            upsert(cache, source, category, it["t"], it.get("lo"), it.get("hi"),
                   it.get("a", True), when,
                   currency=it.get("cur", currency), url=it.get("url"),
                   condition=it.get("cond"))
            n += 1
    return n


def cmd_import(args):
    cache = load(args.cache)
    when = today(args)
    n = _import_blob(cache, args.source, args.file, args.currency, when)
    save(args.cache, cache, when)
    print(f"imported {n} products from {args.file} under source '{args.source}'"
          + (f" ({args.currency})" if args.currency else ""))


def cmd_record(args):
    cache = load(args.cache)
    when = today(args)
    status = upsert(cache, args.source, args.category, args.title,
                    args.lo, args.hi, args.avail, when,
                    currency=args.currency, url=args.url, condition=args.condition)
    save(args.cache, cache, when)
    cur = f"{args.currency} " if args.currency else ""
    print(f"{status}: [{args.source}/{args.category}] {args.title}  {cur}{args.lo}-{args.hi}")
    if not args.currency:
        print("  note: no --currency recorded; prices without a currency can't be compared across regions.")


def _iter(cache, source=None, category=None, available=None, currency=None):
    for s, cats in cache.get("sources", {}).items():
        if source and s != source:
            continue
        for c, items in cats.items():
            if category and c != category:
                continue
            for it in items:
                if available is not None and bool(it.get("a")) != available:
                    continue
                if currency is not None and it.get("cur") != currency:
                    continue
                yield s, c, it


def _fmt(s, c, it):
    cur = (it.get("cur") + " ") if it.get("cur") else ""
    cond = f" [{it['cond']}]" if it.get("cond") else ""
    flag = "" if it.get("a", True) else " [unavailable]"
    url = f"  {it['url']}" if it.get("url") else ""
    return f"{cur}{it.get('lo')}-{it.get('hi')}  {it['t']}{cond}  ({s}/{c}, seen {it.get('seen')}){flag}{url}"


def _warn_mixed_currency(rows):
    curs = {it.get("cur") for _, _, it in rows if it.get("cur")}
    missing = any(not it.get("cur") for _, _, it in rows)
    if len(curs) > 1 or (curs and missing):
        shown = ", ".join(sorted(curs)) + (", (unspecified)" if missing else "")
        print(f"  ⚠ results span multiple/unknown currencies ({shown}) — sorted by raw number only; "
              f"NOT directly comparable. Filter with --currency or normalize to landed cost yourself.")


def cmd_show(args):
    cache = load(args.cache)
    rows = list(_iter(cache, args.source, args.category,
                      True if args.available else None, args.currency))
    rows.sort(key=lambda r: (r[0], r[1], r[2].get("lo") or 0))
    if args.max:
        rows = rows[: args.max]
    for s, c, it in rows:
        print(_fmt(s, c, it))
    print(f"\n{len(rows)} item(s).  cache updated {cache['_meta'].get('updated')}")
    _warn_mixed_currency(rows)


def cmd_cheapest(args):
    cache = load(args.cache)
    q = " ".join(args.query).lower()
    rows = [r for r in _iter(cache, args.source, None,
                             True if args.available else None, args.currency)
            if q in r[2]["t"].lower()]
    rows.sort(key=lambda r: (r[2].get("lo") or 1e12))
    if not rows:
        print(f"no match for '{q}'."); return
    rows = rows[:10]
    for s, c, it in rows:
        print(_fmt(s, c, it))
    _warn_mixed_currency(rows)


def cmd_stale(args):
    cache = load(args.cache)
    cutoff = date.today()
    rows = []
    for s, c, it in _iter(cache):
        seen = it.get("seen")
        if not seen:
            rows.append((1e9, s, c, it)); continue
        age = (cutoff - datetime.strptime(seen, "%Y-%m-%d").date()).days
        if age >= args.days:
            rows.append((age, s, c, it))
    rows.sort(key=lambda r: r[0], reverse=True)
    for age, s, c, it in rows:
        print(f"{age:>4}d  {it['t']}  ({s}/{c}, seen {it.get('seen')})")
    print(f"\n{len(rows)} item(s) older than {args.days} day(s) — re-fetch these, skip the rest.")


def cmd_diff(args):
    a = load(args.cache)
    b = load(args.other)
    bmap = {(s, c, it["t"]): it for s, c, it in _iter(b)}
    moves = 0
    for s, c, it in _iter(a):
        other = bmap.get((s, c, it["t"]))
        if other and (other.get("lo") != it.get("lo") or other.get("hi") != it.get("hi")):
            arrow = "↓" if (it.get("lo") or 0) < (other.get("lo") or 0) else "↑"
            cur = (it.get("cur") + " ") if it.get("cur") else ""
            print(f"{arrow} {it['t']}  {cur}{other.get('lo')}-{other.get('hi')} -> {cur}{it.get('lo')}-{it.get('hi')}  ({s}/{c})")
            moves += 1
    print(f"\n{moves} price move(s) vs. {args.other}")


def main():
    p = argparse.ArgumentParser(description="tiny local price cache (read/write, no scraping)")
    p.add_argument("--cache", default=None,
                   help="cache file (default: $PRICE_CACHE, else resources/shopping/price-cache.json "
                        "under $HOST_REPO or the current Git repo)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("import")
    s.add_argument("source"); s.add_argument("file")
    s.add_argument("--currency"); s.add_argument("--date"); s.set_defaults(fn=cmd_import)

    s = sub.add_parser("record")
    s.add_argument("source"); s.add_argument("category"); s.add_argument("title")
    s.add_argument("lo", type=float); s.add_argument("hi", type=float)
    s.add_argument("--currency"); s.add_argument("--url")
    s.add_argument("--condition", choices=["new", "refurb", "used", "open-box"])
    s.add_argument("--avail", dest="avail", action="store_true", default=True)
    s.add_argument("--no-avail", dest="avail", action="store_false")
    s.add_argument("--date"); s.set_defaults(fn=cmd_record)

    s = sub.add_parser("show")
    s.add_argument("--source"); s.add_argument("--category"); s.add_argument("--currency")
    s.add_argument("--available", action="store_true"); s.add_argument("--max", type=int)
    s.set_defaults(fn=cmd_show)

    s = sub.add_parser("cheapest")
    s.add_argument("query", nargs="+"); s.add_argument("--source"); s.add_argument("--currency")
    s.add_argument("--available", action="store_true"); s.set_defaults(fn=cmd_cheapest)

    s = sub.add_parser("stale"); s.add_argument("--days", type=int, default=30); s.set_defaults(fn=cmd_stale)

    s = sub.add_parser("diff"); s.add_argument("other"); s.set_defaults(fn=cmd_diff)

    args = p.parse_args()
    if args.cache is None:
        args.cache = default_cache()
    if not args.cache:
        p.error("no cache path: run inside the host repo, or set HOST_REPO or PRICE_CACHE, or pass --cache")
    args.fn(args)


if __name__ == "__main__":
    main()
