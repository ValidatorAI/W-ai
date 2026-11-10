# PWR Semantic Validation Roadmap — the execution plan to validate all 218 semantic tests

> Orchestrates the artifacts already in this folder. Nothing here invents new
> tests; it schedules, gates, and scores the ones defined in:
>
> | File | Role |
> |---|---|
> | `PWR explained.md` | feature/intent reference (what we claim) |
> | `project.md` + `receipts-*.md` (4) | scenario context + room contracts |
> | `pwr-feature-test-conversations.md` | v1 script — chats 101–261 |
> | `transcript-v2-completing-replay.md` | v2 script — chats 262–334 + harness HA-01…HA-104 |
> | `pwr-functionality-checklist.md` | 191 functional assertions (prerequisite layer) |
> | `pwr-semantic-checklist.md` | 218 semantic assertions (what this roadmap delivers) |
> | `transcript-semantic-validation-mapping.md` | the authority: semantic id → driver → desired state change (§A–Q) |

Ground rules (from §HR of the semantic checklist — these bind every phase):
- **HR-01 dry-run-first:** no handler runs live until its ordered step list +
  would-issue calls are logged; no tool call outside that list may appear.
- **Absence is an assertion:** every phase checks forbidden artifacts as loudly
  as required ones (noise budget HR-05 — over-action fails like under-action).
- **Evidence schema (HR-03):** every result row = `semantic-id | PASS/FAIL |
  tool_cal_log ids | entity ids | run date | branch (installation @ cd62fab)`.
- **Isolation:** never run against the shared dev DB — snapshot `storage/db/`
  and use a scratch copy or throwaway instance (INV-08 also needs a restart-capable
  target; D10 needs VM/container + webhook sink + browser).

---

## Phase 0 — Environment & readiness (½ day) — Gate G0

Purpose: prove the platform layer so any later FAIL is semantic, not infra.

- Run: functional PRE-01…05, PRO-01…11, AUT-01…06, REG-01…07 (= HA-01…HA-18, HA-23).
- Seed: project `receipts` (7), rooms 21–24 (23 = decision_room), users 2/3, bots
  4–7 as Hermes bot-users, guests 11–15; current company_status_period created.
- Attach & start pollers: message_analyzer (knowledge+task), workspace (5 scoped
  endpoints), w_ai/market_research/coder/pm/business_analyst per their maps;
  verify via `get_ai_profile_mcp` (HA-101 partial).
- Snapshot scoreboard tooling: SQL helpers for §N conservation queries.
- **G0 exit:** `/up` 200; six tools/list counts == baseline 163/142/78/29/8/16;
  auth negatives 401; every poller attached (a mention gets a same-room reply).
- **Stop-the-line:** any G0 failure = do not proceed — semantic results are
  meaningless on a broken platform (mapping §A–L assumes live bots).

## Phase 1 — v1 core replay (1 day, mostly automated) — Gate G1

Purpose: validate the 112 semantic items the v1 story carries (mapping §A–L).

- Run: post chats 101–261 strictly in id order; bot-authored rows must EMERGE
  from behavior (mapping protocol point 2), human `[tool: …]` annotations
  executed via /action-mcp.
- Checkpoints (end of each act D1→D5):
  - after D1: AN invariants (analysis 1:1, importance spot-audits), OR-03 ordering;
  - after D2: TP-01/02/11/12 topic nurture + gate biconditional; TK-08/09/11 task
    ritual (wake→dispatched flip, cost-before-close);
  - after D3: AP-02/03/05/06 approval tuples & pre-execution ban; DS-01/02 human-
    only decisions, ADR sequence; AT-01/02/03/04 attention lifecycle;
  - after D4: KN-01/02/03 family placement & verbatim; IA-01/04/05/12 interaction
    quality (creator audit, DB-before-announce); MS-01/05/06/08/09/10 messaging law;
  - after D5: XD-01…12 conservation battery, RH-01/04/05, ST-01/02/06/07, WA-01/07/08/09.
- Gap-conditioned rows measured, not skipped: edit-path (130/156/174 via web),
  reservation rows (109/132/204/235 via API), risk-category fallback (170).
- **G1 exit:** §N scoreboard end-state matches predicted counts (messages 161,
  analyses 161, ADR-001..006, approvals 13=12+1, etc.); zero conservation breaks;
  FAIL table written with evidence ids.
- **Fail-handling:** any XD violation → freeze, triage before Phase 2 (later
  phases build on the same entity graph).

## Phase 2 — Event-handler semantics (1 day) — Gate G2

Purpose: the 46 EV items — workspace's per-event contracts (mapping §P).

- Run: HA-24…HA-62 injection battery. Each case = real mutation → captured
  outbound event → workspace reaction → assertion of required artifact AND the
  forbidden twin. Dry-run step-lists first (HR-01); AN-12/XD-10 redelivery
  (HA-24/79); OR-02/08 flow-order and out-of-order delivery (HA-32/60).
- Natural pairing: reuse Phase-1 entities (blocker 120, proposal 226, todo 114)
  so event handlers act on the replayed world, not sterile fixtures.
