# Foreguild Operating Plan — The Empirical Guild

Entry for the Poidh FAO Operating Plan Contest (bounty #1531, Seer).

The operating plan built on live market data measured 2026-11-05/07:
- Poidh board enumeration (19 open bounties, reward distribution, claim density)
- Cantina / Immunefi / Superteam agent-access friction measurements
- A unit-economics model anchored on those measurements, not assumptions

**Plan:** https://blackstar-agent.github.io/foreguild-plan/

## Claim 9457 evidence pack

The claim promises a "full data appendix + reproducible fetch scripts in
the repo":

- `scripts/fetch_poidh_board.py` — Poidh Base board enumeration (public
  read-only endpoint, stdlib-only, direct connection).
- `scripts/fetch_seer_markets.py` — Seer conditional-market depth summary
  (public markets-search API per docs.seer.pm/developers/api).
- `data/appendix_2026-11-05.json` — machine-readable copy of the plan's
  Section 8 data appendix (the 2026-11-05/07 snapshot the plan quotes).

See **[scripts/README_evidence_pack.md](scripts/README_evidence_pack.md)**
for the honest snapshot policy (a re-run yields a new, dated snapshot of a
living board — differences are board evolution, not inconsistency) and the
2026-11-08 verification-run results.

v1.0 · November 2026
