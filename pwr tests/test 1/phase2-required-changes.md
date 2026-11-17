# Phase 2 → required changes (Copilot code vs Hermes SOULs/skills), tiered

Source: results-scoreboard-phase2.md (PARTIAL PASS). Owner tags: [COPILOT] =
PWR repo code; [HERMES] = W-ai SOUL/skill edits + mirror deploy to loaded
profiles. Full paste prompts included for every [COPILOT] item — send them in
the listed order (M8 supersedes the F13/F14 paste in phase1-required-changes.md;
it is one stricter, merged PR).

---

## MUST

### M7 [COPILOT] — duplicate-claim dead-end: stalled dispatch groups never re-driven (F13b)
Why MUST: proven at production scale this session — 205 backlog events unrecoverable by
redeliver; my force-dispatch of groups 491–501 was the only way handlers received
blockers/confirms/proposals; several scoreboard rows are PARTIAL purely because of it.
Paste:
```
Work in /home/siavash/Documents/codes/Pavel/W/pwr, branch installation (HEAD b197057+).
Fix OutputEvents::ProcessAndDispatchJob#handle_claim (app/jobs/output_events/process_and_dispatch_job.rb):
the duplicate-member branch currently logs, resets the member's synced=false, and
returns — so redelivering an event whose group is stalled (status dispatching/pending
with no outstanding dispatch, or failed) can NEVER make progress. Observed at scale:
200+ events stuck for hours; only manual stage-:dispatch forcing recovered them.
Required:
1. In the duplicate branch, after resolving the existing group, check if the group is
   recoverable: status in (dispatching pending failed) AND its dispatch attempts are not
   actively outstanding (reuse the busy-path result-token freshness check from commit
   b197057: result.scheduled_at older than the retry delay => not outstanding; status
   failed => always recoverable).
2. If recoverable, enqueue the dispatch stage exactly once:
   OutputEvents::ProcessAndDispatchJob.set(wait: 5.seconds).perform_later(event.id,
   stage: :dispatch, dispatch_group_id: group.id) — stamp result.dispatch_queued_at so
   concurrent duplicate claims cannot stack enqueues (single-flight per window).
3. If the lead event is gone (nullified lead_output_event_id), pick any unsynced member
   as lead for the dispatch.
4. Also make handle_dispatch's guard precise: status 'dispatched' -> skip (as today);
   status 'dispatching' with stale token -> proceed (currently a redelivery mid-storm
   can be swallowed).
Tests (fail before): redeliver member of stale dispatching group -> one delayed dispatch
enqueued, event eventually synced=true on stubbed 2xx; fresh token -> NO stacking;
failed group -> recovered; lead-less group -> any member drives it; happy paths
unchanged (regression: full output_events suites).
Acceptance: after merge I will run: force nothing; POST redeliver on 3 stalled members;
within ~5 min each group must self-drive without rails-runner surgery.
Non-goals: don't touch merge-window semantics, dedupe keys, payload shapes.
```

### M8 [COPILOT] — event-emitter parity: API-plane updates + ALL pool-item creates must fire events (F14 + F14c)
Why MUST: six PARTIAL + two BLOCKED rows (EV-20 mention-created, EV-37/38, EV-04/05 via
API, company add) exist only because creation/API paths emit nothing; agents are blind to
half the platform. One PR covering all emitters.
Paste:
```
Work in /home/siavash/Documents/codes/Pavel/W/pwr, branch installation (HEAD b197057+).
Make event emission plane-independent (emitters move below controllers/services so every
plane fires them). Verified gaps this session:
A) ProjectTodo completion: events project_todo_completed/reopened are recorded ONLY by
   Users::Projects::TodosController#toggle. Move emission to a model callback
   (after_update_commit on completed? change) with data {project_id} and actor from an
   attr_writer set by callers (nil allowed, never User.first). Remove the controller's
   inline Recorder call (web tests must stay green). API PATCH /api/projects/:pid/todos/:id
   with completed=true/false must now fire.
B) AttentionItem: API PATCH changing status to resolved/dismissed bypasses resolve!/
   dismiss!. In Api::AttentionItemsController#update (and MCP edit attention if present),
   route those two transitions through the existing model methods (keep the plain-update
   path for other attrs). Idempotence: re-setting the same terminal status fires nothing.
C) Pool-item creates (F14c): add_knowledge_proposals, add_ai_confirm, add_mentions (and
   dependencies if it gains writes — see separate item) create AttentionItem rows but
   record NO event. Add an after_create_commit on AttentionItem emitting
   "<category>_created" via the same naming map as RESOLVED_EVENT_TYPES
   (mentions_created, ai_confirm_created, knowledge_proposals_created, blockers_created,
   risks_created...) with data {category, title, project_id, room_id}; skip when the
   creating actor is a Bot? NO — keep it simple: emit always; handlers decide.
   Confirm the workspace skill families can consume *_created (they already handle
   *_resolved/*_dismissed); record in the PR any handler naming assumptions.
D) CompanyStatusItem create: same pattern — risk_add/risk_update/<category>_created types
   fire from the API create path (today only update/destroy emit via record_action_event!).
Tests: each plane (web + REST + MCP) produces the event exactly once (shared callback,
no duplication); terminal-status re-PATCH silence; created events carry category payload;
full suite green.
Acceptance: after merge I re-run battery events for EV-20/EV-37/EV-38/EV-13 and expect
recorded events with ids in /api/output_events.
Non-goals: no new event TYPES beyond the <category>_created family + todo plane; don't
touch dispatch/job internals; no UI changes.
```

