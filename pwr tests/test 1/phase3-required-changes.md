# Phase 3 — Required Changes (from results-scoreboard-phase3.md)

Repo state at finding: `W/pwr` branch `installation`; original findings at `d8eacef`, M10 re-check at `4d3fbdb` (2026-11-15).
Owner tags: `[COPILOT]` = PWR code (paste-ready below) · `[HERMES]` = W-ai souls/skills + mirror deploy · `[PRODUCT]` = decision needed · `[TEST-OWNER]` = re-test work I do after fixes land.

---

## MUST — STATUS (verified live 2026-11-15 against HEAD `4d3fbdb`)

- **S9 ✅ FIXED** (adabe3a): `DELETE /api/messages/137` -> 204, row gone, Message model now has
  `dependent: :destroy` on message_topics/message_analysis (+boosts/approval). KN-08 closes with it:
  knowledge item citing deleted msg 137 reads back fine.
- **F17 ✅ FIXED** (e998f71): prose name -> 422 "Name must be a short title, not prose"; short name 201.
- **F18 ✅ FIXED** (6ed3905): `http://example.invalid/...` -> 422 "placeholder or dead domain";
  601-char title -> 422 max 255; valid asset 201.
- **M10 ⚠️ CORE FIXED, 2 DEFECTS RE-FILED** (4d3fbdb): queue starvation is gone — proven live
  (task 43 `does_not_exist_profile` struck out after 3 recorded attempts with the 404
  `dispatch_error`; task 44 `coder` behind it reached dispatch anyway; queue drained to zero).
  Remaining defects in the same commit: (1) `available_profile_names` swallows all errors -> nil, so
  create-time validation never fires even though the router is reachable (chat dispatch to the same
  bad profile got a real HTTP 404); (2) 3rd strike sets `finished: true` — a never-executed task
  silently appears completed, with no blocker/attention visibility.

