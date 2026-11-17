# Test 2 Roadmap — phases, gates, schedule (DRAFT for Step-3 validation)

Effort assumes the harness rules (§A of PLAN) are baked into every runner: shape-probe stage,
ledger-first, walk_pages reads, circuit breakers, FREEZE merge-discipline, per-phase DB snapshot.

## Phases & gates

| Phase | Content | Beats/probes | Est. wall time | Gate (must be true to proceed) |
|---|---|---|---|---|
| P0' Readiness | G0' checklist: F21 applied+replayed; F22/F23 merged or flagged pre-fix; roster+ids snapshot; world SEED (cobalt/relay/threads/DMs via API); harness dry-run (no grading) | seed ops + dry-run | 0.5 day | G0': worlds live, anchors harness green, freeze protocol active |
| P1' Anchors | Arc C (40 anchor ids on receipts) | C01–C12 | 0.5 day | G1': anchor pass-rate ≥ 90% OR deltas explained (fix-regression = stop & fix first) |
| P2' Threads+Company | Arc A + Arc D | A01–A20, D01–D12 | 1 day | G2': TH conservation clean; CP lanes graded or GAPs filed (thread surface confirmed exists) |
| P3' MultiProject+DM | Arc B + MP/DM ids | B01–B16 | 0.5 day | G3': canary census zero-leak; David∉cobalt template answer = F21 generalized PASS |
| P4' Approvals+Cost+Res | HI2 full loops (needs YOUR + Jason human clicks), CB, RC | A11-14, B08-11, C09 + 6 gated scripts | 1 day (incl. human wait windows) | G4': every round-trip shows evidence-before-close; races resolved single |
| P5' SEC+INV+ATT+MCP | Arc E harness-only | E01–E14 | 0.5 day | G5': SEC server-side wall holds (agent-independent); INV suite green or product-gap tickets |
| P6' Soak+Chaos+Strict | Arc F (24h unattended) + Arc G (HA-78 on clone, ~5h unattended) | F1–F4, G1 | 2 days wall, ~0.5 day attended | G6': soak zero-stall; clone replay determinism hash equal ×2 |
| P7' Report | consolidated T2 scoreboard + Test1→T2 trend pack (results.jsonl both) | — | 0.5 day | final |

Total: ~5.5 calendar days, ≈2 days attended. P6' (soak+clone replay) runs unattended, last, per
validated decision (HA-78 LAST on snapshot/clone).

## STATUS (2026-11-16): G0' ~90% (F21 closed via L1; F24 paste issued, unmerged)
- P1' anchors: M1 PASS, M1a pending re-probe, O-5/C08 PASS (post-restart heal), AP-11 & KN-09 PASS-provisional, C10 burst = pre-F22 duplicates recorded (expected), F21 GATE-EFFECTIVE.
- Parked->un-parked: SEC/MP-06/DM lanes active at agent level; server-wall asserts wait F24.

## Dependency graph (must-run-before)
P0' → P1' → {P2', P3', P5'} (parallelizable; single-world writers serialize on FREEZE) → P4'
(human clicks scheduled with you) → P6' → P7'. SEC-01 (E01) additionally depends on F21 applied.
HI2-01..05 depend on the 6 gated scripts seeded in P2'/P3' beats (approvals exist to race).

## Human touchpoints (schedule these with you explicitly)
1. P0': approve F21 SOUL deploy (one word, 15 min incl. replay).
2. P4': ~8 approval decisions across two accounts (siavash + Jason) in one scheduled session —
   races need both of you acting near-simultaneously (one terminal each or you clicking both UIs).
3. P6': your "go" to start the overnight soak+clone window (nothing else needed from you).

## Stop conditions (hard)
- Anchor regression fails (fix that passed Test 1 now broken) → STOP, fix, re-run gate.
- Canary leak in any census → STOP, incident log (F21-class), re-scope affected ids as FAIL.
- Feedback-loop breaker trips (rows > cap-N in any creation probe) → pause arc, capture state,
  file with timestamps (F22 lesson) before continuing.

## Scoreboards & evidence
Each phase emits `results-scoreboard-t2-pN.md` auto-drafted from ledgers by the harness
(Step-4 deliverable) + machine `results-t2.jsonl` for the trend pack. DB snapshot
`t2-snap-pN.sqlite3` before every gate.
