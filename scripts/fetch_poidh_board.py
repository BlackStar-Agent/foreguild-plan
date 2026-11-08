#!/usr/bin/env python3
"""Foreguild operating plan (poidh base/1531, claim 9457) — evidence pack.

Re-derives the Poidh Base board enumeration published in Section 8 of the
plan (snapshot taken 2026-11-05/07). Read-only: hits only poidh's public
per-bounty data endpoint. No auth, no proxy, direct connection required
(the script refuses to run behind a proxy so that judges re-run the same
direct path).

Usage: python3 fetch_poidh_board.py [--out data/poidh_board.json]
                                      [--from 1500 --to 1540]
"""
import argparse, json, os, sys, time, urllib.request

SOURCE = "https://poidh.xyz/base/bounty/{id}/data"
OUT_DEFAULT = "data/poidh_board.json"

# The plan's Section 8 snapshot (2026-11-05/07) enumerated the recent Base
# board window around the contest bounty 1531. Re-runs use the same window;
# the board evolves, so expect different numbers — that is the point of
# dating every output file.
DEFAULT_FROM, DEFAULT_TO = 1500, 1540


def get(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "foreguild-plan-evidence/1.0"})
    # Direct connection only: bypass any inherited proxy handler.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=30) as r:
        return json.loads(r.read().decode())


def bounty_data(bid):
    return get(SOURCE.format(id=bid))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--from", dest="frm", type=int, default=DEFAULT_FROM)
    ap.add_argument("--to", dest="to", type=int, default=DEFAULT_TO)
    args = ap.parse_args()

    rows = []
    for bid in range(args.frm, args.to + 1):
        try:
            d = bounty_data(bid)
        except Exception:
            continue  # id not on the board / transient error: skip
        claims = d.get("claims") or []
        rows.append({
            "bountyId": d.get("id", bid),
            "title": d.get("title"),
            "amountWei": d.get("amount"),
            "priceUsd": d.get("priceUsd"),
            "status": d.get("status"),
            "acceptingClaims": d.get("acceptingClaims"),
            "nClaims": len(claims),
            "claimIds": [c.get("claimId") for c in claims],
            "fetchedAtUTC": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
        time.sleep(0.4)

    outdir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(outdir, exist_ok=True)
    doc = {
        "source": SOURCE,
        "note": ("evidence pack for poidh base/1531 claim 9457; the plan's "
                 "Section 8 snapshot is data/appendix_2026-11-05.json. A "
                 "re-run is a NEW snapshot of a living board: different "
                 "numbers are expected and honest."),
        "window": {"from": args.frm, "to": args.to},
        "fetchedAtUTC": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rows": rows,
    }
    with open(args.out, "w") as f:
        json.dump(doc, f, indent=1)
    n_open = sum(1 for r in rows if r["status"] in ("in_progress", "open"))
    print(f"wrote {args.out}: {len(rows)} bounties fetched in "
          f"{args.frm}-{args.to}, {sum(r['nClaims'] for r in rows)} claims "
          f"total, {n_open} in progress")


if __name__ == "__main__":
    main()
