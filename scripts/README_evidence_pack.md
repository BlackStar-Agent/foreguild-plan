# Evidence pack — poidh base bounty 1531, claim 9457

Claim 9457 promises: *"Full data appendix + reproducible fetch scripts in the
repo."* This directory fulfills that promise.

## Contents

- `scripts/fetch_poidh_board.py` — re-derives the Poidh Base board
  enumeration published as Section 8 of the plan (snapshot taken
  2026-11-05/07 during the contest). Hits only poidh's public per-bounty
  data endpoint; read-only, no auth, refuses to run behind a proxy.
- `scripts/fetch_seer_markets.py` — depth summary of Seer's public
  markets-search endpoint (documented at docs.seer.pm/developers/api),
  supporting the liquidity-fallback design (plan Section 6 / v2 Section C,
  risk 2). Read-only, no auth, no proxy.
- `data/appendix_2026-11-05.json` — machine-readable copy of the Section 8
  data appendix numbers quoted in the plan. **This is the 2026-11-05/07
  snapshot the claim was judged against.**

## Honest snapshot policy

`data/appendix_2026-11-05.json` is the snapshot captured on 2026-11-05/07,
when the plan was written. A re-run of the scripts produces a **new**
snapshot of a living board: Poidh bounties open, close, and collect claims;
Seer markets are created and traded. Therefore **a re-run will not match the
appendix numbers exactly, and that is the expected, honest behavior** — the
difference is board evolution, not inconsistency. Every output file is
stamped with its `fetchedAtUTC`.

## Run

```
python3 scripts/fetch_poidh_board.py      # → data/poidh_board.json
python3 scripts/fetch_seer_markets.py     # → data/seer_depth.json
```

No dependencies beyond Python 3 stdlib. Direct connection required (the
scripts bypass proxy settings so a judge re-run exercises the same public
path we used).

## Verification run 2026-11-08

Both scripts were re-run from a clean directory on 2026-11-08, one day after
the plan was submitted:

- `fetch_poidh_board.py` (window 1500–1540): **41 bounties fetched,
  436 claims total, 18 of them in progress** on 11-08 — vs. the plan's
  19 open bounties enumerated on the visible board at capture. The board
  has visibly evolved in three days; both snapshots are preserved and
  dated.
- `fetch_seer_markets.py`: **548 conditional markets on Gnosis, median
  volume ≈ $7 on non-zero markets, only 5 markets > $10k** — matching the
  independent Seer-depth measurements published by competing entries, and
  supporting v1 §7's "thin markets govern by published defaults" design.
  On Base, all three Foreguild-named conditional markets created during
  this contest show volume and liquidity of $0 — thin depth is the norm,
  exactly the regime Foreguild's fallback design anticipates.

The 11-05/07 plan numbers and the 11-08 re-run outputs are both preserved:
`data/appendix_2026-11-05.json` (claim-time snapshot) alongside whatever a
fresh run of the scripts produces (current snapshot).