### M9 [COPILOT or PRODUCT] — dependency family has no trigger surface (F16)
Evidence: 'dependencies' MCP tool is read-shaped (no add_ variant; my call created
nothing and recorded no event) — roadmap EV-35 + HA-35 assume a created/broken/resolved
dependency family. Two options, needs your pick before paste: (1) add add_dependency /
edit_dependency MCP tools backed by whatever entity the fiction means (attention category
'dependencies' exists in the attention map? — if yes, reuse pool pattern from M8-C);
(2) descope EV-35/HA-35 items. If (1):
```
Work in /home/siavash/Documents/codes/Pavel/W/pwr, branch installation.
Add dependency pool surface: if AttentionItem.CATEGORY_CONFIG supports 'dependencies'
(not in the RESOLVED map today — decide: add category or new model) — implement the
smallest honest version: add_mentions-style MCP tool add_dependencies {title, meta_text,
project_id|project_name, room_id|room_name} creating the pool row + firing
dependencies_created (per emitter-parity PR M8 pattern), plus dependency_broken/
dependency_resolved event types wired to status transitions. Document the state machine
in the PR description and mirror the names into workspace skills list if any. Tests:
tool creates + event fires; resolved/dismissed fire *_resolved/*_dismissed; regression
green.
```

---

## SHOULD

### S5 [HERMES] DONE (2026-11-13, deployed+verified) — workspace skill worked-examples for the newly-visible event families
Files: W-ai/worspace profile/skills/... (input/action procedure skills) then mirror to
~/.hermes/profiles/workspace/skills/. After M8 fires *_created events, the workspace
profile has no procedure text for them — it will fail-closed into ambiguity handling.
Add short worked examples: mentions_created -> route to mentioned profile w/ ids
(EV-20 mapping text); ai_confirm_created -> present to human, do NOT auto-resolve;
knowledge_proposals_created -> dedupe-check vs existing summaries before adopting;
project_todo_completed/reopened from API origin -> tracker close semantics unchanged.
Deploy per w-ai-profile-mirror skill (backup + byte-verify), gateway restart to take.

