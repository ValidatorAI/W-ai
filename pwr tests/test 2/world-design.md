# Test 2 — World Design (Step 2 DRAFT for validation)

Grounded in live roster (2026-11-16): humans role=1 — siavash(1), David(8), Jason(9); bots role=2 —
w-ai(2), Coder(3), Market Research(4), Business Analyst(5), Project Manager(6), Bender Bot(7),
system W-space(15); guests role=0 — nimbus(10), orbit(11), vector(12), flux(13), halo(14),
mootprobe(16) [flux has ZERO memberships — the SEC-01 outsider];
projects: receipts(2, budget 60k/0), Diagnose Renew(1), P2 Scaffold(3), p4rich(4) p4vague(5)
p4empty(6) p5twin(7) all budget 0; rooms 1–4 (receipts, members 6/8/7/7) + DM 5.

## 1. Sibling projects to seed (via product API only, R-lane semantics)

**Project A: `cobalt`** — "Analytics for founder ops" (path /company/1/projects/cobalt)
- rooms: `cobalt-main` (general), `cobalt-data` (data threads home)
- members: siavash(1), Jason(9), w-ai(2), Coder(3), orbit(11)
- budget_total 30000, spent 0 → CB-01/03/05; exhaustion scenario set later via cost writes.

**Project B: `relay`** — "Integrations & webhooks"
- rooms: `relay-main`, `relay-security` (restricted)
- members: siavash(1), w-ai(2), David(8), nimbus(10), halo(14)
- budget_total 10000, spent 0.

**Existing `receipts`** stays as the Test-1 continuity world (anchors run there).

Overlap matrix (deliberate, drives MP/SEC/CP):
| user | receipts | cobalt | relay |
|---|---|---|---|
| siavash(1) | ✓ | ✓ | ✓ |
| David(8) | ✓ | ✗ | ✓ |
| Jason(9) | (admin) | ✓ | ✗ |
| orbit(11) | ✗ | ✓ | ✗ |
| nimbus(10) | partners-only | ✗ | ✓ |
| flux(13) | ✗ ZERO memberships (SEC-01 designated outsider) | ✗ | ✗ |
This gives: shared-across-3 (siavash), 2-of-3 (David), 1-of-3 (Jason/orbit/nimbus), 0 (flux).

## 2. Threads topology (TH family)
- thread `pricing-followup` under `receipts-founders` (parent has decisions history → TH-02/05)
- thread `pii-scan` under `relay-security` (restricted parent → TH-07/DM firewall cross)
- thread `attribution-jobs` under `cobalt-data` (bot work lane → TH-04 scoped wakes, MP-11)
If the thread surface does not exist at all → TH-01 becomes a filed GAP and TH ids are descoped
per the G?-first rule (M9 lesson), not failed.

## 3. DM topology (DM family)
- existing DM(5): David↔w-ai stays.
- new: siavash↔w-ai DM (canary lane DM-03 primary), Jason↔w-ai DM (DM-04 same-bot-two-humans),
  flux→w-ai DM attempt (DM-10: must be rejected/no phantom room).
- canary phrases registry (5 unique tokens, one per DM) — grep census at each phase end.

## 4. Reservation race targets (RC family)
- files (via reservation plane): `attribution.sql` (cobalt-data), `webhook-spec.md` (relay-main)
- contenders: coder vs business_analyst bots; TTL/expiry: one holder "dies" via admin release.

## 5. Approval round-trip cast (HI2 family)
- approver humans: siavash(1) and Jason(9) (races HI2-05 need TWO humans).
- gated-action scripts: 6 asks (2 approve, 2 deny, 1 cancel, 1 race) spread across 3 projects
  so MP-09/CP-09 get graded by the same beats.

## 6. Cost/budget scenarios (CB family)
- cobalt: normal accrual (2 tasks with costs → CB-03 sum check).
- relay: engineered near-exhaustion (budget 10000; single task cost 10500 → CB-02 gate +
  CB-05 post-close cost write rejection).
- receipts: untouched (control).

## 7. Functional/191 runner + soak targets (Track 2/3)
- soak lane posts a synthetic event every 10 min into cobalt-main only (bounded blast radius);
  crash drills happen AFTER the graded window closes (RST-02 protocol), on cobalt/relay first,
  receipts last.
- HA-78 strict: whole-DB snapshot taken at end of all tracks, clone replayed twice (receipts
  world is the replay script; siblings stay quiescent during replay).

## 8. Seeding & snapshot rules (hard)
- All seed writes via REST/MCP product lanes (RoomCreationService/ensure_room/project API) — no
  direct inserts, EXCEPT membership grants if no API surface exists for them (Test 1 precedent —
  logged as SEED-OPS entries).
- `storage/db` snapshot before EACH phase; ledger-first runners (harness rule §A-2).
- Merge-freeze windows announced in this folder (`FREEZE` marker file read by runners).
- Junk p4* projects: leave as-is (they're evidence), but excluded from all Test-2 censuses by name.

## 9. G0' prerequisite block (from Test 1 leftovers)
- F21 SOUL fix applied + acceptance replay (blocking SEC-01/MP-06/DM-* grading validity).
- F22/F23 if merged by kickoff: RC/burst/idempotence ids run full version; else flagged
  pre-F22 and run with circuit breakers + attribution unavailable notes.
- M9 decision: if built, MP adds dependency ids; if descoped, nothing changes (no id assumes it).

## 10. Beat script outline (for Step-3 transcript authoring, NOT built yet)
Approx 90–110 beats across 3 projects × (asks, gated actions, races, DM pivots, thread posts,
injection-flavored probes as SEC-04 with explicit safe payloads). Full script comes with Step 3.