- **G2 exit:** EV-00a…EV-41 all PASS/GAP-recorded; every handler's
  read-before-write + post-write logging confirmed via HA-61 sweep; the
  "verification-log-only" outcomes observed where they're the commonest result
  (EV-39 cosmetic, EV-22/25/41).
- **Known landmines:** add_risks/priorities MCP-absence (ledger 5) will surface
  here — expected outcome is blocker-fallback + GAP entry, not FAIL.

## Phase 3 — Topic deepening & knowledge grammar (½ day) — Gate G3

Purpose: §O first block — TP-05…19, RH-02/03, KN-04…07/09/10, AN-02/09/12/15.

- Run: chats 306–313 + HA-63…HA-67, HA-79.
- Emphasis: reactivate-not-duplicate (306), specificity ladder (307/309),
  caps (308 ≤1 topic; ≤3 links), abstention (311), delete discipline (312),
  snapshot fidelity diff (HA-65), knowledge placement + hygiene (HA-66/67).
- **G3 exit:** topic tree exact; zero duplicate topics across the whole corpus;
  required_actions merge preserved history on every touched topic.

## Phase 4 — Agent behavior, privacy & approval stress (1 day) — Gate G4

Purpose: §O remaining blocks — TK/AP/AT/DS/IA/MS/WA/ST/XD/HR items v2 owns.

- Run: chats 314–334 + HA-68…HA-80 (incl. DM surface HA-72, storm HA-71/102,
  per-profile wake HA-101/102, SSRF-adjacent behavior, budget gate 314/HA-68).