- **M10-remainder ⚠️ PARTIAL** (166a054, checked live 2026-11-15):
  - Defect 2 core ✅ — 3rd strike keeps `finished=false`, parks task, creates blocker
    `AttentionItem` + emits `blocker_created`. Verified BOTH ways: simulated (task 44 ->
    blocker #19, event #723) and organic live queue (task 45 `does_not_exist_profile` struck
    3x on HTTP 404 -> parked, blocker #20, event #724; queue drained behind it — no starvation).
  - Defect 1 ❌ — create-time validation STILL never fires: `available_profile_names` GETs the
    router's root `/v1/models`, which this router answers with **HTTP 404 "Unknown or
    unconfigured profile"** (it only serves profile-scoped `/p/<profile>/v1/models`), and the
    rescue still logs/mmaps that HttpError as "Gateway unreachable" -> nil -> accept. Task 45
    was created after this "fix". The reachable-vs-unreachable distinction (any HTTP response =
    reachable) was explicitly required and not implemented.
  - Retry affordance ❌ — `dispatch_attempts` is permitted on neither `PATCH /api/api/tasks/:id`
    nor `update_ai_task`; PATCH with `{"dispatch_attempts":0}` silently ignored; a parked task
    has no path back to the queue.
  - Note: blocker created via `project.attention_items` (project scope, room_id nil) — spec asked
    room-first, project-fallback; acceptable if project attention surfaces are monitored, flag once.

- **M10-remainder 2 ⚠️ 2.5/3** (2fd518c, re-checked live 2026-11-15):
  - (1) create-time validation ✅ — `profile_exists?` probes `/p/<name>/v1/models` with chat auth;
    live: coder→true, unknown→false; `create_ai_task` bad profile now REJECTED with
    "Unknown assignee profile 'does_not_exist_profile' for the active Hermes gateway."
  - (2) retry affordance ⚠️ — reset works (PATCH dispatch_attempts=0 -> task 44 re-queued and
    genuinely re-dispatched on next polls) BUT range validation missing: PATCH
    `{"dispatch_attempts":9}` accepted silently (200), leaving the task with dispatched=false and
    attempts>=MAX — invisible to the queue selector yet not marked parked. Required: validate
    0..MAX_DISPATCH_ATTEMPTS -> ValidationError/422 outside range.
  - (3) blocker scoping ✅ — strike-sim on task 45 produced blocker #23 with room_id=2 (room-first).
  - Observation (new, not M10): repeated `Net::ReadTimeout` dispatches to coder — Hermes::Client
    default timeout seems too short for cold/busy profiles; consider configurable per-call timeout
    for dispatch messages.

- **M10-remainder 3 ✅ SOLVED** (7a06e94, verified live 2026-11-15): REST PATCH battery on task 44 —
  `9`/`-1`/`"abc"` -> 422 with record untouched; `3` -> 200; `0` -> 200 + full requeue reset
  (attempts 0, dispatched false, finished false, error cleared). MCP `update_ai_task` validates too
  ("dispatch_attempts must be an integer between 0 and 3", isError). Dispatcher now passes
  `Hermes.configuration.dispatch_timeout` to the ping; fallback chain HERMES_DISPATCH_TIMEOUT ->
  HERMES_HTTP_TIMEOUT -> 120 default confirmed live (=60 with current .env, by design; set
  `HERMES_DISPATCH_TIMEOUT=120` in .env explicitly to loosen cold-profile timeouts).
  Docs updated (.env.example, ENVIRONMENT_VARIABLES.md). **M10 family CLOSED.**

### M10-remainder 3 (historical prompt as delivered)

"In Api::TasksController (and update_ai_task if it gained the same attribute), the newly permitted
`dispatch_attempts` lacks range validation: PATCH {\"dispatch_attempts\": 9} returns 200 and leaves
the task undispatched but invisible to the queue (attempts >= MAX excludes it from the selector).
Validate: integer between 0 and AiTask::MAX_DISPATCH_ATTEMPTS inclusive; any other value raises the
existing ValidationError so the endpoint keeps the 422-with-message contract. Spec: PATCH 9 -> 422
record untouched; PATCH -1 -> 422; PATCH 'abc' -> 422; PATCH 0 -> 200 with the existing
requeue-reset behavior."

### M10-remainder 2 (round, historical) [COPILOT] — paste prompt as delivered

"Two follow-ups on commit 166a054 (AI task dispatch starvation):
(1) Fix create-time profile validation: `Hermes::Client#available_profile_names` calls the router
root `/v1/models`, which returns HTTP 404 'Unknown or unconfigured profile' on this gateway — it
only serves profile-scoped paths. Do NOT enumerate; validate the single requested name: hit
`GET /p/<assignee_profile>/v1/models` with the same auth headers as chat_completions. 200 =
profile exists (accept); HTTP 404 with the 'Unknown or unconfigured profile' body = reject with
the existing ArgumentError/ValidationError naming the unknown profile; connection-level failures
only (ECONNREFUSED/DNS/connect timeout) may soft-accept. Any HTTP status code means the gateway
was REACHABLE — stop mapping HttpError to 'unreachable' (the log line 'Gateway unreachable while
fetching profile names' is emitted for a 404 from a live gateway).
(2) Add the retry affordance for parked tasks: allow resetting `dispatch_attempts` through the
existing `PATCH /api/tasks/:id` (and/or `update_ai_task`) — permitted attribute, validated
integer 0..MAX_DISPATCH_ATTEMPTS; resetting to 0 must also set `dispatched=false` so the task
rejoins the queue on the next poll. Spec: parked task (attempts=3, dispatched=true, finished=false)
-> PATCH reset -> undispatched again and dispatchable."

### M10 remainder (round 1, now historical) [COPILOT] — full paste prompt (verified state 2026-11-15, HEAD 4d3fbdb)

Fix two remaining defects in the AI-task dispatch failure path (repo: Bonfire/Space Rails app;
relevant files: `app/services/hermes/client.rb`, `app/services/mcp/tools/tasks.rb`,
`app/models/ai_task.rb`, `app/services/ai_task_dispatcher.rb`).

Background. Commit "Fix AI task dispatch starvation and assignee validation" added:
`dispatch_attempts`/`dispatch_error` columns on `ai_tasks`, `AiTask#mark_dispatch_failed!` with
`MAX_DISPATCH_ATTEMPTS = 3`, queue query excluding struck tasks, and `validate_assignee_profile!`
in the `create_ai_task` MCP tool using `Hermes::Client#available_profile_names`. Live testing
showed the queue starvation is fixed, but two things are wrong:

Defect 1 — create-time assignee validation never fires. `Hermes::Client#available_profile_names`
rescues all errors (`HttpError`, timeouts, socket errors, `StandardError`) and returns `nil`;
`validate_assignee_profile!` then treats `nil` as "gateway unreachable" and accepts any profile.
But the Hermes gateway IS reachable in these cases: dispatching to the unknown profile
`does_not_exist_profile` returns a real HTTP 404 JSON body from the router. So the profile-list
call is failing on URL/path/auth shape, not connectivity, and unknown profiles are still accepted
at create (wasting 3 poll cycles per task). Fix:
1. Make `available_profile_names` use the exact same base URL, API key header and auth mechanism
   that the working `chat_completions(payload, profile:)` path uses — just against the router's
   `GET /v1/models` endpoint (the router lists loaded profiles there).
2. Distinguish "gateway reachable but list request failed" from "gateway unreachable": on any
   response (including 401/403/404), treat the gateway as reachable; log a warning with the error
   class + message when the list fails while reachable. Only connection-level failures
   (ECONNREFUSED, DNS, connect timeout) should permit the soft-accept fallback.
3. When the list succeeds, unknown `assignee_profile` values must raise the existing
   `ArgumentError`/ValidationError contract so `create_ai_task` returns a clear rejection naming
   the unknown profile.
4. Do not change behavior when the gateway is genuinely down: accept and let the dispatcher's
   3-strike logic handle it.

Defect 2 — struck-out tasks are silently marked completed. `mark_dispatch_failed!` currently does
`update!(dispatched: true, finished: true, ...)` on the 3rd failure. `finished:true` means "work
done" in every surface (kanban/UI/attention queries filter on it), so a task that never executed
appears completed — silent data corruption. Fix:
1. On reaching `MAX_DISPATCH_ATTEMPTS`, keep the task out of the dispatch queue (whatever existing
   flag/query semantics you need — a dedicated terminal failure state is preferable to abusing
   `finished`), but do NOT set `finished = true`.
2. Create a human-visible blocker: an `AttentionItem` with `category: "blockers"`, title like
   `"Dispatch failed after 3 attempts: task <id> (<assignee_profile>)"`, body/meta referencing the
   `dispatch_error`, in the task's `room_id` (fall back to the project's main room when the task
   has no room). Use the SAME creation path the web UI/controller uses (the `AttentionItem`
   `after_create_commit :record_created_event!` callback already emits `blocker_created`), so both
   planes stay identical and the event fires automatically.
3. Add an admin/agent retry affordance: resetting `dispatch_attempts` to 0 (via the existing REST
   `PATCH /api/tasks/:id` surface if it can carry that attribute; otherwise a small dedicated
   route) must return the task to the dispatchable pool.

Acceptance tests (required):
1. Unit: `AiTask#mark_dispatch_failed!` third call -> blocker `AttentionItem` exists in the task's
   room with category `blockers`, task is NOT `finished`, and a `blocker_created` output event row
   exists.
2. Request/tool test: `create_ai_task` with a well-formed but unknown `assignee_profile` against a
   reachable-but-wrong-profile gateway returns the validation rejection (stub the router's
   `/v1/models` list in tests); with the gateway truly unreachable (connection error stub) it is
   accepted.
3. Integration: task A with unknown profile strikes 3 times; task B with a valid profile still
   dispatches (this passes today — keep it passing); after A strikes out, assert A is visible via
   `GET /api/attention_items` as a blocker and `A.finished == false`.

Constraints: mirror existing web-controller semantics, no parallel behavior paths; validation
errors keep the ValidationError/422 contract; never coerce unknown values silently.

## MUST — original briefs (pre-merge, kept for reference)

### S9 [COPILOT] — `DELETE /api/messages/:id` raises 500 (FK constraint), message survives

**Repro (live, twice):** `DELETE http://localhost:3000/api/messages/137` with the output-events
token → HTTP 500 HTML error page; message row persists. Controller path:
`Api::MessagesController#destroy` line 123 (`message.destroy` → `broadcast_remove`), exception:

```
ActiveRecord::InvalidForeignKey (SQLite3::ConstraintException: FOREIGN KEY constraint failed)
  app/controllers/api/messages_controller.rb:123:in 'Api::MessagesController#destroy'
```

Transaction rolled back after destroying ActionText rich text + loading boosts/approval — so a
child table with an FK on `messages.id` is NOT covered by `dependent:` (top suspects:
`message_topics`, `message_analyses`, approval/action-text side tables). The web-plane destroy
works (messages were deleted through it in earlier phases), so the model's dependent cleanup is
incomplete for the plain `destroy` path the API uses, or the web controller runs extra cleanup.

**Blocker impact:** KN-08 (knowledge item citing a deleted message must degrade, not break)
is untestable until this lands.

Paste for Copilot:

"Fix `Api::MessagesController#destroy` (app/controllers/api/messages_controller.rb:123): calling
`message.destroy` raises ActiveRecord::InvalidForeignKey (SQLite FK constraint failed) and the
transaction rolls back, so REST deletion of messages never works. First reproduce with
`DELETE /api/messages/137`. Find every table with a FK referencing messages (PRAGMA foreign_key_list
for each) and compare against the Message model's `dependent:` declarations — likely gaps:
message_topics, message_analyses, approval request action tables. Fix by completing `dependent:
:destroy`/`:nullify` in the Message model (choose semantics that MATCH the web controller's delete
path — read Users::MessagesController destroy first and mirror it; do not invent new semantics).
Add a test: create a message with a boost, a topic link, an analysis row, and an approval request,
destroy via API, expect 204 and all dependent rows handled per web semantics, and a knowledge item
whose text cites the message id must still read back without error afterwards (degradation, not
crash)."

### F17 [COPILOT] — API accepts prose paragraph as directory-item name (web-plane placement rule bypassed)

**Evidence:** `POST /api/projects/2/directory_items {"name":"This is a full prose paragraph about
launch metrics and should not be a directory entry","item_type":"file"}` → 201-ish created (id 7).
Phase-3 KN-06 expectation (from the semantic checklist): directory entries are names/titles, not
sentences. If the WEB form/service enforces this (verify in the web controller/service or model
validation first), the API plane bypasses the rule — an emitter/validation parity gap exactly like
M8's family. If the web also accepts it, this is a product-rule gap and should be implemented in
the MODEL so both planes share it.

Paste for Copilot:

"Directory-item placement rule is not enforced on the API plane: POST /api/projects/:id/directory_items
accepted a full prose sentence as the name (row id 7 in development). Locate the canonical rule (web
controller/model validation for directory items vs knowledge-note placement — read how the web plane
distinguishes a name-like short title from a sentence). Implement the validation in the MODEL (shared
by both planes, no parallel behavior paths): reject name values that look like prose (e.g., more than
N words or ending in sentence punctuation) with ActiveRecord::RecordInvalid so controllers keep the
422-with-clear-message contract, and add model + request specs covering (a) normal short names pass,
(b) prose rejected, (c) the same rejection fires via API and via web."

### F18 [COPILOT] — external assets: dead URL and 601-char title accepted via API

**Evidence (same run):** `POST /api/projects/2/external_assets` with `url:"http://example.invalid/deck.pdf"`
created id 1; title of 601 chars created id 2. Expected per checklist (KN-07 family): dead/placeholder
URLs rejected (or at least flagged) and title length capped. Same parity rule as F17: whatever the
web plane does, move it to the model so both planes enforce it. Reachability check must be non-blocking-safe:
validate URL FORMAT synchronously; do health-check synchronously against third-party hosts (a HEAD probe
with short timeout, recorded as `active:false`/flag is acceptable; hard failure on network timeout is NOT).

Paste for Copilot:

"External asset validations are missing on the API plane: a dead placeholder URL
(http://example.invalid/...) and a 601-character title were both accepted via
POST /api/projects/:id/external_assets (rows id 1, 2). Read the web-plane behavior for external
assets (Users/... controllers + model) and move any existing title-length/URL-format rules into
the ExternalAsset model so both planes share one validation path. Add: length cap consistent with
DB column intent (reject > 255 chars with RecordInvalid -> 422), URL format validation (valid
http/https URI), and a clearly-named `placeholder/dead domain` rule per the existing product spec
(check the semantic rule source first; if none exists, implement reject-on-obvious-placeholder
domains like example.invalid/localhost with a config list). Request specs for API and web."

---

## SHOULD

### M9 (carry-over, [PRODUCT]) — dependency write surface still absent
`70dedfe` aligned the dependency EVENT surface only; `add_dependencies` does not exist, EV-35 has no
trigger. Decide: descope EV-35 (I update mapping/roadmap/functionality docs to mark it product-removed)
or re-file the option-1 prompt from phase2-required-changes.md. Nothing breaks Phase 4 either way.

### M10 (carry-over, [COPILOT]) — queue starvation fix
Filed with full paste prompt in `phase2-required-changes.md` (same file, M10 section). Unchanged:
dispatch failure must not head-block the FIFO queue; validate `assigneee_profile` at create.

### R1 [TEST-OWNER] ✅ DONE (2026-11-15) — verdicts after correct-paginated regrade
- S6-GATEWAY PROOF: 284 `noop-verification` rows (of 604 cal) — analyzer dedupes reissue fillers
  and records one designed-nothing row each; restart concern CLOSED (S5/S6/S7 live).
- AN-09 ✅: msg 308 (decision+owner+deadline) analysis importance exactly 4 (single bump).
- AN-15 ✅: 306/307 importance 1 `useless`, zero topic links/history side effects.
- TP-17 ✅+: zero `delete_topic` calls; msg-313 (delete-proxy ask) refused ~13 times with
  noop rows citing delete-discipline reasoning — textbook.
- TP-15 ✅-variant: genesis link on msg 309 exists but to EXISTING topic 13 ("Product Hunt
  Launch") — continuity-over-duplication preference. Note: analyzer-created "Churn Signal
  Tracking" (topic 44) vanished without any logged delete call between 02:36 and 07:30 —
  unlogged topic deletion flagged as observability gap O-1.
- RH-02 ⚠️ PARTIAL: fixture reseeded (topic 'proxy' 46, links 311+313, snapshot #77).
  Snapshot row is a POINTER (room/topic/last_state only) — no body/message set to compare
  fidelity against. Either the web snapshot carries content the API doesn't expose (O-2)
  or mapping wording needs relaxation.
- KN-04 ⚠️ PARTIAL: adoption activity exists ("adopted proposal 13... filed as knowledge item 1",
  actor w-ai, target_path = directory form). Proposals carry NO knowledge_path field to compare
  equality against — mapping precondition absent in data model; relax check or add field (O-3).
- KN-05 ❔ UNTESTABLE via API: knowledge_item has no family/badge semantics exposed
  (badge:null always); dual-fit routing cannot be graded from this plane (O-4).
- KN-09 ✅ FIXED + VERIFIED LIVE (2026-11-15, proc_b18b514ea1ff): seeded proposal #24 ("Cap guest
  tokens for eval users") -> dismissed via fixed API path -> asked w_ai to (re)propose the same
  thing. Result: NO new pending proposal (final state: only #24 dismissed), w_ai replied asking
  for new evidence (cap value, scope) and routed the ask as task 46 — the forbidden re-raise did
  not happen. Partial-deviation note: the reply asked for inputs rather than explicitly citing
  "dismissed #24" — acceptable handling, watch in Phase-4 correlation.
- KN-08 ✅ closed at S9 acceptance (citing item read back after msg-137 delete, no error).

---

## GOOD

### G4 [COPILOT, refactor] — one validation home per entity
F17/F18 both say the same thing: rules live in web controllers, API routes around them. Introduce
(or extend the pattern from M8's Recorder centralization) shared model-level validation + a parity
spec that runs the same assertions through web-service and API-service entry points.

### G5 [TEST-OWNER] — bot-emergent assertions for beats 307/313
Single-shot content beats don't get HI arcs; the w_ai "video idea verdict" and "wrap-up summary"
emergent replies belong to the Phase 5 cross-platform pass. Noted, no action now.

---

## Order & dependencies

1. ~~S9 / F17 / F18~~ — ALL MERGED+VERIFIED (adabe3a, e998f71, 6ed3905) as of 2026-11-15.
2. M10 remainder prompt (above) — next paste; small, self-contained.
3. M9 product decision — whenever, blocks nothing.
4. R1 re-test batch — S9 landed so KN-08 already closed; remaining: proxy fixture reseed + HA-65
   set-equality + attention-filter regrade (do before Phase 4 proper).
5. Gateway restart (S5/S6/S7 text already deployed) — independent; R1 step 4 verifies it.

Phase 4 (privacy & access battery) is NOT gated by any open item — GO.
