# PWR Test 2 — Plan (v0, pending step-by-step validation)

Prepared 2026-11-16 from Test 1 experience (`../test 1/OVERALL-REPORT.md`).
This is the PLANNING doc only — no test assets exist yet; each step below has a
**VALIDATION GATE**: nothing is built until you approve that step.

---

## A. What Test 1 taught us (design constraints for Test 2)

1. **Shape-probe before fire** — half the Phase-2/4 crashes were guessed payloads. Test 2 runners
   must begin every scenario stage with a controller/route schema diff (cheap curl/PRAGMA check),
   then proceed. (Saved us: R1 regrade; cost us: 2 runner crashes + one lost full replay.)
2. **Ledger-first, resume-safe runners** — write evidence to jsonl BEFORE in-memory results; every
   phase runner must be re-runnable after a crash from its last completed step (test 1 lost the
   22-min R2 sweep to a column-name bug because state lived in a variable).
3. **Merge-freeze protocol** — a puma hot-reload minute silently destroyed an entire evidence
   window (Phase 4 v2). Rule: no merges during a graded window; if unavoidable, stamp `counts_t0`
   immediately pre/post and auto-mark the window suspect.
4. **Reads are paginated newest-first @200** — empty probes were MY query bugs twice. Harness ships
   a `walk_pages()` helper; every assertion uses it.
5. **Correlation sweep > live windows** — dispatch latency outruns human patience; grade from
   ledger joins, not fixed sleeps. (Kept Phase 2 honest; 420 s heals in Phase 5 are the norm.)
6. **DB surgery is allowed but must be: minimal, committed, logged here, and never in graded
   windows** (poison tasks 34/35, strike sims, burst cleanup — all legitimate, all now formalized).
7. **Agent feedback loops are a real hazard** (3 calls → 20 rows). Test 2 burst/idempotence probes
   carry built-in circuit breakers: cap-N + auto-cleanup clause in every creation scenario.
8. **Hermes fixes are first-class work** — S5/S6/S7/AP-11/KN-09 were fixed AND verified inside the
   test loop. Test 2 budgets explicit SOUL-fix deploy/verify rounds (they take ~15 min each, not
   "zero").
9. **Protected-file writes need the approval word BEFORE the window** — F21 sat blocked mid-Phase.
   Pre-collect approvals for planned SOUL edits.
10. **Never trust 'all green' single queries** — two HA-100 "violations" were my wrong assumptions
    (int enums, join semantics). Conservation suite ships with per-query unit self-tests.

## B. Test 1 leftovers that become Test 2 prerequisites (not scope)
- F21 w_ai privacy SOUL fix (needs your approval + acceptance replay)
- F22 creation idempotence / F23 creator attribution (Copilot round)
- M9 dependency decision, O-6 ADR structure decision, O-8 wording
If any is unresolved at kickoff, it lands in the Test 2 G0' readiness gate as a blocking item, and
the related scenarios are deferred rather than half-graded.

## C. What Test 2 is — the delta, not a rerun

Test 1 asked: "does PWR behave as its SOULs say?" (247 ids, single project, one world).
Test 2 asks the next three questions:

**Track 1 — Breadth: the surfaces Test 1 never touched (~80 new semantic ids)**
- THREADS / child rooms (create, context inheritance, privacy across parent/child, message
  routing) — the hierarchy spec says threads exist; Test 1 had ZERO thread battery.
- COMPANY-level plane: company home items, priorities/learning categories end-to-end,
  multi-project attention, cross-project material_changes, company status periods beyond "binding
  rejected" (period rollover, by_slug/by_name lookups under load).
- MULTI-PROJECT world: 2–3 concurrent projects, agents cross-talking, no context bleed
  (topic/knowledge/task namespaces per project), per-project budget accounting (ai_task_cost).
- DIRECTS/DM depth: private→private continuity, bot-initiated DMs, room↔DM context firewall
  (MS-02 was one canary; make it a battery).
- RESERVATION concurrency: two agents racing the same file lock; expiry takeover; holder churn.
- DECISION/HI arcs end-to-end: gate → human click via ApprovalFlow → execute → evidence-before-
  close (AP-14 chains) → denial path → cancel path → double-click idempotence under real agents
  (Test 1 graded mostly the raise side; Test 2 grades the FULL loop).
- COST/budget semantics: token/USD accounting across profiles, exhaustion gates (TK-05 deepened:
  explicit exhaustion messaging, partial-spend, admin reset).

**Track 2 — Rigor: the proofs Test 1 consciously skipped (~40 ids + full 191 functional)**
- HA-78 strict: fresh-DB double full replay (deterministic end-state equality).
- HA-96 INV battery: TZ (+03:30) read-back, trailing-space dupes, unicode/emoji/RTL bodies,
  `<script>`/HTML injection render & storage path, README/route parity re-check.
- Attachment & size caps (HA-90 subcases): 6-attachment events, oversize payloads, dead-URL
  variants (localhost/example.invalid/redirect chains).
- 191-item functional checklist: systematic pass, every route/tool once with positive +
  negative (404/401/422) expectations.
- MCP auth/session edges: wrong Mcp-Session-Id, expired session, cross-scope tool call
  (write-tool on read-mcp), unknown-arg regression guards (M1 keeps working).

