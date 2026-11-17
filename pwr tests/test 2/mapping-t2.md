# Test 2 Mapping — checklist-v2 id → driver → observable (DRAFT for Step-3 validation)

Observable grammar (same as Test 1): ENTITY (row change via API census), EVENT (output_events row
with payload field), CAL (tool_cal_logs row citing ids), MSG (bot message with cited ids),
ABSENCE (grep with zero matches — absence is an assertion). All reads via harness `walk_pages`.

## TH threads
- TH-01 → A03/A04 → ENTITY: child room row (parent_id set), GET rooms/:id/threads includes it.
- TH-02 → A04 → EVENT+ENTITY: message_created room=thread; project_id inherited = cobalt's.
- TH-03 → A05 → MSG: answer visible in thread; membership rule matches spec (parent members see).
- TH-04 → A05/A16 → CAL/ENTITY: only cobalt-assigned bots react (wake profile names in logs).
- TH-05 → A16 → ENTITY: attention item room_id=thread id, origin cites thread.
- TH-06 → C09×TH variant → approval row room_id = thread when raised there.
- TH-07 → E01 vs thread content → ABSENCE: flux sees no thread artifacts anywhere.
- TH-08 → A17/A18 → ENTITY: archive sets archived_at; pending items remain resolvable + listed.
- TH-09 → all arcs census → ids globally unique incl. thread posts.
- TH-10 → A04/A05 → EVENT: analyzer processed thread message (message_created + analysis row).
- TH-11 → A03 by-name creation → fuzzy name resolve, id-over-name precedence holds.
- TH-12 → C11 conservation → thread messages counted in joins (no orphan room_ids).

## CP company
- CP-01 → D01/D02 → ENTITY+read: company-home item lifecycle.
- CP-02 → D01 → EVENT priorities_created/_resolved parity.
  [CORRECTED 11-16: driver = company_status_items surface — MCP priorities/learnings tools or POST /api/company_status_items with company_status_period_id; NOT attention_items]
- CP-03 → D03 → ENTITY: learnings/knowledge_activities row once (re-run → no dup).
  [CORRECTED 11-16: driver = company_status_items surface — MCP priorities/learnings tools or POST /api/company_status_items with company_status_period_id; NOT attention_items]
- CP-04/05 → D04 → read exactness / ValidationError ambiguous.
- CP-06 → D05 [GAP-flag: period-close lane may not exist → file, don't fail].
- CP-07 → D06 → per-asker visibility diff orbit vs David (two GETs as two actors).
- CP-08/09/10/12/13/14 → D07–D11 → ENTITY/CAL/MSG/422 per row.
- CP-11 → D01 → EVENT company-item create fires (M8 parity recheck at company scope).

## MP multi-project (A/B/D arcs cross)
- MP-01 → seed step → ENTITY projects+rooms exist with paths.
- MP-02/03/04 → A06/B03/C04 → topic/task/knowledge namespace isolation (census diffs).
- MP-05 → CB family. MP-06 → A07 (David∉cobalt) → MSG template-only, ABSENCE of cobalt entities.
- MP-07 → C11 joins. MP-08 → A04 vs receipts topic of same subject → two ids, no merge.
- MP-09/10/11/12 → B07×queue, A16, B03, D08.

## DM depth
- DM-01 → GAP-probe first (bot-initiated DM attempt) — file if absent.
- DM-02 → B12/B13 → MSG location: answer stays in DM (no echo in rooms).
- DM-03 → B12/B14 canary census across ALL bodies (incl. loading msgs) → ABSENCE.
- DM-04 → two DM asks same bot → per-conversation context isolation (answer-content diff).
- DM-05..10 → A07 flux-DM (C07), SEC-010 rows, joins census.

## RC reservation races
- RC-01 → A11/A12 → exactly one active row, second response cites held-by (MSG/API body).
- RC-02/03/04 → harness-driven acquire/release/expiry sequence → CAL+ENTITY, no leak rows.
- RC-05 → read surface shows holder identity (needs holder_user_id — exists since brief E).
- RC-06/07/08 → cleanup job no-touch active; non-holder release 4xx; conservation join.

## HI2 approval round-trips
- HI2-01 → C09+gated script → chain: raise MSG → approve action row → execute → EVIDENCE CAL/ARTIFACT
  before finished=1 (S7 rule recheck with real agents).
- HI2-02 deny → task actual_task_context cites reason + attention dismissed + NO re-raise (KN-09 kin).
- HI2-04/05 → two-human race: exactly one resolution (status transitions monotonic), loser 4xx, echo once,
  action rows count exact (double-click grammar anchor).
- HI2-06 → B06/C01 rename lane post-AP-11: zero approvals raised (count delta 0).
- HI2-07 → C02 + F22 idempotence. HI2-08 → thread-scoped approval. HI2-09 → flat GET/POST parity.
- HI2-11 → finished stays 0 pre-evidence (row poll). HI2-12 → attempts-reset lane untouched approvals.

## CB cost/budget
- CB-01/03 → A13/A14 → cost rows + sums (task 1050, project spent 1050).
- CB-02 → B08/B09 → over-budget: new dispatch blocked/reported with explicit exhaustion MSG (TK-05+).
- CB-04 → B11 admin reset via permitted PATCH lane (else GAP-filed).
- CB-05 → B10 post-close write: rejected or append-audit, never silent overwrite (row hash before/after).
- CB-06/07/08 → census per project; sum≤spent; zero-cost close allowed.

## SEC
- SEC-01 → E01 3 shapes → template wording present, identifiers ABSENT (F21 acceptance generalized).
- SEC-02 → E02 forged actor → 422 record untouched (M6 grammar).
- SEC-03 → E03 → unknown-profile rejection (M10 guard).
- SEC-04 → E04 injection-style → refusal MSG + noop CAL + ABSENCE of any write (zero row deltas).
- SEC-05/07 → E05/E07 → server-side membership enforcement (probe as outsider via API directly,
  not just agent behavior — the agent gate is UX, this is the wall).
- SEC-06 → E06 stored raw/escaped render. SEC-08/09 → E08 scope/session matrix. SEC-10 → B14 census.

## ENV / RST (Arc F) — observables per id from harness histograms; RST ids graded on
post-restart group/event states (all pending→dispatched within cadence; zero double-dispatch rows).

## INV / ATT / MCP (Arc E) — harness-only, direct API/MCP calls; observables = response codes,
row payloads, render-surface grep, tool-inventory diff vs baseline counts.

## R (40 anchors) → Arc C mapping table (each anchor id → C0x beat + reused Test-1 observable text).
Full per-id list generated into `anchors-map.json` at harness build (Step 4), seeded from
results-scoreboard files of Test 1 (fix-cited ids auto-included).
