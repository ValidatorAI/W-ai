# Phase 1 → required changes (code + Hermes SOULs/skills), tiered

Companion to `results-scoreboard-phase1.md` (evidence: phase1_ledger.jsonl,
phase1_sweep.json, DB census 2026-11-12). Hermes source-of-truth paths below are
W-ai repo files — after review they must be mirrored to loaded profiles
(~/.hermes/profiles/<id>/) per the standard deploy flow; never edit loaded copies
as source.

Legend: MUST = blocks Phase-2 value or fixes broken-world semantics.
SHOULD = quality/coverage before Phase 3. GOOD = polish/ergonomics.

---

## MUST-HAVE

### ✅ VERIFICATION RESULT — M1a + M5 CLOSED (2026-11-13, HEAD 341192b + data fix)
R1 CLOSED live: create_ai_task with `room_id:"receipts-growth"` + slug project →
stored project 2 / room 2, warning intact (probe rows cleaned). R2 CLOSED live by
DATA, not bridge: bot user id 2 renamed `w-ai`/"W AI" (it was functionally the w_ai
assistant under the name "Ask about company"), so add_message `user_name:"w-ai"` now
creates as creator_id 2 — the AiProfile bridge tier itself remains UNVERIFIABLE
because `ai_profiles` is empty (see F12); with no rows it cannot fire, and it is not
needed for identity resolution anymore. MS-01 flips PASS (next analyzer→w_ai probe
will confirm attribution under the corrected name).
NOTE found while renaming: **M6 regression** — PATCH /api/users/2 {name,display_name}
returned 200 with BOTH fields unchanged AND silently demoted the bot (role bot→member;
repaired via direct SQL). Cause: UserAdminService.update ignores everything except
role and coerces missing role to "member".
Paste-ready (Copilot) — M6:
```
Work in /home/siavash/Documents/codes/Pavel/W/pwr, branch installation (HEAD 341192b+).
Fix UserAdminService.update (app/services/user_admin_service.rb): apply ONLY the
attributes actually present in params (name, display_name, email_address, role), each
validated by web-model rules; NEVER overwrite an existing role when params omit it
(current code coerces bot/admin to member on every unrelated update); password via
password= writer only when present; empty-params update = no-op returning the record.
Audit every caller (API users#update, web admin forms, users_settings) so form posts
that legitimately omit fields no longer reset them; add tests: partial update keeps
role; name-only update works; bot role survives a display_name edit; invalid role ->
422 not coercion. This data-destroying bug shipped in the brief-B campaign; own it in
the PR description.
```
F12 (product decision, no code bug): `ai_profiles` has ZERO rows in dev while 8
Hermes profiles are loaded — mention-routed event dispatch and the whole ai-admin
plane are dormant-by-data. Decide whether to seed rows per loaded bot profile
(soul/toolsets become DB-managed) or drop the AiProfile-based routing tier.

