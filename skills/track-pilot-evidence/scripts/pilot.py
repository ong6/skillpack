#!/usr/bin/env python3
"""Check a pilot record, tie agent proposals to their inputs, record human reviews, write handovers.

  python3 pilot.py check    PILOT_DIR [--customer] [--today YYYY-MM-DD]
  python3 pilot.py propose  PILOT_DIR (--criterion ID | --decision) --outcome X --actor NAME --rationale TEXT [--conditions TEXT]
  python3 pilot.py record   PILOT_DIR (--criterion ID | --decision) --outcome X --reviewer NAME --rationale TEXT [--date D] [--conditions TEXT] [--visibility customer]
  python3 pilot.py handover PILOT_DIR --out FILE.md [--today YYYY-MM-DD]

PILOT_DIR holds pilot.json and its attachments. `record` is for a person at a terminal: it refuses
without an interactive TTY and asks the reviewer to type their name. Stdlib only, Python 3.7+.
Exit codes: 0 ready or done, 1 warnings, 2 invalid record or refused.
"""
import argparse
import copy
import datetime
import hashlib
import json
import os
import sys

CRITERION_OUTCOMES = ("met", "unmet", "blocked")
DECISION_OUTCOMES = ("proceed", "hold", "stop")
SECTIONS = ("criteria", "evidence", "attachments", "risks", "decisions", "checklist", "proposals", "reviews")
DEFINITION = ("id", "name", "metric", "baseline", "threshold", "target_date", "owner", "visibility")


class Invalid(Exception):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def by_id(records):
    return sorted(records, key=lambda r: r["id"])


def load(pilot_dir):
    path = os.path.join(pilot_dir, "pilot.json")
    with open(path, encoding="utf-8") as handle:
        pilot = json.load(handle)
    if pilot.get("version") != 1:
        raise Invalid("pilot.json needs \"version\": 1")
    pilot.setdefault("charter", {})
    for section in SECTIONS:
        pilot.setdefault(section, [])
    ids = set()
    for section in SECTIONS:
        for record in pilot[section]:
            if record.get("id") in ids or not record.get("id"):
                raise Invalid("%s: missing or duplicate id %r" % (section, record.get("id")))
            ids.add(record["id"])
            if section not in ("proposals",) and record.get("visibility", "internal") not in ("internal", "customer"):
                raise Invalid("%s: visibility must be internal or customer" % record["id"])
    criteria = {c["id"] for c in pilot["criteria"]}
    for c in pilot["criteria"]:
        missing = [k for k in DEFINITION[1:7] if not str(c.get(k, "")).strip()]
        if missing:
            raise Invalid("%s: criterion needs %s" % (c["id"], ", ".join(missing)))
    for record in pilot["criteria"] + pilot["evidence"]:
        day = record.get("target_date" if record in pilot["criteria"] else "collected", "")
        try:
            datetime.date.fromisoformat(day)
        except (TypeError, ValueError):
            raise Invalid("%s: dates are YYYY-MM-DD (target_date, collected)" % record["id"])
        if record in pilot["evidence"] and not 1 <= record.setdefault("stale_after_days", 30) <= 3650:
            raise Invalid("%s: stale_after_days must be 1-3650" % record["id"])
    for section in ("evidence", "risks", "decisions"):
        for record in pilot[section]:
            unknown = set(record.get("criteria", [])) - criteria
            if unknown:
                raise Invalid("%s links to missing criteria: %s" % (record["id"], ", ".join(sorted(unknown))))
    evidence = {e["id"] for e in pilot["evidence"]}
    for a in pilot["attachments"]:
        if a.get("evidence") not in evidence:
            raise Invalid("%s: attachment links to missing evidence" % a["id"])
    for r in pilot["proposals"] + pilot["reviews"]:
        allowed = CRITERION_OUTCOMES if r.get("kind") == "criterion" else DECISION_OUTCOMES
        if r.get("kind") not in ("criterion", "decision") or r.get("outcome") not in allowed:
            raise Invalid("%s: kind must be criterion or decision with a matching outcome" % r["id"])
    return pilot


