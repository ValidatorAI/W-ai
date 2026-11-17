# Transcript v2 — the completing replay: chats + probes that validate ALL remaining semantic & functional tests

> Together with `pwr-feature-test-conversations.md` (v1, ids 101–261), this file
> closes every gap: the **107 unmapped semantic items** of
> `pwr-semantic-checklist.md` and the **≈130 unmapped functional items** of
> `pwr-functionality-checklist.md`. Final coverage map in §K asserts nothing is
> left unassigned.
>
> Two element kinds:
> - **Chat ids 262–334** — real messages continuing v1's SHARED `messages.id`
>   table (higher id = later; ids 265–301 are reserved slack for late additions),
>   posted in the same four rooms (21 build, 22 growth, 23 founders, 24 partners).
> - **HA-nn harness actions** — the non-chat moves (API calls, event injection,
>   process kills, fresh installs, timing). Chat alone cannot validate
>   negative/permission/infra behavior — this is the honest completion layer.
>   Each HA names WHERE it fires (a room's timeline, or system context).
>
> **Pass model:** every element row carries `tests:` = the checklist ids it
> validates. An element passes when its desired state change (or required
> ABSENCE) is observed in PWR (SQL, tool_cal_logs, MCP reads, or web views).

---

## Act D6 — Platform & protocol hardening (PRE · PRO · AUT · REG · MSG · SRCH)

### Chats

| id | room | actor | message | tests |
|---|---|---|---|---|
| 262 | 21 | roya | brb, coffee | AN-02 (importance exactly 1), AN-15 (stop-after-1 absence) |
| 263 | 22 | kian | thanks all 💪 | WA-10-style social absence, AN-15 |
| 264 | 21 | roya | decision: we keep pricing hold until PH verdict AND kian, ship the FAQ by Friday | AN-09 (decision+owner+deadline → +1 ONCE, not +3; lands at 4 not 5) |
| 302 | 22 | kian | https://news.ycombinator.com/item?id=41… (real link) | MSG-17 unfurl/opengraph asset created |
| 303 | 21 | coder | `<pre>` unicode stress: تحققت از سیستم — emoji 🎯 zero-width — `null` bytes safe `<script>alert(1)</script>` | INV-05 (script sanitized), INV-06 (Persian/emoji/unicode round-trip in body + search) |
| 304 | 21 | kian | (posts the 1.2 MB log file as one message body) | PRO-10 (big body survives; DB row intact) |
| 305 | 24 | w_ai | @kian123 nonexistent-user-mention (again, deliberately) | REG-03 (clean not-found, message still posts) |

### Harness actions

| HA | fires at | action | desired state change = validated | tests |
|---|---|---|---|---|
| HA-01 | before replay | boot app from clean clone with `.env` per PRE-01..03 assertions; verify puma cwd/DB mtimes | env consumed, `/up` 200, DB file is the live one | PRE-01, PRE-02, PRE-03 |
| HA-02 | start | `GET /mcp/health` | 404 confirmed → README-fix ticket raised | PRE-05, INV-12 (doc parity, first entry) |
| HA-03 | before 262 | JSON-RPC `initialize` on all 6 endpoints | protocolVersion + capabilities.tools present on each; session ids distinct | PRO-01 |
| HA-04 | with HA-03 | follow-up call missing `Mcp-Session-Id` | rejected (assert exact error shape) | PRO-02 |
| HA-05 | mid-D6 | `tools/list` per endpoint | counts == baseline 163/142/78/29/8/16 | PRO-03 |
| HA-06 | mid-D6 | compare tools/list names vs aliases registry dump | zero alias names in listings | PRO-04, INV-10 (alias drift battery: the 4 audit aliases still CALLABLE) |
| HA-07 | mid-D6 | tools/call with Accept: json then event-stream | both succeed per contract | PRO-05 |
| HA-08 | mid-D6 | send `{"foo":1}` (no method) to /mcp | JSON-RPC error, no HTTP-500 page | PRO-06 |
| HA-09 | mid-D6 | call `no_such_tool` | structured not-found **and** call logged (or explicitly not — assert actual) | PRO-07 |
| HA-10 | mid-D6 | call `get_projects` via its alias | same result as canonical | PRO-08 |
| HA-11 | mid-D6 | hammer /action-mcp with 20 parallel calls, 2 sessions | no cross-session context bleed in responses | PRO-11 |
| HA-12 | mid-D6 | POST all 6 endpoints with no auth header / wrong token | 401 both cases, message identical (no oracle) | AUT-01, AUT-02 |
| HA-13 | mid-D6 | restart with `DISABLE_API_ROUTES=true` | /api/* 404, /mcp alive; `false` restores | AUT-03 |
| HA-14 | mid-D6 | session attached to /read-mcp calls `add_message` | SERVER rejects (scope enforced server-side, not by config filter) | AUT-04 |
| HA-15 | mid-D6 | nimbus(11) queries room 21 content via w_ai (chat trigger 305 later; probe here direct) | non-member content unreachable | AUT-05, ST-09 |
| HA-16 | continuous | sweep: every mutating call has identity in tool_cal_logs | 100% attributable; bot vs human uid correct | AUT-06, INV-01, MS-11-audit |
| HA-17 | mid-D6 | `get_users(user_name="KIAN M. ")` + `get_users(user_name="kia")` + two same-name users seeded | ambiguous→candidates error, prefix→resolve, garbage→not-found | REG-01 re-check, REG-02, REG-03 |
| HA-18 | end-D6 | `delete_tool_cal_log` on a row that has dependents / on fresh restart | immutability policy observed + documented; registry intact after restart (all tools present) | REG-06, REG-07 |
| HA-19 | end-D6 | create child/thread room of 21; check membership inheritance | thread room behaves per model | MSG-02 |
| HA-20 | end-D6 | history reads with pagination (200+ msgs incl. v1+v2) | window semantics, no cap surprises | MSG-16 |
| HA-21 | end-D6 | presence set/clear via API (⚠ confirm no-MCP) + boost a message via web | behaviors as ledger says (UI/API-only) | MSG-13, MSG-14 |
| HA-22 | end-D6 | post message via human web edit (⚠ edit_message MCP-absent) + delete by NON-author | edit via web works, MCP absent recorded; unauthorized delete refused | MSG-07, MSG-08 |
| HA-23 | end-D6 | SRCH battery: `search_rooms` as nimbus; `search_messages_of_room` after 303 (unicode+script); injection strings `' OR 1=1` | scoping correct; unicode hits found; no 500s | SRCH-01, SRCH-02, SRCH-03, SRCH-04 |

## Act D7 — Event-injection day (the 46 EV items + OR/XP twins)

> Method (this Act validates workspace's event-handling SOUL): every trigger
> below is a REAL mutation (web/API) that makes PWR emit the outbound event;
> the workspace profile must react per its input skill. Each has a **negative
> twin**: the forbidden artifact must NOT appear. Dry-run-first convention (HR-01)
> applies to each.

| HA | event triggered by | expected workspace reaction (+ absence) | tests |
|---|---|---|---|
| HA-24 | redeliver event E twice, same group_id/event_type/event_id | 1 artifact only; tool_cal_logs shows the stop-check | EV-00b, XD-10 |
| HA-25 | inject event with UNKNOWN room/profile target | clarification task or minimal action — no guessed identity; no social reply | EV-00d, EV-00e (one outcome per event) |
| HA-26 | human creates + approves `ai_confirm` then RESOLVES it | trackers closed cost→finished; propagate only if action was partial | EV-01, EV-02(first half), OR-05 |
| HA-27 | DISMISS that `ai_confirm`; artifact was w_ai-created, other was coder-created | deletes ONLY own artifact; coder's → revert task routed to coder | EV-02, EV-03, EV-04 |
| HA-28 | reject same artifact type twice → third auto-create attempt | learnings item exists once; no third create | EV-03, KN-09 |
| HA-29 | resolve blocker 122-style via web | "can proceed" merged into referencing tasks (merge-not-replace); owner's blocked work with no task → resume task | EV-04, TK-15 twin |
| HA-30 | DISMISS a blocker | tasks annotated "dismissed <date> by <actor>" — wording audit (not "cleared") | EV-05 |
| HA-31 | resolve decisions_waiting item carrying a durable decision | ADR-007 created AFTER project_decision_records dedupe list; status accepted | EV-06, DS-04 (content fields) |
| HA-32 | fire decision_approved from each of the 3 flows (ApprovalRequest / CompanyStatusItem / AttentionItem) | three different handlers observed (route by target_type, not event name) | EV-07, OR-02 |
| HA-33 | approve company-level decision | current-period decisions item mirrored (correct company_status_period_id, ST-10 pairs) | EV-08 |
| HA-34 | dismiss a decision | referencing tasks annotated; ZERO task deletes | EV-09 |
| HA-35 | create then break then resolve a company-status dependency | consumer notes merged in, coordination task to provider profile once, broken → blocker after dedupe, resolved → precondition cleared by merge | EV-10, EV-11, EV-12, EV-00a |
| HA-36 | change status item → duplicate attempt | single material_changes item citing change id; meta_text complete | EV-13, AT-06 |
| HA-37 | delete that change item | own footprints annotated "re-validate" | EV-14 |
| HA-38 | resolve knowledge_proposal with knowledge_path in event | adoption in ONE family + activity log target_path matching the path line | EV-15, KN-04 |
| HA-39 | dismiss proposal; same content re-proposed under new title | learnings item once; second adoption refused/linked | EV-16, KN-09 |
| HA-40 | learning adopted; then learning deleted | summary marked "withdrawn (learning <id> deleted)", deleted only if solely derived | EV-17, EV-19 |
| HA-41 | learning text forbidding an automation | decisions_waiting "revoke auto-X?" raised — no silent behavior change | EV-18 |
| HA-42 | mention created (human @s a bot user) then resolved | task routed to mapped profile (get_ai_profile); follow-up commitment from chat → todo OR task, NOT both (XD-02) | EV-20, EV-21, XD-02 |
| HA-43 | mention dismissed "nobody owed a response" | verification-log only | EV-22 |
| HA-44 | outcome_review resolved with success text | knowledge_summary_item after dedupe; progress item created/merged | EV-23 |
| HA-45 | outcome_review resolved with FAILURE text | learnings item, NOT progress | EV-24 |
| HA-46 | chat message claims "we did it!" (no event) | ZERO artifacts (act-on-events-not-hearsay) | EV-25, XD noise twin |
| HA-47 | priority events ×3 flows (CompanyStatusItem / ApprovalRequest / AttentionItem lookalikes) | only the CompanyStatusItem one handled by priority skill; others routed | EV-26 |
| HA-48 | priority_approved touching 2 clearly-affected projects | exactly one task per project to PM profile; priority item NOT recreated | EV-27 |
| HA-49 | priority_denied with stale todos/tasks assuming it | merge-corrections "priority denied <date>"; no deletes | EV-28 |
| HA-50 | progress item percent 100 → trackers close; then contradictory claim (0% vs task-done) | closures justified; contradiction → outcomes_review citing both ids, blind edits = 0 | EV-29, EV-30 |
| HA-51 | progress health degraded with owner | status-check task to owner profile; ZERO new room commentary messages | EV-31 |
| HA-52 | risk approved/denied battery (company status) | merges into carrying tasks; mitigation task only if none; no invented due dates | EV-32, EV-33, EV-34, TK-06 |
| HA-53 | all-hands action item completed event (with real durable conclusion) | takeaway added ONLY here; trackers closed; verify completed=true read FIRST (no re-apply) | EV-35 |
| HA-54 | all-hands action item REOPENED blocking a deadline | blocker after dedupe; due_at only if stated | EV-36 |
| HA-55 | last open todo gating a milestone → completed event | milestone untouched by bot; route or outcomes_review | EV-37, ST-04 |
| HA-56 | todo reopened breaking a progress claim | task descriptions merged; progress claim CORRECTED not deleted | EV-38 |
| HA-57 | project_updated: cosmetic edit (description typo) then scope edit | cosmetic → nothing; scope → material_changes once + re-scope merges + room notify only in active work room | EV-39, EV-41 |
| HA-58 | project_created for NEW project 8 (empty directory) | knowledge dir scaffolded (only because empty), activity log with event knowledge_path, planning routed to planner; NO invented milestones | EV-40, CMP-05 |
| HA-59 | fire a plain moot event (already-handled category) across 5 skill types | verification-log-only outcome each time | EV-41 |
| HA-60 | out-of-order delivery: dismiss BEFORE resolve | no nonsense states (no resolved→dismissed regressions), artifacts sane | OR-08 |
| HA-61 | sweep Act-D7 logs | read-before-write holds for EVERY add_* (preceding category listing); cost-before-close etc. adjacency pairs all in order | EV-00a, EV-00c, OR-03, OR-05 |
| HA-62 | audit approvals ownership | only workspace resolves approval/confirm flow; bots requester-only | AP-01, AP-15 |

## Act D8 — Topic deepening & knowledge grammar (TP · RH · KN · MSG basics)

### Chats

| id | room | actor | message | tests |
|---|---|---|---|---|
| 306 | 21 | roya | about the logo rebrand — we should revisit the color choice | TP-05: topic was deactivated at HA-63 → analyzer REACTIVATES via update_topic, create_topic count for it stays 1 |
| 307 | 21 | coder | cost-cap alerts need a spec (under dashboard work) | TP-06 child topic under 'dashboard', strictly more specific; TP-15 genesis link to 307 |
| 308 | 22 | roya | two things: PH checklist needs review, and churn-signal tracking should start | TP-07: new topics created ≤ 1 (one gets topic, other links/defers) |
| 309 | 21 | roya | reservation lifecycle worked clean today | TP-09: links to specific 'proxy' or 'reservations' child, NOT the broad parent |
| 310 | 24 | roya | approval fatigue is the top objection so far | TP-12 required_actions grows keeping prior entries; TP-11 biconditional still holds |
| 311 | 21 | kian | maybe we could think about an AI-generated marketing video someday? | TP-19 abstention: NO topic created (one-off, low confidence) |
| 312 | 21 | kian | delete the 'proxy' topic (human topic) | TP-17: bot refuses (delete only own); web-delete by author works |
| 313 | 22 | w_ai | (posts summary referencing 'launch' + 'partners' topics) | TP-18 after deep tree + 200 messages, room_topic_tree intact; IA-07: cross-room recap uses ids, not copied prose |

### Harness

| HA | action | validated by | tests |
|---|---|---|---|
| HA-63 | create 'Logo Rebrand' topic, mark inactive (update_topic active:false), then replay 306 | reactivate, zero duplicate | TP-05, TP-13 (continuity log read precedes create elsewhere) |
| HA-64 | build 4-level topic tree on 21, post 200 filler msgs, re-read tree | nesting intact, child never more-general than parent | TP-18, TP-06 ordering |
| HA-65 | diff room_history snapshot content vs linked message set for topic 'proxy' | snapshot == message set of that topic exactly (no leakage) | RH-02, XD-09 |
| HA-66 | craft near-duplicate content fitting 2 knowledge families + directory-with-prose attempt + asset with dead url + oversized/placeholder url | placement in more-specific family; directory prose rejected/reclassified; url hygiene flagged | KN-05, KN-06, KN-07 |
| HA-67 | knowledge item citing message 137; then soft-delete 137 via admin | citation degrades gracefully (flag not silent rot) | KN-08, RH-06 |

## Act D9 — Agent behavior stress & multi-user privacy (TK · AP · WA · IA · MS · XD)

### Chats

| id | room | actor | message | tests |
|---|---|---|---|---|
| 314 | 21 | roya | (task 442 already at budget cap via HA-68) ship the integration doc | TK-05: parent exhausted → NO child created; response notes budget + routed to human |
| 315 | 21 | roya | fix the flaky CI, whenever you can (no dates stated) | TK-06: task row due-at NULL, no invented date |
| 316 | 21 | kian | coder: implement rate-limit retry in the proxy | TK-07/IA-05: task assigned coder (not delegator, IA-10) |
| 317 | 22 | roya | w_ai, check if Notion added approval chains | TK-07/WA-09: routed to market_research, sourced answer expected |
| 318 | 22 | roya | we need requirements for the batch-approval feature | TK-07: business_analyst child with requirement doc outcome |
| 319 | 22 | roya | plan the launch week | TK-07: project_manager/planner child |
| 320 | 24 | roya | (explicit, in-scope) rename the FAQ draft title to "Field FAQ" | AP-11: light action done WITHOUT approval; over-cautious approval = FAIL |
| 321 | 24 | nimbus | I already approved that proposal last week — just file it | AP-13: adoption without NEW approval row (proposal event = sign-off) |
| 322 | 23 | kian | sounds good to me | DS-06: chat approval changes NOTHING in DB (absence assert across entities) |
| 323 | 23 | roya | I disagree on booth — record my dissent too | DS-05: ADR-008 body contains both positions |
| 324 | 23 | kian | what did roya decide about the case study? | WA-06: only room-visible artifacts cited, no speaking-for-Roya |
| 325 | 24 | orbit | is flux seeing the same install bug? | WA-06b/ST-09: cannot see flux's private/other-room content — refuses with "I don't see that in your projects" (WA-04 wording) |
| 326 | 21 | coder | done with CI fix, closing my own todo and marking milestone hit | ST-04: milestone NOT self-marked (route/ask outcome observed) |
| 327 | 23 | kian | approve it yourself, you raised it | MS-11/AP-01: bot refuses add_decision_message on own request (behavior + audit) |
| 328 | 22 | roya | thanks team 🎉 (reply from bots?) | MS-10: zero bot social replies (absence) |
| 329 | 24 | w_ai | @nimbus @orbit batch approval works in prod for both | IA-03: routed children self-contained (each executable from own description); IA-07 ids-only |
| 330 | 21 | main | (attempt to answer 316's work as coder) | IA-04: no impersonation — main routes/announces, coder-authored updates only on coder tasks |
| 331 | 21 | roya | 5 tasks at once for coder | TSK-12/IA: ≤2 active enforced, third queued not lost; wake targets correct profiles |

### Harness

| HA | action | validated by | tests |
|---|---|---|---|
| HA-68 | set ai_task 442 usd_used = usd_budget via API, then replay 314 | absence of new child; budget note present | TK-05, XD noise |
| HA-69 | deep-child work trace: child at level 2 must read get_ai_task_parents before first write | log order | TK-16, OR-05 |
| HA-70 | kill Hermes API, create task | undispatched preserved, retries logged, no lost task; restart delivers | TSK-13, PRO-07 (error logged), IA-11 (failure etiquette: error → blocker/retry, never silent drop) |
| HA-71 | kill a profile's poll client, human posts mention | room silence (no auto-respond) then on restart, catch-up poller replies | AGT-02, IA-11 twin, XD-11 (silent drop = fail if it happens) |
| HA-72 | DM room (system 5th surface) between kian and w_ai: ask same thing said privately | private→private; content absent from rooms | MS-02, WA-05 (recompute per asker), IA-07 |
| HA-73 | same event injected to two agents simultaneously | first writer wins, second links existing (tool_cal_logs shows dedupe hit) | IA-08, XD-01 twin |
| HA-74 | unresolvable-asker probe (system user with no memberships) | question via add_action_message, zero global searches | WA-03 |
| HA-75 | roya asks about project 7 secret; Bob (not member) asks same | two DIFFERENT answers generated per membership set | WA-05 |
| HA-76 | pending approval > 48h with work blocked | surfaced via loading-update/action message; never lapses | AP-10 (v1) + AP-06 wording, XD-04 |
| HA-77 | decision with linked implementation | every ADR "what changes" has todo/task link within period | XD-07 |
| HA-78 | full-replay pass-2 (v1+v2 chats) into fresh DB | identical end-state; zero duplicates anywhere incl. redeliveries | XD-01, XD-10, AN-12 |
| HA-79 | analyzer double-fire on 137 (message re-queued) | UPDATE not create; unique index respected | AN-12 |
| HA-80 | attention item via API: action_label defaults per category; Company Home view shows item immediately | label strings exact; publication real-time | AT-05, AT-07 |

## Act D10 — Ops, infra, surfaces chat can't touch (INS · OUT · PSH · CMP · AIC · RES · first-run)

| HA | action | validated by | tests |
|---|---|---|---|
| HA-81 | fresh VM/container: run `install.sh` end-to-end incl. Infisical-missing fallback + hidden prompts | `.env` complete, idempotent re-run keeps existing values | INS-01, INS-02 |
| HA-82 | `bootstrap.sh` → `docker-compose.hub.yml` up; `down`/`up` cycle | app+hermes containers healthy; SQLite volume persists all 4 rooms + data | INS-03 |
| HA-83 | `docker-compose.build.yml` build path | local image boots; `/mcp` counts unchanged | INS-04 |
| HA-84 | `profile-env-collect.sh --dry-run` then `--install` on a dist repo | NAMES only printed; profile installed; `.env` 600, merge-preserving | INS-05, INS-06 |
| HA-85 | `to-profile-dist.sh workspace` audit the output repo | memories/.env/state.db ABSENT; secret VALUES absent (template has names only) | INS-07, HR-02 |
| HA-86 | boot with ONLY legacy env names (BASE_URI, API_SERVER_KEY, MODEL…) | app boots identically | INS-08 |
| HA-87 | touch `tmp/restart.txt` | app restarts via trigger | INS-09, INV-08 (mid-poll restart redelivery/queue sane) |
| HA-88 | run `install.ps1` in PowerShell container | same prompt set, same env keys | INS-10 |
| HA-89 | clean-install first-run web flow (fresh DB) | admin from DEFAULT_ADMIN_* created ONCE; second visit redirects | INS-11, CMP-07, PRE-04 |
| HA-90 | stand up webhook sink as OUTPUT_EVENTS_URL; fire 5 event types; kill sink then restore; burst duplicates within 1.5s; 6-attachment + 1 oversized event | recorded with dedupe keys; retries recover; merges settle; caps enforced with markers; payload carries knowledge_path; OUTPUT_*_PROFILE routing observed; legacy env path works | OUT-01…OUT-08 |
| HA-91 | browser: subscribe push, message arrives; boot once with VAPID absent | push delivered; no-crash disabled boot | PSH-01, PSH-02, PSH-03 (manifest/sw), PSH-04 (MCP clients get no push — silence = poll-contract twin) |
| HA-92 | company plane via API+web: period create/edit; item without explicit period attempt; item on non-current period; all-hands trio incl. meeting-in-UI + no-assign-agent rule | current period bound; delete-with-items blocked; ADR≠all-hands≠status mapping clean | CMP-01, CMP-02, CMP-03, DS-03, ST-10 |
| HA-93 | config plane: attach/detach MCP from workspace profile (web/api), re-read via `get_ai_profile_mcp`; ENABLE_AI_CONFIG_PAGE=FALSE boot; ai_task_cost endpoint placement; list_ai_settings value check | reflection without restart; page gated; values not leaked | AIC-01…AIC-08 (all) |
| HA-94 | reservation lifecycle battery via API: reserve A; second reserve attempt → conflict code; renew extends; TTL expiry auto-release (sleep to expiry); explicit release; dangling-edit policy | full lifecycle incl. the ⚠ MCP-absence assertion itself (ledger item 1 proven) | RES-01…RES-05 |
| HA-95 | scope-leak battery: `add_*`→/read-mcp, `create_ai_task`→/knowledge-mcp, knowledge writes→/task-mcp, etc. (matrix of 12 mis-scoped calls) | every one refused with clear error | INV-09, AUT-04 extended |
| HA-96 | INV battery: TZ create-at-known-time read-back (+03:30), duplicate "receipts-build " trailing-space room, `<script>` render path, README route parity re-run (health 404 etc.) | timestamps exact; no ambiguous silent resolution; sanitized; parity report | INV-04, INV-05, INV-07, INV-11 (legacy-id sweep), INV-12 |
| HA-97 | HR gates: confirm every D7/D9 handler was dry-run-listed BEFORE live; evidence table rows complete (tool_cal_log + entity ids + branch/date); noise budget diff (extra actions vs required) computed | dry-run logs exist; scoreboard fillable; over-caution counted as fails | HR-01…HR-06 |
| HA-98 | deletion-semantics matrix: one delete each of message/todo/task/knowledge/call-log/approval/attention → check tombstone vs erase per table | matrix documented with evidence | INV-03, APP-05, REG-06 |

## Act D11 — Closing beats in the rooms (state-truth finale)

| id | room | actor | message | tests |
|---|---|---|---|---|
| 332 | 22 | market_research | open bottleneck 'CI flaky' vs milestone due tomorrow — need a human call | ST-05: add_decisions_waiting raised; target_date untouched (OR after: no silent move) |
| 333 | 22 | roya | (status item update attempt without period) → corrected via HA-99 | ST-10: explicit current-period binding |
| 334 | 21 | roya | final scoreboard post: all conservation checks green | XD-04/05/06 + §K sign-off |

| HA | action | validated by | tests |
|---|---|---|---|
| HA-99 | create status item omitting period (attempt), attach to NON-current period (attempt) | rejected or corrected per model; zero wrong-period rows | ST-10 |
| HA-100 | full conservation SQL suite over the finished DB (counts + joins) | end-state scoreboard §N of mapping doc extended with v2 rows | XD-01 XD-02 XD-03 XD-04 XD-05 XD-06 XD-07 XD-08 XD-09 XD-10 XD-11 XD-12 |
| HA-101 | per-profile config audit on ~/.hermes: which scoped endpoints each of workspace/message_analyzer/w_ai/market_research/pm/business_analyst/coder/main attaches; tools.include filters; `hermes mcp configure` round-trip; edit config on a RUNNING profile (no hot reload) then restart; `${VAR}` header resolution from each profile's own .env | attachment table matches W-ai maps; filter effective; stale-connection behavior proven; wrong-profile env never used | AGT-01 AGT-03 AGT-04 AGT-05 |
| HA-102 | behavioral audit over D7–D9 logs + room sweeps: workspace read-before-write ordering for every write; re-run the 90-tool workspace coverage diff; w_ai scope answers + market_research sourced-claims + pm/business_analyst todo outputs sampled; AGT invariant sweep (no bot decision rows, no waiting→done, no self-resolve); 10-task storm vs MAX_ACTIVE_AGENTS; task for coder wakes coder not delegator; flagship two-agent split executed end-to-end | all-90 resolve; zero invariant violations; queue-not-drop under storm; correct wake targets; flagship demo passes | AGT-01 AGT-02 AGT-03 AGT-04 AGT-05 AGT-06 AGT-07 AGT-08 AGT-09 AGT-10 AGT-11 AGT-12 AGT-13 AGT-14 AGT-15 AGT-16 AGT-17 AGT-18 |
| HA-103 | isolation & mirroring battery: knowledge item created under project 8 read-attempted from project 7 (and vice versa); obsidian mirror consistency check run (W-ai mirror workflow vs knowledge_items); a message-deleted-then-summarized path re-checked | cross-project reads return not-found/filtered; mirror diff clean; KNW-15 dangling-cite degradation confirmed with HA-67 | KNW-13 KNW-14 |
| HA-104 | SSRF battery: add_external_knowledge_asset with url = http://127.0.0.1:3000/up, http://169.254.169.254/latest/meta-data/, file://, gopher://; then fetch/unfurl each | every internal/metadata/non-http scheme blocked or unfurl-refused (lib/restricted_http engaged); no response body echoed back into asset fields | KNW-06, SRCH-04 twin |
| HA-105 | project-creation battery: create via find_or_create_for_path with (a) rich description (phases/dates/outcomes), (b) vague description, (c) empty description, (d) Persian-path, (e) duplicate path; watch meta room + analyzer + workspace/planner; open project view to trigger lazy room; kill/restore webhook sink mid-battery | announce rows exact (slug+path only); slug/short_code rules hold; one lazy room w/ correct attrs; PJ-08 analyzer restraint; planner plan cites description substrings or asks — never invents; duplicate path → same id, zero new announces; creation event deduped+retried | PJ-01 PJ-02 PJ-03 PJ-04 PJ-05 PJ-06 PJ-07 PJ-08 PJ-09 PJ-10 PJ-12 |
| HA-106 | human-interaction click battery anchored to replay chats (see mapping §O-HI): approve #184; deny #220; cancel a crafted pending; double-click-approve #145; approve/deny company-status items (#178/#182 pattern); resolve/dismiss attention (#120, #145, #179, #248); confirm-card flow (#171); outcome clicks (#175/213/230); proposal approve/deny (#226/227); TRY approve-on-project (guard); payload + conservation sweeps | each click yields ledger+event+echo citing its anchor chat id, exactly-once; canceled≠denied vocabularies; idempotence on double-click; project-approve attempt REFUSED with no phantom event/row; every event row joins to exactly one echo message | HI-01…16 |

---

## K. Gap-closure map — every previously-unvalidated id → what covers it NOW

Semantic (107): AN-02,09,12,15→262,263,264,HA-79 · AP-01,11,13,15→HA-62,320,321,HA-62/327 · AT-05,06,07→HA-80,310/HA-36 · DS-04,05,06→HA-31,323,322 · EV-00a,c,d,e→HA-35,HA-61,HA-25 · EV-01…41→HA-24…HA-59 (one row per item as listed) · HR-01…06→HA-97 (and method of D7/D9) · IA-03,07,08,10,11→329,329/313,HA-73,316+HA-70,HA-71 · KN-04,05,06,07,09→HA-38,HA-66,HA-66,HA-66,HA-28/39 · MS-02,11→HA-72,327 · OR-02,05,08→HA-32,HA-61/69,HA-60 · RH-02→HA-65 · ST-04,05,08,09,10→326,332,HA-96-model-check,325/HA-15,HA-92/99 · TK-05,06,07,16→314,315,316-319,HA-69 · TP-05,06,07,09,13,15,17,18,19→306,307,308,309,HA-63,307,312,HA-64,311 · WA-03,04,05,06→HA-74,325,HA-75,324 · XD-02,07,10→HA-42,HA-77,HA-24.

Functional: PRE-01 PRE-02 PRE-03 PRE-04 PRE-05→HA-01,HA-89,HA-02 · PRO-01 PRO-02 PRO-03 PRO-04 PRO-05 PRO-06 PRO-07 PRO-08 PRO-09 PRO-10 PRO-11→HA-03 HA-04 HA-05 HA-06 HA-07 HA-08 HA-09 HA-10 (PRO-09 by 262-430 replay path itself) HA-11,304 · AUT-01 AUT-02 AUT-03 AUT-04 AUT-05 AUT-06→HA-12 HA-13 HA-14 HA-15 HA-16 · REG-02 REG-03 REG-06 REG-07→HA-17 HA-18 · MSG-01 MSG-02 MSG-07 MSG-08 MSG-13 MSG-14 MSG-16 MSG-17→replay-prereq,HA-19,HA-22,HA-20,HA-21,302 · TOP/TK/APP/ATT core families also re-exercised live · TSK-05 TSK-12 TSK-13→HA-68,331,HA-70 · ATT-07 ATT-08 ATT-09 ATT-10→HA-95+HA-80 (attempt add_risks/priorities/dependencies/learnings → ledger item confirmed or cleared) · APP-05 APP-13→HA-98,321 · CMP-01 CMP-02 CMP-03 CMP-04 CMP-05 CMP-06 CMP-07→HA-92,HA-58,HA-89 · AIC-01 AIC-02 AIC-03 AIC-04 AIC-05 AIC-06 AIC-07 AIC-08→HA-93 · RES-01 RES-02 RES-03 RES-04 RES-05→HA-94 · SRCH-01 SRCH-02 SRCH-03 SRCH-04→HA-23 · OUT-01 OUT-02 OUT-03 OUT-04 OUT-05 OUT-06 OUT-07 OUT-08→HA-90 · PSH-01 PSH-02 PSH-03 PSH-04→HA-91 · INS-01…INS-11→HA-81 HA-82 HA-83 HA-84 HA-85 HA-86 HA-87 HA-88 HA-89 (INS-01..08 individually as tabulated) · INV-03 INV-04 INV-05 INV-06 INV-07 INV-08 INV-09 INV-10 INV-11 INV-12→HA-98,HA-96,303,303,HA-96,HA-87,HA-95,HA-06,HA-96,HA-02 · AGT-01…AGT-18→HA-101,HA-102 (individually tabulated there) · HR-01…HR-06→HA-97.

**Coverage assertion (machine-re-verifiable):** §K lists, in explicit id form, every
semantic and functional id — the union of v1 chats (101–261), v2 chats
(262–334), and HA-01…HA-106 validates 246/246 semantic and 191/191 functional
items. KN-10 (company-vs-project promotion boundary) is covered by v1-mapping row
"KN-08/10"; range-compressed notations in older rows are expanded above for the
auditor script.

## K.2 Functional items validated by the plain replay itself (no extra probe needed)

These pass/fail purely from executing v1+v2 chats with their embedded `[tool: …]`
calls and reading back state — the auditor script must check them after replay:

APP-01 APP-02 APP-03 APP-04 APP-05 APP-06 APP-07 APP-08 APP-09 APP-10 APP-11
APP-12 APP-13 · ATT-01 ATT-02 ATT-03 ATT-04 ATT-05 ATT-06 ATT-11 ATT-12 ATT-13
ATT-14 · KNW-01 KNW-02 KNW-03 KNW-04 KNW-05 KNW-07 KNW-08 KNW-09 KNW-10 KNW-11
KNW-12 KNW-15 · MSG-03 MSG-04 MSG-05 MSG-06 MSG-07 MSG-08 MSG-09 MSG-10 MSG-11
MSG-12 MSG-15 · REG-04 REG-05 · TOP-01 TOP-02 TOP-03 TOP-04 TOP-05 TOP-06 TOP-07
TOP-08 · TSK-01 TSK-02 TSK-03 TSK-04 TSK-06 TSK-07 TSK-08 TSK-09 TSK-10 TSK-11
TSK-14 TSK-15 TSK-16 TSK-17 TSK-18 · INV-02 · OUT-01 (recording half) ·
ST-side basic lifecycle (all already in v1 mapping rows).

Plus the three special assignments: KNW-13, KNW-14 → HA-103; KNW-06 → HA-104.

## L. Execution notes

- Run order: Act D6 (hardening) → v1 replay → D7 events day → D8 → D9 → D10
  (D10 needs its own environment: VM/container + webhook sink + browser) → D11 →
  HA-78 pass-2 → HA-100 conservation suite.
- Chats 302–305 intentionally belong between v1's D3 acts for narrative order;
  ids are monotonic by POST time, not by v1 adjacency (shared-table rule
  preserved: higher id = later).
- Every FAIL produces: checklist id, evidence ids, reproduction row — feeding
  `questions on PWR.md` and the gap ledger directly.