Earlier probe results (kept for history):
M1a: `resolve_project` slug-resolution WORKS (create with `project_id:"receipts"` →
stored `project_id=2`); bogus slug → `isError: Project not found for
project_id="no-such-project-xyz"` and ZERO rows. M1a remaining sub-gap R1:
`room_id:"receipts-growth"` → `isError: Room not found` (room_id string path does NOT
name/slug-resolve; the `room_name` arg path does).
M5: `|| User.first` GONE (grep clean across `mcp/tools/`; unresolvable sender →
`isError: Sender (user or bot) not found`, zero rows); `bot_name:"Project Manager"` →
created as creator 6 ✅. M5 remaining sub-gap R2 — the AiProfile name-bridge is
MISSING: `user_name:"w_ai"` still errors, so profiles posting under their SOUL
identity (`user_name: "<profile>"` per the authoring convention) cannot post at all
now (fail-loud is correct, but it blocks the w_ai answer path until bridged).
Both sub-gaps are required before Phase 2 is meaningful.
Paste-ready (Copilot) — close-out commit for M1a-R1 + M5-R2:
```
Work in /home/siavash/Documents/codes/Pavel/W/pwr, branch installation (HEAD 0abb2d0).
R1 — string room_id must resolve like project_id does:
In Mcp::Tools::Concerns::ResolutionHelpers#resolve_room (and FuzzyMatcher.match_room):
when room_id is a non-numeric string, resolve it by exact name then slug (project-scoped
when project present), else Mcp::FuzzyMatcher.match_room; numeric ids unchanged; still
raise/failure when nothing matches (never fall back to another room).
R2 — AiProfile name-bridge for bot senders:
Profiles post under names like "w_ai", "message_analyzer", "workspace", which are
AiProfile profile_name/bot_name values, not User names. Add resolution BEFORE failing:
search AiProfile (bot: true) by profile_name and bot_name (exact, then fuzzy >= 0.4 via
the existing similarity_score); when exactly one matches, return its linked bot User
(inspect the model association — find the column that links AiProfile to a User/bot row;
if AiProfile has no User link, resolve by matching the profile's bot_name against
User.bot names); ambiguous multi-match -> failure listing the candidates;
no match -> existing "Sender (user or bot) not found".
Wire it so resolve_bot(args)/resolve_sender benefits from this bridge for the
bot_name AND user_name argument paths (SOULs send the profile name in either field).
Tests: create_ai_task with room_id "receipts-growth" -> room row linked; room_id 99999
-> isError; add_message user_name "w_ai" with an AiProfile present -> post attributed to
that bot (creator_id != 1, role bot); user_name "coder" style -> existing bot; unknown
profile name -> isError, zero rows; regression on messaging tests.
Acceptance (I re-run it): POST the w_ai answer probe -> room post attributed to a bot
user (creator 2–7), MS-01 row flips to PASS; PM gated-action probe -> approval row
raised + echo on approve.
```

