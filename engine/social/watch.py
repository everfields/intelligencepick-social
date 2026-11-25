"""The conditions that raise an alarm without a post failing: the runway, a batch left unrendered, a post with no outcome,
an enabled network that is not live, a network silent for silent_alarm_days, and an outside network's feed gone quiet.

Run after intake, after metrics and at the end of each publisher run. An alarm clears itself once its condition does.
"""

from __future__ import annotations

import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Callable

from .alarms import Alarms
from .config import Config
from .intake import runway
from .state import DRAFTED, HANDED, PROCESSING, PUBLISHED, PostLog, iso, parse_iso


REAL = (PUBLISHED, DRAFTED, PROCESSING, HANDED)


def real_post(r: dict[str, str]) -> bool:
    """A row that reached the network: a done status and no rehearsal's made-up id or link."""
    return r["status"] in REAL and r.get("remote_id") != "dry-post" and ".dry.run" not in r.get("url", "")


def silence(log: PostLog, cfg: Config, alarms: Alarms, now: datetime) -> tuple[list[str], dict[str, str]]:
    """While SOCIAL_CRON is live: an enabled network that is not live (its credentials are missing or empty) posts
    nothing, so it raises `not-ready-<net>` at once; an enabled network whose newest real post is older than
    silent_alarm_days raises `silent-<net>`, counted from its first row when it never posted. Neither waited for a person
    before (Intelligence Pick, 2026-11-25: TikTok dry for five days, found by the founder)."""
    not_ready, last = [], {}
    if cfg.cron != "live":
        return not_ready, last
    rows = log.rows()
    limit = timedelta(days=cfg.silent_alarm_days)
    for net in cfg.enabled():
        if not cfg.is_live(net.name):
            not_ready.append(net.name)
            alarms.raise_(f"not-ready-{net.name}", f"{net.name}: enabled but not live, nothing is posted",
                          f"SOCIAL_CRON is live and {net.name} is enabled in social.json, but it is not in the live set: "
                          f"its credentials are missing or empty (SOCIAL_READY_NETWORKS is built from the secrets and "
                          f"variables in the workflow). Set them again, or disable the network in social.json.", "high")
            continue
        alarms.clear(f"not-ready-{net.name}", f"{net.name} is live")
        mine = [r for r in rows if r["network"] == net.name]
        posted = sorted(t for t in (parse_iso(r["at"]) for r in mine if real_post(r)) if t)
        since = posted[-1] if posted else min((t for t in (parse_iso(r["at"]) for r in mine) if t), default=None)
        last[net.name] = iso(posted[-1]) if posted else ""
        if since and now - since > limit:
            alarms.raise_(f"silent-{net.name}", f"{net.name}: no post in {cfg.silent_alarm_days:g} days",
                          f"The newest real post on {net.name} is {last[net.name] or 'none (never posted)'}. Check the "
                          f"publisher's runs, the queue and the account.", "high")
        else:
            alarms.clear(f"silent-{net.name}", f"{net.name} posted {last[net.name]}")
    return not_ready, last


