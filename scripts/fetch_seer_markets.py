#!/usr/bin/env python3
"""Foreguild operating plan (poidh base/1531, claim 9457) — evidence pack.

Depth summary of Seer's public market data, supporting the liquidity-fallback
design in plan Section 6 / v2 Section C (risk 2: "prediction markets too thin
to govern"). Read-only: POSTs the same markets-search endpoint the Seer web
app uses. No auth, no proxy — direct connection required.

Endpoint documented at https://docs.seer.pm/developers/api (Netlify Functions
reference; markets-search is POST with a JSON body).

Usage: python3 fetch_seer_markets.py [--out data/seer_depth.json] [--pages N]
"""
import argparse, gzip, json, os, statistics, sys, time, urllib.request

URL = "https://app.seer.pm/.netlify/functions/markets-search"
SOURCE_DOC = "https://docs.seer.pm/developers/api"
OUT_DEFAULT = "data/seer_depth.json"


def post(body, attempts=4):
    # The endpoint truncates large *uncompressed* responses mid-body;
    # requesting gzip makes transfers complete reliably. Retry with fresh
    # connections anyway. Direct connection only: bypass any inherited
    # proxy handler.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    last = None
    for i in range(attempts):
        req = urllib.request.Request(
            URL, data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json",
                     "Accept-Encoding": "gzip",
                     "User-Agent": "foreguild-plan-evidence/1.0"})
        try:
            with opener.open(req, timeout=120) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                return json.loads(raw.decode())
        except Exception as e:  # http.client.IncompleteRead, timeouts, …
            last = e
            time.sleep(2 * (i + 1))
    raise last


def usd(m, key):
    try:
        return float(m.get(key) or 0)
    except (TypeError, ValueError):
        return 0.0


def summarize(markets, label):
    vols = sorted(usd(m, "volumeUSD") for m in markets)
    nz = sorted(v for v in vols if v > 0)
    liqs = sorted(usd(m, "liquidityUSD") for m in markets)
    n = len(vols)
    return {
        "scope": label,
        "nMarkets": n,
        "medianVolumeUsd": round(statistics.median(vols), 4) if n else None,
        "medianVolumeUsdNonzero": round(statistics.median(nz), 4) if nz else None,
        "over10kVolume": sum(1 for v in vols if v > 10_000),
        "zeroVolume": sum(1 for v in vols if v == 0),
        "medianLiquidityUsd": round(statistics.median(liqs), 4) if n else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT_DEFAULT)
    args = ap.parse_args()

    # Per-chain requests keep each response small enough to survive the
    # flaky large-response truncation. The `count` field gives the true
    # total per chain, so coverage is reported honestly. Optimism (10)
    # routinely fails mid-body even gzipped; it is optional.
    markets = []
    chains = {}
    counts = {}
    errors = {}
    for chain in ("8453", "100", "10"):
        try:
            d = post({"chainsList": [chain], "showConditionalMarkets": True,
                      "limit": 1000})
            batch = d.get("markets") or []
            counts[chain] = d.get("count")
            chains[chain] = batch
            markets.extend(batch)
            time.sleep(1.0)
        except Exception as e:
            errors[chain] = repr(e)
            print(f"chain {chain}: error {e!r}", file=sys.stderr)

    # Per-chain views (Seer runs on Gnosis 100, Optimism 10, Base 8453).
    chains = {}
    for m in markets:
        chains.setdefault(str(m.get("chainId")), []).append(m)

    summary = {
        "endpoint": URL,
        "doc": SOURCE_DOC,
        "note": ("supports the liquidity-fallback design (plan Section 6, "
                 "v2 Section C risk 2). Conditional markets only — the type "
                 "Foreguild's five governing markets would use. Thin depth "
                 "is the expected, measured result; published defaults "
                 "govern whenever volume is below the floor."),
        "fetchedAtUTC": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "serverCountPerChain": counts,
        "fetchErrors": errors,
        "overallConditional": summarize(markets, "all chains, conditional"),
        "byChain": {c: summarize(ms, f"chain {c}") for c, ms in sorted(chains.items())},
    }
    # Base detail: the contest chain — small N, show it raw.
    base = chains.get("8453") or []
    fg = [m for m in base if "foreguild" in (m.get("marketName") or "").lower()]
    summary["baseDetail"] = {
        "nConditional": len(base),
        "foreguildNamedMarkets": [
            {"name": m.get("marketName"), "volumeUSD": m.get("volumeUSD"),
             "liquidityUSD": m.get("liquidityUSD")} for m in fg],
    }

    outdir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(outdir, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