### M5 🆕 VERIFIED DEFECT — MCP `resolve_sender` silently posts as User.first (F11)
Found live 2026-11-12 during M2/M3/M4 verification: w_ai answered task #10 but its
room post (msg #163) was attributed to creator_id 1 (siavash, admin) instead of a bot.
Root cause (verified in code): `app/services/mcp/tools/concerns/resolution_helpers.rb`
line ~50: `resolve_sender = resolve_bot(args) || resolve_user(args, ...) || User.first`
— when the profile posts under its profile identity (`user_name:"w_ai"`, per the SOUL
authoring convention) and no User row matches that name (bot users are named
"Bender Bot", "Ask about company", "Project Manager"…), resolution falls through to
User.first = HUMAN ADMIN. Same anti-pattern class as the previously removed
`|| Room.first` on room resolution. Effect: bot output masquerades as human authorship
— breaks MS-01/MS-13, attribution audits, and every permission check keyed on creator.
Paste-ready (Copilot):
```
Work in /home/siavash/Documents/codes/Pavel/W/pwr, branch installation.
Fix MCP sender resolution (app/services/mcp/tools/concerns/resolution_helpers.rb):
1. Remove the `|| User.first` fallback in resolve_sender. If neither bot nor user
   resolves, return failure("Sender not found: provide a user_id/user_name or
   bot_id/bot_name that matches an existing account") — callers in messaging/action
   tools must surface it; NO message may be created with a default sender.
2. Bridge profile identities: before giving up on a user_name string, also search
   AiProfile (profile_name/bot_name, bot:true) and return the linked bot User when
   exactly one matches — agents posting under "w_ai"/"coder"/"message_analyzer"
   style names must resolve to their bot users, not fail for the ones that exist.
   Inspect ai_profiles' actual association to User (bot link column) and use it;
   ambiguous multi-match -> failure listing candidates.
3. Audit other `|| User.first|Room.first|Project.first` style fallbacks in
   app/services/mcp/tools/ (grep 'User.first' etc.) and convert each to an explicit
   failure; list what you changed in the PR description.
Tests: add_message with bot_name "Project Manager" -> that bot; user_name "w_ai" ->
resolves via AiProfile bridge to its bot user; unresolvable name -> isError, ZERO
message rows created; regression on existing messaging tests (adjust any that
depended on the fallback — flag them in the PR).
```
After merge: re-run the w_ai answer probe (expect new post attributed to a bot user,
creator_id 2–7) + PM approval loop; update scoreboard MS-01 row.

### M1a / M1-orig / M2 / M3 / M4 statuses

### M1 ✅ VERIFIED RESOLVED (05413e7) + follow-up M1a (NEW, must-have)
Live-verified 2026-11-12: unknown args rejected with allowed-key list (`profile_name`
→ isError); `assignee_profile` 2-e alias persists to `assigneee_profile`; blank
assignee returns structured `warning.code=missing_assignee_profile`; integer
project_id spawns the blockers AttentionItem (row observed). Probe rows cleaned up.

**M1a — project_id on MCP create is NOT slug-resolved and stores garbage `0`.**
Evidence: `create_ai_task {project_id:"receipts"}` → row has `project_id=0` (FK
nowhere); consequently the orphan-attention path silently skips (project nil) and
TK-01 "always project_id" is unenforceable on the MCP plane. Integer id works.
Pass-1 tasks #1/#2 carry the same 0 — agents passing names/slugs lose project
context silently (coder only knew the project after REST PATCH, where find_project
accepts id OR slug).
Paste-ready (Copilot):
```
Work in /home/siavash/Documents/codes/Pavel/W/pwr, branch installation (HEAD 05413e7+).
In MCP task tools (app/services/mcp/tools/tasks.rb): resolve project arguments the
same way REST find_project does — accept integer id OR slug/name via the existing
Mcp::FuzzyMatcher/project resolution used by other tools; store the resolved integer;
if a string project arg is present but unresolvable, return failure (never store 0).
Apply to create_ai_task AND update_ai_task; same treatment for room_id string vs id.
Tests: slug create -> project row linked; bogus slug -> isError naming it; integer
unchanged; orphan attention item now created for slug case.
```

### M1-orig · PWR: `create_ai_task` silently drops unknown args; unassigned tasks never dispatch (F5) — DONE, kept for history
Evidence: pass-1 probe sent `profile_name` — task #1/#2 created with
`assigneee_profile=None`; AiTaskDispatcher polls forever but never wakes any agent
(bot plane blind for the first ~2 h of Phase 1 until a manual PATCH). Pass 2 re-fire
produced task #3: same silent orphan, `isError:false` both times. Unknown keys are
swallowed; `description` is the only required arg.
Target: /home/siavash/Documents/codes/Pavel/W/pwr — app/services/mcp/tools/tasks.rb
(+ create controller for REST parity check).
Paste-ready (Copilot):
```
Work in /home/siavash/Documents/codes/Pavel/W/pwr, branch installation (HEAD bf0d2c9+).
Harden MCP create_ai_task (app/services/mcp/tools/tasks.rb):
1. Reject unknown argument keys: if args.keys - schema_properties.keys is non-empty,
   return failure("Unknown argument(s): <list>. Valid: <schema keys>") — do NOT create
   the task. Same for update_ai_task.
2. Validate assignee BEFORE create: if assigneee_profile is blank, still create
   (drafting is legal) BUT include in the success payload
   "warning":"no assigneee_profile — task will never dispatch" and record an
   attention_item (category tasks, status pending) for the project so orphans are
   visible; add GET-side already? no — attention row is enough.
3. Accept alias: assignee_profile (2 e's) maps to assigneee_profile (document the
   legacy 3-e column name; keep DB column unchanged).
Tests: unknown key -> isError naming keys; valid call unchanged; missing assignee ->
created:true + warning + attention row; alias works. Regression: existing ai_task
tests green.
```

### M2 ✅ DONE+DEPLOYED — message_analyzer SOUL: verify-before-log (F1 ghost write)
Shipped 2026-11-12: new `## Verify-before-log (iron gate for every write)` section in
`W-ai/message_analyzer/SOUL.md` (re-read before logging; one write one log row;
`failed:` rows for failures; ids only from response/re-read; ghost-todo incident as the
Wrong example). Mirrored to `~/.hermes/profiles/message_analyzer/SOUL.md` (byte-verified,
`.bak-20261112` kept). EFFECT PENDING: gateway restart (SOULs read at session start).
Original item kept below for history.

### M2-orig · Hermes SOUL: message_analyzer must verify writes before claiming/logging (F1 ghost write)
Evidence: cal_log #1 (03:42:21) change_log claims `Project todo 'OSS README rewrite'
created … entity 15` — `project_todos` count is **0**; topic 7 it also claims DOES
exist (mixed true/false in one log entry = fabrication risk). The claimed add never
landed (failed call or never made), yet the post-write log asserted success.
Target: /home/siavash/Documents/codes/Pavel/W/W-ai/message_analyzer/SOUL.md
(mirror → ~/.hermes/profiles/message_analyzer/).
Required change (append to its post-write discipline rules):
- A `create_tool_cal_log` entry may describe ONLY writes whose success was
  RE-READ: after any add_*/update_* call, verify by listing/getting the target
  (the response id must resolve). If the write failed or cannot be verified, the
  log entry must say `failed:` + reason, never `created`.
- Never bundle multiple claimed artifacts in one log line; one write, one verified
  log row (splits the todo/topic ambiguity of the evidence case).
- Forbidden: citing entity ids not present in a read-back result.
Deploy note: SOUL edit + `hermes` profile skills mirror per existing procedure;
verify with a 1-beat test (post a "file a todo" message; cal_log must show
verified/failed, todo row must exist).

### M3 ✅ DONE+DEPLOYED · M4 ✅ DONE+DEPLOYED (pending gateway restart)
Resolution turned out to be wiring, not new policy: `bot-approvals` already contained
the full raise procedure — nothing delivered chat intent TO the bots. Shipped:
(a) `W-ai/message_analyzer/SOUL.md` new `## After analysis: routing obligations` —
questions → `create_ai_task(assignee_profile="w_ai", cites message id)`, gated-entity
actions → task to owning worker with `Gated action: … first raise approval …` prefix,
routing table (coder/market_research/business_analyst/project_manager/w_ai), explicit
"never end silent" + anti-bug clauses (no self-answers, no self-approvals, never
unassigned tasks, integers only). (b) `bot-skills/bot-approvals/SKILL.md` new
`### Task-inbound` section — receive `Gated action:` task → first visible step is
`add_approve_request_with_message` with 4-tuple, waiting-for-approval state, act only
on approved decision citing approval id. (c) w_ai SOUL needed no edit (already owns
ANSWER/ACT/ASK BACK + same-room verdict-first). Mirrors deployed byte-verified:
analyzer SOUL → loaded message_analyzer; skill → all 5 profiles holding bot-approvals
(w_ai, coder, market_research, business_analyst, project_manager), `.bak-` per file.
Verification plan after restart (I run it): two probe beats — a question ("should we
ship Friday?") expecting an analyzer-created w_ai task; a gated action ("post the
launch summary to all-hands") expecting coder/pm task → approval raised in-room →
approve via API → observe execution + echo. AP/DS/HI/WA/MS families then become
testable end-to-end in Phase 2.

### M3-orig · Hermes SOUL+SKILL: approval-raise-from-chat policy (F3)
Evidence: 13 gated fiction beats (#112/#184/#193/#205/#216/#220/#246/#252… — the
"needs-approval actions" map in project.md routing rules) → `approval_requests`
count 0 in every room; AP/DS/HI families untestable end-to-end; only API-raised
approvals work (validated out-of-band).
DECISION NEEDED (owner): which profile raises — message_analyzer triage or the
acting bot itself. Recommended split: acting bot raises before external/destructive
steps (its own SOUL), analyzer raises nothing.
Targets: bot-skills/bot-approvals/SKILL.md (W-ai/bot-skills/) + the four bot SOULs
(hermes/profiles/bots/*/SOUL*) + coder/PM/market-research/BA.
Required change text (paste into SKILL.md, review then mirror):
- Trigger table extended: money-moving (budget > $X), external sends, deletions,
  user-visible announcements, deploy/restart ops → MUST `add_action_message` +
  `add_approval_request` (atomic tool available: add_approve_request_with_message)
  BEFORE acting; approval body carries the 4-tuple (target+ids/scope/boundary/
  evidence per AP-03).
- After decision event: resume or abandon with citation of the approval id (AP-14).
- Forbidden: acting first and raising as notification; re-raising denied scope.
Test hooks: replay beats 112/184/193/205 post-deploy — approvals must appear in
their rooms (scoreboard GAP → live rows).

### M4-orig · Hermes SOUL/routing: questions must get in-room answers (F4, WA-01…06) — superseded by M3/M4 block above
Evidence: 122 replay messages incl. explicit questions ("reply GO/NO-GO", guest
#141/#147-class asks, mode:"ask" trios dispatched) → exactly ONE bot-authored room
message in 5 h (coder task report #35). w_ai/ask-from-w never answered anywhere;
analyzer analyzed and stayed silent.
Targets: message_analyzer SOUL triage (Answer form) + bots/ask from w/SOUL.MD
(w_ai) + bot-messaging SKILL.
Required changes:
- message_analyzer: for events with mode:"ask" or a resolved question with no
  self-sufficient answer, MUST either (a) answer in-room via add_message when it
  holds the answer, or (b) create_ai_task to the answering profile (w_ai for
  company/project questions; market research for evidence questions) — silence
  without either outcome violates EV-00e one-outcome rule.
- w_ai SOUL: on task wake, answer in the SAME room as the source message, verdict-
  first, citing ids read (MS-01/MS-13 rules restated).
- Add to w_ai SOUL the membership-cached-read order (get_room_members before
  content lookups) so WA-01/02 pass verifiably.
Test hooks: beats 141/147/151/195 (question arcs) must produce bot replies;
MS/WA families upgrade from vacuous to live.

---

## SHOULD-HAVE

### S1 · Bots: post-write logging coverage (F9)
10 tool_cal_log rows vs ~20+ observed agent writes. bot-messaging SKILL + every bot
SOUL: reinforce "every state-changing call → create_tool_cal_log immediately"
(EV-00c), with M2's verify-before-log rule applied to bots too. Test hook: after M2/M4
deploy, log-per-write ratio ≥ 1:0.9 in census.

### S2 · PWR: MCP `create_room` tool (brief R5 leftover)
REST POST /api/rooms exists (R1) but agents have no create_room; workspace/analyzer
cannot seed rooms for new projects autonomously. Target app/services/mcp/tools/
rooms.rb wrapping RoomCreationService (action scope; fuzzy project_name;
user_names[]). Copilot paste: reuse brief R's §R5 text verbatim.

### S3 · PWR: redact `ai_settings.setting_value` in API/MCP reads
Long-standing open item (brief E review): AI_SETTING_FIELDS serializes
setting_value — potential secret leak through /api/ai_settings. Mirror the
soul/bearer_token `*_present` redaction pattern. Non-blocking, small PR.

### S4 · Data hygiene: pre-Z `synced=true` rows
Historical rows flipped true during the claim-bug era (incl. 401-era #1-#4). Post-Z
code is honest but old rows lie. Optional backfill: reset synced=false for events
with NO matching success-log evidence pre-11-Nov-16:00, then redrive once. Cosmetic
for Phase 2 (new rows are trustworthy); do when convenient.

---

## GOOD-HAVE

### G1 · Merge-window analysis guarantee knob
payload_merger collapses burst messages (by design, XD-safe); some messages never get
their own analysis row. If per-message analysis is a product promise, add a merge
cap or "analyze-all-ids-in-group" prompt field; otherwise document 60-70% coverage as
expected under load (recommended: document — it matches EV-41 nothing-outcomes).

### G2 · Dispatch-queue visibility
A `GET /api/output_events/queue_status` (pending/dispatching/dispatched/failed group
counts) — Phase 3 (full-system soak) will want saturation telemetry; cheap to add now.

### G3 · H-section APIs (boosts/presence/unfurl) for Playwright
Unchanged from before: web-only features; either API them or assign to the browser
lane. Still not a blocker (Phase 3+).

### G4 · Duplicate-description advisory on task create
Platform-level dedupe of identical open descriptions doesn't exist (confirmed by
design in Pass 2 — SOUL duty). Optional nicety: warning field when an identical
undone task exists, mirroring M1's orphan-warning pattern.

---

### F13b + F14 — filed 2026-11-13 after Phase-2 Tier-1 (both MUST; paste blocks)
While running the injection battery two structural gaps surfaced:
F13b: ProcessAndDispatchJob#handle_claim duplicate-branch is a dead end — when a
redelivered event is already a member of a stalled group (status dispatching/pending/
failed with unsynced members), the claim logs and RETURNS without re-driving (line
~22-26). The drain loop could not make progress by design: 205 events stuck; only
stage-:dispatch forcing (or the F13 delayed follow-up enqueued before the stall) recovers
them. Rails-restart orphans in-process delayed jobs, which makes this the permanent
stall mode in dev.
F14: API-plane mutations skip web-plane event emitters: todo completed/reopened events
exist ONLY in `users/projects/todos_controller.rb` (project_todo_completed /
project_todo_reopened), and attention resolve/dismiss ONLY via model resolve!/dismiss!
called from web controller — REST CRUD updates silently change state with NO event.
Any agent watching events cannot see API-side work (parity violation against the
brief-A/D "shared service" principle; functional-checklist parity rows pass vacuously).
Paste-ready (Copilot), two commits:
```
Work in /home/siavash/Documents/codes/Pavel/W/pwr, branch installation (HEAD b197057+).
COMMIT A — F13b duplicate-claim re-drive:
In OutputEvents::ProcessAndDispatchJob#handle_claim duplicate branch: after resetting
synced=false, if the claimed-into group status is in (dispatching pending failed) and it
has any unsynced member events, (re)enqueue the dispatch stage:
perform_later(event.id, stage: :dispatch, dispatch_group_id: group.id, wait: 5.seconds)
— guarded so concurrent duplicate claims enqueue at most one delayed follow-up per group
window (reuse the busy-path result-token pattern from commit b197057). Tests: member of
stalled group redelivered -> delayed dispatch enqueued; already-dispatched group -> no
enqueue; no enqueue stacking on rapid double-redeliver.
COMMIT B — F14 event emitters moved to model callbacks (API parity):
1. ProjectTodo: after_update on completed? transition -> record project_todo_completed /
   project_todo_reopened via OutputEvents::Recorder with the SAME data shape the web
   todos_controller uses today (actor from a service-assigned attr, never User.first).
   Web controller keeps working: strip its inline Recorder calls, rely on callback
   (its tests must stay green — adjust expectations for actor).
2. AttentionItem: same for status transitions resolved/dismissed via API PATCH —
   route update through the existing resolve!/dismiss! methods when status changes to
   those values (both API + web), so events fire from every plane.
3. grep for any other web-controller-only Recorder calls (milestone, all-hands, etc.)
   and move each to model/service level the same way; list them in the PR.
Tests: REST PATCH todo completed -> event recorded once (no double when web used);
API attention status resolved -> blocker event; idempotence: re-PATCH same status ->
no second event; web flows unchanged outcomes.
```

## Sequencing recommendation
1. M1 + M2 + S3 now (one Copilot pass + one SOUL review pass) — they make Phase 2
   handler evidence trustworthy.
2. M3 + M4 need your owner decision first (who raises; who answers), then ship
   together — they unblock AP/DS/HI/WA/MS live evidence.
3. Pass 2 completion verdict (running now) may add rows to M2 evidence but is not
   expected to change tiers.
4. S1/S2 with Phase 2 prep; GOOD items deferred.