**Track 3 — Endurance & chaos (~15 new ids)**
- 24-hour soak: steady synthetic event flow; assert zero stalled groups, constant heal times
  (no drift), noop-rate stable, DB size growth bounded, WAL checkpointing healthy.
- Crash drills (scheduled, not during graded windows): gateway restart mid-flight (does the
  per-claim self-enqueue recover ALL groups?), puma restart mid-replay, kill-poller (HA-71
  finally runs: silence-then-catchup proof), Redis/resque flush if applicable.
- Concurrent-human stress: two founders approve/deny the same request simultaneously (exactly-one
  resolves; echo once), double-post same ask (dedupe holds with F22).

**Security mini-track (folded into Track 1/2 as scenario prefixes SEC-):**
- Cross-project bleed probes (guest agents asking across scopes — F21 acceptance generalized),
  forged actor names/ids in payloads (M6/M5-class regressions), fuzzy-match abuse
  ("w-aix" → matches w-ai?), prompt-injection-ish message bodies ("ignore your rules…") —
  graded as: does the agent contract hold.

## D0. Step 0 VALIDATED (2026-11-16, by siavash via kickoff form)
- Tracks: ALL THREE + SEC mini-track.
- World: keep current `receipts` world + seed 2 sibling projects for multi-project/threads.
- Regression: anchors-only (~40 ids where fixes landed); full 247 NOT rerun.
- HA-78 destructive strict: scheduled LAST, on DB snapshot/clone.

## D. Step-by-step preparation with VALIDATION GATES

**Step 0 — Scope contract (THIS step, now)**
Deliverable: agreement on Track 1/2/3 inclusion, security mini-track, new-id families
(TH thread, CP company, MP multiproject, RC reservation-concurrency, CB cost, SEC, ENV soak,
RST restart), time budget, fixture-world strategy.
YOU VALIDATE: the four questions in the kickoff message.

**Step 1 — Checklist v2 ✅ VALIDATED (approved as-is, 2026-11-16) → `pwr-semantic-checklist-v2.md` shipped (122 new + 40 anchors + 191 functional, 87 MUST / 35 NICE)** (`test 2/pwr-semantic-checklist-v2.md`)
Extract new ids from SOULs + PWR docs + the gap list above; re-state Test-1 ids only as
REGRESSION ANCHORS (a short per-family set, not all 247 — full rerun only where a fix landed,
e.g. AP-11/KN-09/F21/F22). Target ≈ 135–160 new/updated ids.
YOU VALIDATE: id list + severity ranking (which are MUST vs NICE) before mapping.

**Step 2 — Transcripts & world design ✅ VALIDATED (approved as-is, 2026-11-16) → `world-design.md` final (cobalt/relay names, overlap matrix, Jason=2nd approver, budgets 30k/10k/over-10.5k)**
Two new scripted worlds: (W1) multi-project company scenario script (~120 beats incl. threads,
DMs, two founders racing, one saboteur-guest); (W2) fresh-DB determinism twin of Test-1 v1 core
(only for HA-78 strict, run in a sandbox copy).
YOU VALIDATE: world B story beats + actor roster + which rooms/threads exist.

**Step 3 — Mapping & roadmap v2** (`test 2/mapping.md`, `test 2/roadmap.md`)
Every new id → driver → observable; phases with gates G0'–G6', each ≤ 1 working day, with the
harness rules baked in (merge-freeze, circuit breakers, walk_pages).
YOU VALIDATE: phase split + schedule + go/no-go on the destructive fresh-DB run slot.

**Step 4 — Harness v2 build** (scripts in `test 2/harness/`)
Runner library: shape-probe stage, ledger-first, resume pointer, burst circuit breakers,
conservation self-tests, scoreboard auto-emitter (phase runner produces its own results-*.md).
Functional-checklist runner (191 ids, auto-generated from the doc).
YOU VALIDATE: dry-run of harness against live world (no assertions graded — HR-01 first step).

**Step 5 — Execution** Phases per roadmap; per-phase scoreboard; each phase's findings triaged
HERMES vs COPILOT vs PRODUCT immediately (no post-campaign archaeology like Test 1 Phase 4–7).
YOU VALIDATE: at every gate (G0'…G6') before the next phase starts.

**Step 6 — Final report + trend pack**
Compare Test 1 → Test 2 (stall counts, heal times, noise ratio, leak incidents, approval hygiene)
from machine-readable `results.jsonl` both campaigns now emit.

## E. Rough effort (after scope validated)
- Steps 0–1: 1 working session (planning + checklist drafting)
- Steps 2–4: ~2 days of agent work, mostly writing + dry-runs
- Step 5 execution: Track 1 ≈ 2 days (agent waits dominate) · Track 2 ≈ 1 day (+5 h if HA-78
  strict runs) · Track 3 ≈ 1 day incl. the 24 h soak (unattended)
- Step 6: same day
Total calendar ≈ 5–6 days wall-clock, of which ~1 day is your validation time.

## F. Standing risks (from Test 1)
- Gateway saturation by our own traffic (cap 8 was hit repeatedly) → throttle scenario fan-out.
- Transient-code incidents (I2 precedent) → snapshot DB before each graded phase; keep external
  evidence ledgers.
- Protected-file approval latency → pre-approve the SOUL edits listed in §B before Track 1 starts.