def save(pilot_dir, pilot):
    path = os.path.join(pilot_dir, "pilot.json")
    temp = path + ".tmp"
    with open(temp, "w", encoding="utf-8") as handle:
        json.dump(pilot, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    os.replace(temp, path)


def customer_view(pilot):
    """Customer-visible records only; review hashes swapped for the ones taken over this view."""
    view = copy.deepcopy(pilot)
    view["charter"].pop("internal_notes", None)
    view["proposals"] = []
    view["criteria"] = [c for c in view["criteria"] if c.get("visibility") == "customer"]
    shown = {c["id"] for c in view["criteria"]}
    for section in ("evidence", "risks", "decisions"):
        view[section] = [dict(r, criteria=[k for k in r.get("criteria", []) if k in shown])
                         for r in view[section] if r.get("visibility") == "customer"]
    view["checklist"] = [r for r in view["checklist"] if r.get("visibility") == "customer"]
    evidence = {e["id"] for e in view["evidence"]}
    view["attachments"] = [a for a in view["attachments"]
                           if a.get("visibility") == "customer" and a["evidence"] in evidence]
    view["reviews"] = [dict(r, fingerprint=r.get("customer_fingerprint")) for r in view["reviews"]
                       if (r["kind"] == "criterion" and r.get("criterion") in shown)
                       or (r["kind"] == "decision" and r.get("visibility") == "customer")]
    return view


def criterion_inputs(pilot, cid):
    criterion = next((c for c in pilot["criteria"] if c["id"] == cid), None)
    if criterion is None:
        raise Invalid("criterion %s is not in this view" % cid)
    evidence = by_id(dict(e, criteria=sorted(e.get("criteria", [])))
                     for e in pilot["evidence"] if cid in e.get("criteria", []))
    linked = {e["id"] for e in evidence}
    return {"criterion": {k: criterion.get(k) for k in DEFINITION}, "evidence": evidence,
            "attachments": by_id(a for a in pilot["attachments"] if a["evidence"] in linked)}


def decision_inputs(pilot):
    judged = [{k: r.get(k) for k in ("id", "criterion", "outcome", "reviewer", "rationale", "date")}
              for r in pilot["reviews"] if r["kind"] == "criterion"]
    snapshot = {section: by_id(pilot[section]) for section in
                ("criteria", "evidence", "attachments", "risks", "decisions", "checklist")}
    snapshot.update(charter=pilot["charter"], criterion_reviews=judged)
    return snapshot


def fingerprint(pilot, cid=None):
    return sha256(canonical(criterion_inputs(pilot, cid) if cid else decision_inputs(pilot)).encode())


def latest_review(pilot, cid):
    reviews = [r for r in pilot["reviews"] if r["kind"] == "criterion" and r.get("criterion") == cid]
    return reviews[-1] if reviews else None


def attachment_health(pilot_dir, a):
    root = os.path.realpath(pilot_dir)
    path = os.path.join(root, a.get("path", ""))
    real = os.path.realpath(path)
    if os.path.islink(path) or os.path.commonpath([root, real]) != root:
        return "unsafe path"
    if not os.path.isfile(real):
        return "missing"
    with open(real, "rb") as handle:
        data = handle.read()
    return "ok" if sha256(data) == a.get("sha256") and len(data) == a.get("bytes") else "changed"


def age(today, day):
    return (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(day)).days


def assess(pilot, pilot_dir, today):
    """Return (warnings, rows): readiness warnings and one status row per criterion."""
    warnings, rows = [], []
    health = {a["id"]: attachment_health(pilot_dir, a) for a in pilot["attachments"]}
    charter = pilot["charter"]
    if not all(charter.get(k) for k in ("customer", "title", "objective", "owners", "start", "end")):
        warnings.append("charter: complete customer, title, objective, owners, start and end")
    if not pilot["criteria"]:
        warnings.append("no success criteria defined")
    fresh = lambda e: 0 <= age(today, e["collected"]) <= e.get("stale_after_days", 30)
    for c in pilot["criteria"]:
        review = latest_review(pilot, c["id"])
        status = review["outcome"] if review else "unassessed"
        freshness = "-" if not review else (
            "current" if review.get("fingerprint") == fingerprint(pilot, c["id"]) else "changed")
        linked = [e for e in pilot["evidence"] if c["id"] in e.get("criteria", [])]
        files = [a for a in pilot["attachments"] if a["evidence"] in {e["id"] for e in linked}]
        passing = (status == "met" and freshness == "current" and linked and all(map(fresh, linked))
                   and all(health[a["id"]] == "ok" for a in files))
        rows.append((c, status, freshness, bool(passing), len(linked)))
        if status != "met":
            warnings.append("%s: %s" % (c["id"], status))
        if freshness == "changed":
            warnings.append("%s: inputs changed since the %s review; needs re-review" % (c["id"], status))
        if not linked:
            warnings.append("%s: no linked evidence" % c["id"])
        if c["target_date"] < today and not passing:
            warnings.append("%s: target date %s has passed" % (c["id"], c["target_date"]))
    for e in pilot["evidence"]:
        if age(today, e["collected"]) < 0:
            warnings.append("%s: collected date is in the future" % e["id"])
        elif not fresh(e):
            warnings.append("%s: stale (%d days old)" % (e["id"], age(today, e["collected"])))
        if not e.get("criteria"):
            warnings.append("%s: not linked to a criterion" % e["id"])
    for a in pilot["attachments"]:
        if health[a["id"]] != "ok":
            warnings.append("%s: attachment %s (%s)" % (a["id"], health[a["id"]], a.get("path")))
    for r in pilot["risks"]:
        if r.get("status") in ("open", "accepted"):
            warnings.append("%s: %s %s risk" % (r["id"], r.get("severity", "?"), r["status"]))
    if not pilot["checklist"]:
        warnings.append("no handover checklist defined")
    for item in pilot["checklist"]:
        if not item.get("done"):
            warnings.append("%s: handover item open%s" % (item["id"], " and overdue" if item.get("due", "9") < today else ""))
    for d in (r for r in pilot["reviews"] if r["kind"] == "decision"):
        if d.get("fingerprint") != fingerprint(pilot):
            warnings.append("%s: %s decision of %s reviewed a pilot that has since changed" % (
                d["id"], d["outcome"], d.get("date")))
    return warnings, rows


def cmd_check(args):
    pilot = load(args.pilot_dir)
    view = customer_view(pilot) if args.customer else pilot
    warnings, rows = assess(view, args.pilot_dir, args.today)
    print("%s view, %s" % ("customer" if args.customer else "full", args.today))
    for c, status, freshness, passing, count in rows:
        print("  %-22s %-10s review %-8s evidence %d  current pass: %s" % (
            c["id"], status, freshness, count, "yes" if passing else "no"))
    for p in view["proposals"]:
        target = p.get("criterion") or "pilot"
        state = "current" if p["fingerprint"] == fingerprint(view, p.get("criterion")) else "inputs changed"
        print("  proposal %s: %s proposes %s for %s (%s; not a review)" % (
            p["id"], p["actor"], p["outcome"], target, state))
    for w in warnings:
        print("WARN  " + w)
    print("ready for human review" if not warnings else "%d warnings" % len(warnings))
    return 0 if not warnings else 1


def target(args, pilot):
    if args.decision == bool(args.criterion):
        raise Invalid("pass exactly one of --criterion ID or --decision")
    if args.criterion and args.criterion not in {c["id"] for c in pilot["criteria"]}:
        raise Invalid("unknown criterion %s" % args.criterion)
    allowed = DECISION_OUTCOMES if args.decision else CRITERION_OUTCOMES
    if args.outcome not in allowed:
        raise Invalid("outcome must be one of " + ", ".join(allowed))
    return ("decision", None) if args.decision else ("criterion", args.criterion)


def cmd_propose(args):
    pilot = load(args.pilot_dir)
    kind, cid = target(args, pilot)
    inputs = criterion_inputs(pilot, cid) if cid else decision_inputs(pilot)
    proposal = {"id": "p-%d" % (len(pilot["proposals"]) + 1), "kind": kind, "criterion": cid,
                "outcome": args.outcome, "actor": args.actor, "rationale": args.rationale,
                "conditions": args.conditions, "visibility": "internal",
                "created": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                "fingerprint": fingerprint(pilot, cid)}
    pilot["proposals"].append(proposal)
    save(args.pilot_dir, pilot)
    reviewed = [r["id"] for key in ("evidence", "attachments") for r in inputs.get(key, [])] if cid else ["whole pilot"]
    print("proposal %s recorded (internal, not a review); inputs: %s; fingerprint %s" % (
        proposal["id"], ", ".join(reviewed) or "none", proposal["fingerprint"][:12]))
    return 0


def cmd_record(args):
    pilot = load(args.pilot_dir)
    kind, cid = target(args, pilot)
    if not sys.stdin.isatty():
        raise Invalid("record needs a person at an interactive terminal; agents propose instead")
    typed = input("Recording a human %s review: %s for %s. Type your reviewer name to confirm: " % (
        kind, args.outcome, cid or "the pilot")).strip()
    if typed != args.reviewer:
        raise Invalid("name did not match --reviewer; nothing recorded")
    visible = cid and next(c for c in pilot["criteria"] if c["id"] == cid).get("visibility") == "customer"
    view = customer_view(pilot)
    review = {"id": "rv-%d" % (len(pilot["reviews"]) + 1), "kind": kind, "criterion": cid,
              "outcome": args.outcome, "reviewer": args.reviewer, "rationale": args.rationale,
              "conditions": args.conditions, "date": args.date or args.today,
              "visibility": args.visibility if kind == "decision" else ("customer" if visible else "internal"),
              "fingerprint": fingerprint(pilot, cid),
              "customer_fingerprint": fingerprint(view, cid) if (visible or kind == "decision") else None}
    pilot["reviews"].append(review)
    save(args.pilot_dir, pilot)
    print("recorded %s (locally asserted human review, not authenticated sign-off)" % review["id"])
    return 0


def cmd_handover(args):
    if os.path.exists(args.out):
        raise Invalid("%s exists; choose a new file" % args.out)
    view = customer_view(load(args.pilot_dir))
    warnings, rows = assess(view, args.pilot_dir, args.today)
    ch = view["charter"]
    names = {c["id"]: c["name"] for c in view["criteria"]}
    links = lambda r: ", ".join(names[k] for k in r.get("criteria", [])) or "none"
    out = ["# %s" % (ch.get("title") or "Pilot handover"), "",
           "%s · %s to %s · Owners: %s" % (ch.get("customer", "Customer not set"), ch.get("start", "?"),
                                           ch.get("end", "?"), ch.get("owners", "not set")), "",
           ch.get("objective", ""), "",
           "> Customer-visible records only. Evidence is not approval: each criterion needs an explicit "
           "review, and a historical review is not a current pass. %d of %d criteria are current passes."
           % (sum(1 for r in rows if r[3]), len(rows)), "", "## 1. Success criteria", ""]
    for c, status, freshness, passing, count in rows:
        review = latest_review(view, c["id"])
        out += ["### %s" % c["name"], "",
                "- Metric: %s · Baseline: %s · Threshold: %s · Target date: %s · Owner: %s" % (
                    c["metric"], c["baseline"], c["threshold"], c["target_date"], c["owner"]),
                "- Assessment: %s (review %s) · Current pass: %s" % (
                    status, freshness, "yes" if passing else "not established"),
                "- Reviewer: %s" % ("%s, %s: %s" % (review["reviewer"], review["date"], review["rationale"])
                                    if review else "awaiting explicit review"), ""]
    out += ["## 2. Evidence register", ""]
    for e in view["evidence"]:
        state = "stale, refresh required" if age(args.today, e["collected"]) > e.get("stale_after_days", 30) else "within freshness window"
        out += ["### %s" % e["name"], "", e.get("summary", ""), "",
                "- Source: %s · Owner: %s · Collected: %s (%s) · Criteria: %s" % (
                    e.get("source", "not given"), e.get("owner", "?"), e["collected"], state, links(e))]
        for a in (a for a in view["attachments"] if a["evidence"] == e["id"]):
            out.append("- Attachment `%s`, %s bytes, SHA-256 `%s` (%s)" % (
                os.path.basename(a["path"]), a.get("bytes"), a.get("sha256"), attachment_health(args.pilot_dir, a)))
        out.append("")
    out += ["## 3. Risks and mitigations", ""] + ["- **%s** (%s, %s): %s Mitigation: %s Owner: %s." % (
        r["name"], r.get("severity"), r.get("status"), r.get("detail", ""), r.get("mitigation", "none"),
        r.get("owner")) for r in view["risks"]] + ["", "## 4. Decisions", ""]
    decisions = [r for r in view["reviews"] if r["kind"] == "decision"]
    out += ["- **%s** by %s on %s (%s): %s%s" % (
        d["outcome"], d["reviewer"], d["date"],
        "current" if d.get("fingerprint") == fingerprint(view) else "pilot changed since; not current approval",
        d["rationale"], " Conditions: " + d["conditions"] if d.get("conditions") else "") for d in decisions]
    out += [] if decisions else ["- No customer-visible proceed, hold or stop decision has been recorded."]
    out += ["- %s (%s, %s): %s" % (d["name"], d.get("owner"), d.get("date"), d.get("detail", ""))
            for d in view["decisions"]] + ["", "## 5. Operational handover", ""]
    out += ["- [%s] %s. Owner: %s. Due: %s" % ("x" if i.get("done") else " ", i["name"], i.get("owner"), i.get("due"))
            for i in view["checklist"]] + ["", "## 6. Review notes", ""]
    out += ["- " + w for w in warnings] or ["- No automated warnings in the customer view. Human approval is still required."]
    out += ["", "_Prepared %s from customer-visible records. Visibility is filtering, not redaction: "
            "read every free-text field before sending._" % args.today, ""]
    with open(args.out, "x", encoding="utf-8") as handle:
        handle.write("\n".join(out))
    print("wrote %s (%d warnings in the customer view)" % (args.out, len(warnings)))
    return 0


def main():
    today = datetime.date.today().isoformat()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command")
    sub.required = True
    for name in ("check", "propose", "record", "handover"):
        p = sub.add_parser(name)
        p.add_argument("pilot_dir")
        p.add_argument("--today", default=today)
        if name in ("propose", "record"):
            p.add_argument("--criterion")
            p.add_argument("--decision", action="store_true")
            p.add_argument("--outcome", required=True)
            p.add_argument("--rationale", required=True)
            p.add_argument("--conditions", default="")
        if name == "propose":
            p.add_argument("--actor", required=True, help="which agent is proposing")
        if name == "record":
            p.add_argument("--reviewer", required=True)
            p.add_argument("--date")
            p.add_argument("--visibility", choices=("internal", "customer"), default="internal")
        if name == "check":
            p.add_argument("--customer", action="store_true", help="check only what the handover shows")
        if name == "handover":
            p.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        return {"check": cmd_check, "propose": cmd_propose, "record": cmd_record,
                "handover": cmd_handover}[args.command](args)
    except (Invalid, OSError, ValueError, KeyError) as error:
        print("error: %s" % error, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