### S6 [HERMES] DONE (2026-11-13, deployed byte-verified) — message_analyzer: make 'nothing' observable (correlation blind spot)
Phase-2 grading showed silent-correct handlers are indistinguishable from dead ones
(PARTIAL rows). Add to W-ai/message_analyzer/SOUL.md (mirrored to profile): when an
event is intentionally a verification-log-only outcome (EV-41 class), write ONE
create_tool_cal_log row {used_tool_name:"noop-verification", change_log:"<event id> ->
nothing by design"} — cheap observability that upgrades future correlation from PARTIAL
to verdictable. Right/Wrong example per authoring conventions.

### S7 [HERMES] DONE (2026-11-13, deployed to 5 profiles) — executor wake-check after approvals (EV-06 execution side)
Task-18/12 evidence shows raise+waiting perfect, but post-approve execution follow-through
(outreach template send, expense receipt filing) has only partial traces. Add to
bot-approvals SKILL.md Task-inbound section: on receiving YOUR approval's approved
decision event, you MUST (a) execute within approved scope, (b) file receipt/knowledge
artifact when the action is money/sending, (c) post completion message citing the
approval id (AP-14), before closing the task. Verify with targeted re-run after M7
(decision events will actually reach the assignee once dispatch self-heals).

### S8 [COPILOT, small] — flat GET /api/approval_requests/:id throws exception page
Found live: /api/approval_requests/1 -> HTML exception; nested list works. One-line
route/controller fix in the API approval resource (member GET mirroring the nested
serializer). Include in M8 PR or standalone:
```
Work in /home/siavash/Documents/codes/Pavel/W/pwr. Fix Api::ApprovalRequestsController
member GET: /api/approval_requests/:id currently raises (exception page). Wire it to the
same serializer as the nested list; 404 JSON for unknown id; add the two route tests.
```

---

## GOOD

G1 [HARNESS] correlation grader: match event text bodies (not just ids) and widen
window to 45 min — my own tooling upgrade for Tier-3/Phase-3.
G2 [PRODUCT] HA-28 result pending at time of writing; if the third raise is NOT gated,
add learnings-gate example to workspace skill (S5 file set).
G3 [OPS] dev ergonomics: document HERMES_MAX_ACTIVE_AGENTS meaning (live work-units,
counts this gateway's chat sessions) in ENVIRONMENT_VARIABLES.md.

---


### DONE-record S5/S6/S7 (2026-11-13)
S5: repo sources `worspace profile/skills/input/{mention,ai_confirm,knowledge_proposal,
project_todo_completed}.md` gained `*_created` procedure sections + API-origin note;
deployed as SKILL.md (frontmatter description now advertises the `_created` families) to
`~/.hermes/profiles/workspace/skills/input/{mention,ai-confirm,knowledge-proposal,
project-todo-completed}/`; 19 input skills load, byte-verified, .bak- files kept.
S6: `message_analyzer/SOUL.md` gained "Nothing-outcomes must be observable"
(noop-verification cal row + Right/Wrong examples); mirrored byte-identical.
S7: `bot-skills/bot-approvals/SKILL.md` Task-inbound rule 4 (execute -> evidence -> message
citing approval id -> cost -> close); mirrored to w_ai, coder, market_research,
business_analyst, project_manager (5/5 verified).
EFFECT PENDING: the gateway must be restarted by the operator from an external shell
(SOULs/skills are read at session start) — same procedure as the previous two deploys.
Acceptance re-runs after that: mention_created -> routed task citing event id;
ai_confirm_created -> surfaced, zero auto-resolve; moot event -> noop-verification row;
approval execute -> receipt -> close chain shows evidence before finished.

---


---

### M10 [COPILOT, small] — dispatch-failure poisons the whole task queue (FIFO head retry)

`AiTaskDispatcher#dispatch_next_pending_task!` takes `AiTask.where(dispatched: false).order(:created_at, :id).first`
and on `Hermes::Client` failure logs + returns nil WITHOUT setting `dispatched` — so a task whose
`assigneee_profile` is unreachable (e.g. profile "planner" does not exist on the gateway) is retried
forever AND blocks every newer task behind it. This exact state (task 34 failing dispatch inside
`AiTaskDispatchPollJob`, poll loop `ai_task_dispatch_loop.rb:13`) was the runtime context when the
output-event ledger wipe (incident I2) happened.

Required behavior:
1. On dispatch failure: increment `dispatch_attempts`, set `dispatch_error` text; after N (default 3)
   consecutive failures mark the task failed-with-visibility (attention item or status flag) so the
   queue advances. Manual retry = admin resets attempts.
2. Unit test: task A (bad profile, 3 failures) then task B (good profile) — B must dispatch while A
   remains failed; assert A marked after 3 strikes.
3. `create_ai_task` should validate `assigneee_profile` against the gateway profile list when reachable
   (422 on unknown profile); if gateway down, accept.

Paste for Copilot:
"Fix AI task dispatch queue starvation: AiTaskDispatcher#dispatch_next_pending_task! retries the oldest
undispatched task forever on transient Hermes failures and blocks newer tasks. Add dispatch_attempts and
dispatch_error columns on AiTask; after 3 consecutive failures mark the task failed-with-visibility and
move on. Validate assigneee_profile in create_ai_task against the gateway profile list when reachable
(422 on unknown profile). Write the two-task starvation test (bad-profile task must not block
good-profile task)."

---

## Incidents during verification window (2026-11-13 ~15:00-17:00 UTC)
I2 — OUTPUT-EVENT LEDGER WIPED (~16:44): `output_events` + `output_event_dispatch_groups`
reduced to the 4 newest rows; earlier 470+ rows gone. Evidence: paired
`OutputEvent Delete All` + `OutputEventDispatchGroup Delete All` in development.log.
ISSUER LOCALIZED: both DELETEs are logged INSIDE AiTaskDispatchPollJob, mid-loop at
app/services/ai_task_dispatch_loop.rb:13 (between AiTask loads) — the APP process ran them.
Current HEAD has no delete_all anywhere, and a fresh invalid-profile dispatch failure
(task 35) does NOT reproduce it -> best fit: a transient reloaded code state (Copilot
work-in-progress on the dispatch/M7 path) wiped the event ledger inside the poll loop,
and that version is gone from the final commits. Poison tasks 34/35 (profile 'planner'
does not exist; dispatch fails every poll cycle) were closed post-incident so the loop
never re-enters the state that coincided with the wipe; a third wipe during Phase 3
would disprove the transient-code theory and escalate as a live bug. WORLD INTACT (users/projects/
rooms/messages/decisions unchanged); event ledger is a disposable transport log and all
Phase-2 grading artifacts (ledgers, correlation.json, scoreboards) were written BEFORE
the wipe. DB snapshot kept at ~/.hermes/cache/scratch/pwr-db-snapshot-1647.sqlite3.
ACTION: Phase 3 regenerates its own events from zero; if a second wipe happens mid-run,
correlate timestamp + escalate to whoever operates consoles. (An earlier "messages
279->222" scare was MY misread — truncated curl output cut the count digits; retracted.)

---

## Order & dependencies
1. M7 first (unblocks honest delivery for everything else; my PARTIAL rows re-grade after).
2. M8 next (creation/API events; S5 must land with it — workspace needs procedures before
   new event types hit it, else it drowns in unhandled types).
3. M9 after your scope decision.
4. S5/S6/S7 SOUL edits + mirror deploys (one batch, gateway restart).
5. S8 small PR anytime.
6. Then: re-grade EV-20/26/35/37/38 + Tier-3 execution (specs ready in mapping §M/§P).