def read_feed(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (social watch)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def outside(cfg: Config, alarms: Alarms, now: datetime, fetch: Callable[[str], bytes] | None = None) -> dict:
    """Networks that post by another route (social.json `outside`: {"pinterest": {"feed": "<public RSS>"}}): the newest
    item of the account's own public feed, `silent-<net>` past silent_alarm_days, `unread-<net>` when the feed cannot be
    read (a feed the runner can't reach is itself a blind spot)."""
    if cfg.cron != "live":
        return {}
    fetch = fetch or read_feed
    out: dict = {}
    limit = timedelta(days=cfg.silent_alarm_days)
    for name, o in cfg.outside.items():
        url = str((o or {}).get("feed") or "")
        if not url:
            continue
        try:
            root = ET.fromstring(fetch(url))
            dates = [d for d in (pub_date(e.text or "") for e in root.iter("pubDate")) if d]
        except (OSError, ET.ParseError, ValueError) as e:
            out[name] = {"error": str(e)[:200]}
            alarms.raise_(f"unread-{name}", f"{name}: its public feed cannot be read", f"{url}: {str(e)[:300]}")
            continue
        alarms.clear(f"unread-{name}", "the feed was read")
        newest = max(dates, default=None)
        out[name] = {"newest": iso(newest) if newest else ""}
        if newest is None or now - newest > limit:
            alarms.raise_(f"silent-{name}", f"{name}: no post in {cfg.silent_alarm_days:g} days",
                          f"The newest item in {url} is {iso(newest) if newest else 'none'}. Check what feeds it.", "high")
        else:
            alarms.clear(f"silent-{name}", f"{name} posted {iso(newest)}")
    return out


def pub_date(s: str) -> datetime | None:
    try:
        d = parsedate_to_datetime(s.strip())
    except (TypeError, ValueError, IndexError):
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def check(root: Path, state_dir: Path, cfg: Config, alarms: Alarms, now: datetime,
          fetch: Callable[[str], bytes] | None = None) -> dict:
    log = PostLog(state_dir / "posts.csv")
    report: dict = {"runway": runway(root, cfg, log.used_ids(), now)}
    live = [n for n in cfg.enabled() if cfg.is_live(n.name)]
    for net in live:
        r = report["runway"][net.name]
        key = f"runway-{net.name}"
        if r["days"] < cfg.runway_alarm_days:
            alarms.raise_(key, f"{net.name}: {r['days']} days of posts left",
                          f"{r['posts']} checked posts wait for {net.name}, at {r['per_day']} a day: under "
                          f"{cfg.runway_alarm_days} days. Did the last render run? Did intake quarantine the batch? An empty "
                          f"queue goes quiet; it never reposts.")
        else:
            alarms.clear(key, f"{r['days']} days of runway")
    hb_file = root / "pc" / "heartbeat.json"
    hb = json.loads(hb_file.read_text(encoding="utf-8")) if hb_file.is_file() else {}
    at = parse_iso(str(hb.get("at", "")))
    report["heartbeat"] = hb.get("at", "")
    # The heartbeat moves only when a batch renders, so its age says nothing while every batch is rendered (a full
    # queue needs no new batch; the runway alarm covers a queue running out). It alarms only when a batch newer than
    # the last rendered week has waited past heartbeat_alarm_hours, or nothing ever rendered (Every Little Room's
    # false alarm fired three times, 2026-11-17 to 11-22, each costing an incident run).
    batch_dir = root / "batches"
    done_week = str(hb.get("week", ""))
    waiting = sorted(b.stem for b in batch_dir.glob("*.json") if b.stem > done_week) if batch_dir.is_dir() else []
    report["unrendered"] = waiting
    if live:
        age_h = (now - at).total_seconds() / 3600 if at else None
        if age_h is None or (waiting and age_h > cfg.heartbeat_alarm_hours):
            alarms.raise_("heartbeat", "a batch is waiting to render",
                          f"The last render was {hb.get('at') or 'never'} "
                          f"({'never' if age_h is None else f'{age_h:.0f} h ago'}, week {done_week or 'none'}) and "
                          f"{', '.join(waiting) or 'no batch'} is not rendered yet. Check the latest social-render run. "
                          f"Publishing carries on from the queue.")
        else:
            alarms.clear("heartbeat", f"heartbeat {hb.get('at')}, nothing waiting to render")
    report["not_ready"], report["last_post"] = silence(log, cfg, alarms, now)
    report["outside"] = outside(cfg, alarms, now, fetch)
    stuck = log.unresolved()
    report["unresolved"] = [f"{r['network']}/{r['id']}" for r in stuck]
    for r in stuck:
        alarms.raise_(f"unresolved-{r['network']}-{r['id']}", f"{r['network']}: a post has no outcome",
                      f"{r['id']} was being posted at {r['at']} and the run stopped before the answer. Check "
                      f"{r['network']}: if it is there, log it with `social resolve {r['network']} {r['id']} --url <link>`; "
                      f"if not, `--failed`. {r['network']} posts nothing until then.", "high")
    return report