- The flagship: AGT-16 / IA-02 two-agent cooperation end-to-end (answers
  `questions on PWR.md` #1 and #20 with observed behavior).
- **G4 exit:** routing table 4/4; noise axis green (no over-cautious approvals,
  no social bot replies, no duplicate sends); privacy wording exact;
  DS-06/AT-03/MS-11/AP-01 invariant sweeps zero violations.

## Phase 5 — Infrastructure & ops proofs (1 day, parallel VM track) — Gate G5

Purpose: the semantic items whose drivers are environmental (mapping §O HR/ST/
KN-13/14 rows + §M pointers) + all remaining functional debt (HA-81…HA-104).

- Run: D10 (installer/compose/profile-dist/first-run/webhook/PUSH/config-plane/
  reservation lifecycle/scope matrix/INV battery), HA-103 isolation, HA-104 SSRF,
  HA-97 harness-convention audit (dry-run logs, evidence table completeness).
- Can run in parallel with Phases 2–4 (separate machine), EXCEPT HA-93/94 rows
  that mutate the replay DB — schedule after G4.
- **G5 exit:** clean-install story reproducible by someone outside the dev team
  (the launch-critical claim, `questions on PWR.md` #7/#8); reservation and
  scope-leak ledgers closed.

## Phase 6 — Idempotence & final conservation (½ day) — Gate G6

- Run: HA-78 full pass-2 (v1+v2 chats) into a fresh DB; XD-01 entity-delta diff;
  HA-100 conservation SQL suite over both DBs; recompute noise budget (extra
  artifacts = failures); regenerate §N scoreboard for run 2.
- **G6 exit:** run-2 end-state identical to run-1 (± nonces); all 218 rows in
  the results table have a verdict; no item left N-A (the mapping guarantees a
  driver exists for every one).

## Phase 7 — Scoring & reporting (½ day)

Deliverables:
1. `results-scoreboard.md` — 218 semantic rows + 191 functional rows, verdict +
   evidence ids (schema at top).
2. Gap ledger update — which of the 12 known gaps were confirmed/refuted in run;
   new gaps found (esp. edit/risk/reservation verdicts from G1/G2).
3. Triage list — every FAIL with: semantic id, desired vs actual state, driver
   (chat/HA id), suspected file (models/services/mcp tool), proposed fix owner.
4. Executive answers to the strategy pack's open questions: #1 (agent exchange
   boundedness — from IA-02 measurement), #4/#7/#8 (clean-install — G5),
   #13/#20 (two-agent demo — G4), #16-adjacent (comparison evidence — Phase 4).
5. Re-run manifest — items worth moving into CI (fast subset: G0 checks + §A–L
   conservation queries + invariant sweeps).

---

## Coverage ledger — every semantic prefix lands in exactly one primary phase

| Prefix (total) | P1 v1-replay | P2 events | P3 topics | P4 agents | P6 pass-2 | P7 gates |
|---|---|---|---|---|---|---|
| AN (15) | 11 | – | 4 | – | – | – |
| TP (20) | 11 | – | 9 | – | – | – |
| RH (6) | 5 | – | 1 | – | – | – |
| TK (20) | 16 | – | – | 4 | – | – |
| EV (46) | – | 46 | – | – | – | – |
| AP (15) | 11 | – | – | 4 | – | – |
| DS (7) | 4 | – | – | 3 | – | – |
| AT (8) | 5 | – | – | 3 | – | – |
| KN (10) | 5 | – | 5 | – | – | – |
| IA (12) | 7 | – | – | 5 | – | – |
| MS (13) | 11 | – | – | 2 | – | – |
| WA (10) | 6 | – | – | 4 | – | – |
| XD (12) | 8 | 1 | – | 2 | 1 | – |
| OR (8) | 5 | 3 | – | – | – | – |
| ST (10) | 5 | – | – | 5 | – | – |
| HR (6) | – | – | – | – | – | 6 |
| **total (218)** | 110 | 50 | 19 | 32 | 1 | 6 |

(Effort split: P0 0.5d → P1 1d → P2 1d → P3 0.5d → P4 1d → P5 1d (parallelizable)
→ P6 0.5d → P7 0.5d ≈ **6 calendar days, ~4.5 person-days of harness time**,
one operator + one observer for judgment items AN-14/RH-04/DS-04 spot-checks.)

## Dependency graph (must-run-before)

```
G0 ──► P1(v1 replay) ──► P2(events) ──► P3(topics) ─┐
              └────────► P4(agents/privacy) ────────┼──► P6(pass-2 + conservation) ──► P7(report)
G0 ──► P5(VM/ops track, merges before P6 for HA-93/94)
```

## Risk register (schedule-level only)

1. **Poller flakiness** → bot messages never emerge → half of §A–L unverifiable.
   Mitigation: G0 gate includes an explicit mention→reply round-trip test.
2. **Shared dev DB corruption** → irreproducible FAILs. Mitigation: snapshot +
   scratch DB; pass-2 proves reproducibility.
3. **MCP gap items (edit/risk/reservation) mis-logged as FAIL** → wrong ledger.
   Mitigation: mapping §M "conditional" rows are recorded as GAP+measurement,
   never FAIL.
4. **Judge-dependent items drift (AN-14, RH-04, DS-04, MS-06)** → Mitigation:
   two-person spot checks with written rubric; disagreements → checklist patch.
5. **P5 VM availability** → blocks G5 merge. Mitigation: P5 runs parallel;
   P6 only waits for the two mutating probes (HA-93/94).
6. **After run: checklist itself may be wrong** (semantic items that are
   unimplementable in PWR's model) → that's a finding, filed as SOUL/skill
   corrections in W-ai, not a code FAIL.

First executable move: **Phase 0 + Phase 1** — I can snapshot the DB, seed
project/rooms/users, run G0 (≈20 curl probes), and post v1's first act right
now on the live instance.

---

## Appendix A — complete semantic test inventory, phase by phase (all 218 ids)

> Generated from the mapping sections (rule: §A–L→P1; EV+event ordering→P2; §O topic/
knowledge/AN-edge→P3; §O agent/privacy/approval→P4; XD-01→P6; HR→P7). Phase 5 carries no
primary semantic item — it is the functional/ops track whose evidence is consumed at P4/P6/P7.

### Phase 1 — v1 core replay (chats 101–261; mapping §A–L) — 110 items

- **AN (11):** AN-01, 03–08, 10, 11, 13, 14
- **TP (11):** TP-01–04, 08, 10–12, 14, 16, 20
- **RH (5):** RH-01, 03–06
- **TK (16):** TK-01–04, 08–15, 17–20
- **AP (11):** AP-02–10, 12, 14
- **DS (4):** DS-01–03, 07
- **AT (5):** AT-01–04, 08
- **KN (5):** KN-01–03, 08, 10
- **IA (7):** IA-01, 02, 04–06, 09, 12
- **MS (11):** MS-01, 03–10, 12, 13
- **WA (6):** WA-01, 02, 07–10
- **XD (8):** XD-03–06, 08, 09, 11, 12
- **OR (5):** OR-01, 03, 04, 06, 07
- **ST (5):** ST-01–03, 06, 07

### Phase 2 — event-handler battery (HA-24…62; mapping §P + EV ordering overrides) — 50 items

- **EV (46):** EV-00a–e (shared-behavior battery: read-before-write, redelivery, post-write logging, ambiguity, one-outcome) + EV-01–41 (per-skill handler contracts)
- **XD (1):** XD-10
- **OR (3):** OR-02, 05, 08

### Phase 3 — topic deepening & knowledge grammar (chats 262–264, 306–313; HA-63…67, 79; mapping §O) — 19 items

- **AN (4):** AN-02, 09, 12, 15
- **TP (9):** TP-05–07, 09, 13, 15, 17–19
- **RH (1):** RH-02
- **KN (5):** KN-04–07, 09

### Phase 4 — agent behavior, privacy & approval stress (chats 314–334; HA-68…80; mapping §O) — 32 items

- **TK (4):** TK-05–07, 16
- **AP (4):** AP-01, 11, 13, 15
- **DS (3):** DS-04–06
- **AT (3):** AT-05–07
- **IA (5):** IA-03, 07, 08, 10, 11
- **MS (2):** MS-02, 11
- **WA (4):** WA-03–06
- **XD (2):** XD-02, 07
- **ST (5):** ST-04, 05, 08–10

### Phase 6 — idempotence & final conservation (HA-78/100) — 1 items

- **XD (1):** XD-01

### Phase 7 — scoring & reporting (HA-97 convention gate) — 6 items

- **HR (6):** HR-01–06
