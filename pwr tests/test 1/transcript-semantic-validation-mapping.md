# Transcript → Semantic-Test Mapping — replaying the chats proves WHAT of `pwr-semantic-checklist.md`

> Companion files: `pwr-feature-test-conversations.md` (v1, 161 messages, ids
> 101–261), `transcript-v2-completing-replay.md` (v2, chats 262–334 + harness
> actions HA-01…HA-104), `pwr-semantic-checklist.md` (218 semantic items).
> Sections A–N below map semantic items to **v1** chats; sections O–P extend the
> map to **v2** chats and probes so the full 218 items have a driver and a
> desired-state assertion.

## Replay protocol (assumed)

1. Live app: `W/pwr` @ `installation`, localhost:3000. Create project `receipts`
   (7) + rooms `receipts-build`(21) `receipts-growth`(22) `receipts-founders`(23,
   decision_room) `receipts-partners`(24); users kian(2) roya(3) bots main(4)
   coder(5) market_research(6) w_ai(7) guests nimbus(11) orbit(12) vector(13)
   flux(14) halo(15).
2. **Attached and polling**: message_analyzer (knowledge+task), workspace
   (5 endpoints), w_ai (action+read+knowledge) — the bots must be live for
   bot-authored messages to emerge from behavior, not be typed in. Where the
   transcript shows a bot message, the replay posts the HUMAN trigger and
   expects the bot to produce that message; ids shift but content-assertions
   hold.
3. Post every message in strict id order (single shared `messages.id` sequence —
   monotonic growth is itself ST/XD evidence).
4. After each act (D1–D5) run the checkpoint queries (see §Conservation).
5. Full replay runs TWICE into a fresh DB per run — pass = identical end-state
   and zero duplicate artifacts on pass 2 (XD-01).

**Validated signal format:** `state-change → verified by <read/query>`.

---

## A. Validated by replay — message analysis (AN)

| ID | Test | Driving chats | Desired outcome = PWR state change |
|---|---|---|---|
| AN-01 | every message analyzed; trivial → no side effects | 124, 160, 245, 259 (thanks/+1) | `message_analyses` rows exist for each with importance 0-1, type useless/normal; **absence**: zero topic/task tool calls attributable to these ids (tool_cal_logs filter message_id) |
| AN-03 | FYI/status stays 2 | 143, 149, 178, 212 | analysis importance=2; no update_topic call after them except AN-11 exception |
| AN-04 | substantive → 3 + topic touch | 137, 164, 182, 202, 219, 222, 232 | importance=3-4 AND a `message_topics` link row appears within the analyzer's cycle — link is the state proof of "noticed and filed" |
| AN-05 | owner+deadline message → 4 with ONE bump | 114 ("todo owner=roya due=Fri"), 150 | importance exactly 4 (base 3 +1 once); assert not 5 |
| AN-06 | one-word decision reply → 4 | 107 "YES, domain", 135, 148, 194, 209, 217, 224, 249 | every single-word approval/rejection row scored 4; state: analysis + downstream decision flow fires only because of this scoring |
| AN-07 | outage/incident → 5 (or 4) | 170 (fail-open), 179 (SLA miss) | importance ≥4; the 5-if-production distinction visible in analysis text |
| AN-08 | ambiguous → lower chosen | 188 ("Thanks — +1 on the scan") | 1 not 2; no artifact beyond analysis |
| AN-10/11 | bot rules incl. threshold-2 exception | 121 (ledger done = step of topic 'proxy'), 127 | 121→importance 2 **but** `update_topic` on 'proxy' required_actions fires (the exception), then link; 104/149-style routine → 1-2 |
| AN-13 | message_type vocabulary | ALL replayed messages | `SELECT DISTINCT message_type` = subset {useless,normal,bot}; zero 'analysis' |
| AN-14 | summary not generic | 137, 164, 182 | stored `message_content_summary` contains story-specific nouns ("prod table", "$312") — string-match assertion |

## B. Validated by replay — topics (TP)

| ID | Test | Driving chats | Desired outcome |
|---|---|---|---|
| TP-01 | create-without-search banned | 117 (topic 'proxy'), 238 (topic 'pivot-evidence') | tool_cal_logs order: `search_topics`+`room_topic_tree` timestamps < `create_topic` timestamp for both |
| TP-02 | near-duplicate reuse | 155, 206, 242 (three dashboard messages) | topic count named ~'dashboard' == 1; each message got a LINK row, not a TOPIC row |
| TP-03 | repetition → link only | 149 (digest restates) | message_topics link exists; `update_topic` absent for that message id |
| TP-04 | nurture order | 170 (bug changes ledger/proxy state) | update_topic (state/memory) → create_message_topic → create/update room_history_topic, in that log order |
| TP-08 | naming grammar | all topics created in replay (expect ~4-6: 'proxy','approval gate','design partner validation','pivot-evidence') | regex: 2-4 words, Title Case, no verbs/names/dates |
| TP-10 | link budget ≤3, one primary | 137, 182 | per-message message_topics count ≤3 |
| TP-11 | gate biconditional | after D2 | for every topic: need_an_action=true ⇔ required_actions ≠ '' (SQL assert on topics table) |
| TP-12 | required_actions merge integrity | 182 → 222 → 226 (cost cap, then fatigue, then batch idea) | topic 'design partner validation'/'approvals' required_actions GROWS preserving earlier entries, no duplicate tokens |
| TP-14 | topic_id at task creation only | 152 vs 196 | child tasks carry topic linkage at creation; zero later task-topic re-link calls in logs |
| TP-16 | merge-not-replace updates | 211 (duplicate feature merged/moved) | untouched fields byte-identical pre/post (diff get_topic before/after) |
| TP-20 | audit log after topic writes | 117, 119, 211, 221, 238, 250 | one `tool_cal_logs` row per topic mutation with used_tool_name matching exactly |

## C. Validated by replay — room history & context (RH)

| ID | Test | Driving chats | Desired outcome |
|---|---|---|---|
| RH-01/03 | snapshot only on material change; refresh not spam | 119 (proxy-w1), 250 (final-w5); D1-D5 material moments (121, 185, 244) | room_history_topics count for 'proxy' small (≈2, not per-message); 250 UPDATES or supersedes, not parallel duplicate |
| RH-04 | summary fidelity | 167 (`room_context_summary`) | every fact in posted summary maps to a real message id ≤166 (manual 5-fact diff or LLM judge against rows) |
| RH-05 | room memory boundary | 202/219 (partners) vs build room reads | room 21's context/summary contains no partner-room content; negative probe: run room_context_summary(21) after 219 — assert absence of "stars +340" |
| RH-06 | post-delete coherence | 146 deletes 136; 210 batch delete | snapshots/summaries generated after show no reference to deleted loading messages |

## D. Validated by replay — tasks (TK)

| ID | Test | Driving chats | Desired outcome |
|---|---|---|---|
| TK-01/TK-20 | meaningful description + always project_id | 103, 152, 165 | ai_tasks rows: description non-trivial; project_id NOT NULL |
| TK-02 | dedupe before create | 165 (main splits child 455) | log: `ai_tasks(project_id,finished=false)` precedes `create_ai_task`; equivalent-open → reuse |
| TK-03 | event→task traceability | 186 (cost-cap from story 182), 231/233 (batch approval) | input_event_entity_id / description cites source message id |
| TK-04 | level math ≤3 | 103→165→196; 442→455,456 | level/parent/grandparent columns consistent; max depth observed 2 ≤ 3 |
| TK-08/09 | flags & start ritual | 103 create → 104 wake | row after create: dispatched=f, finished=f; coder/main's FIRST write on it is update(dispatched:t) |
| TK-10 | closed forever, child continues | 121 closed → 185 separate task | no update touches finished f→t; 185 is new row, cites parent |
| TK-11/12 | cost-before-close + rollup | 127 (441 $8.40/$25), all closes (121, 196, 214, 231, 242) | log order ai_task_cost→update_ai_task(finished); ancestor cumulative cost includes child delta (assert 442 total ≥ child sums) |
| TK-13 | context truth | 121 | actual_task_context describes what happened (not empty) |
| TK-14 | never-delete-to-close | whole replay | `delete_ai_task` call count = 0 (absence assertion) |
| TK-15 | blockage merged into description | 170 incident vs open tasks | affected task descriptions grow by note lines; other fields unchanged |
| TK-17 | person→todo vs agent→AiTask | 114 (roya-owned todo) vs 103 | project_todos row has assignee=roya, deadline; ai_tasks row assigneee_profile set — the same content pattern lands on DIFFERENT surfaces per actor kind |
| TK-18 | chat promise → task id confirmation | 229→231 | task id appears in room reply after routing |
| TK-19 | orphan sweep | 179→180 | w_ai's self-filed blocker resolved AND its tracking task closed same session |

## E. Validated by replay — approvals (AP)

| ID | Test | Driving chats | Desired outcome |
|---|---|---|---|
| AP-02 | one-call raise with message | 184, 216, 252, 112, 145, 205, 220, 246 | approval_requests row created in SAME call as its action message (linked message id, same timestamp) |
| AP-03 | 4-tuple completeness | all 13 raises | each body contains target+ids, scope, boundary ("won't touch"), evidence link — regex/field assert |
| AP-04 | one gate per action | 193 vs 216 (two different actions) | no (target,action) pair with 2 pending rows |
| AP-05/06 | pre-execution ban + waiting wording | 193→194 window; 216→217→**218** | zero tool calls touching PH/announcement before decision id; link-post (218) timestamp AFTER 217 decision row; between 145-148 no message says done/executed |
| AP-07 | execute exactly | 171→185→214 | hotfix+regression executed within approved scope only (log calls ⊆ approved body scope) |
| AP-08/09 | denial closure, no resubmit | 220→224; whole replay | booth task closed citing denial; $99 never appears in spend; `approval_requests` count for booth = 1 ever (absence assertion) |
| AP-10 | no silent lapse | 145 pending surfaced by 153 queue read | pending item visible in attention/queue read before D3 ends |
| AP-12 | gate/no-gate mapping | gated: 112,184,205,216,220,246,252 · ungated: 114,149,144 | approvals exist EXACTLY for the gated seven actions; zero approvals raised for todo-creation/digests (bidirectional assertion) |
| AP-14 | approval id continuity | after D4/D5 | executing calls' change_log cites the approval id they acted under |

## F. Validated by replay — decisions (DS)

| ID | Test | Driving chats | Desired outcome |
|---|---|---|---|
| DS-01 | humans own decisions | every 107/135/148/166/187/194/209/217/224/249/253 | `decision_messages` creator uid ∈ {2,3} — 0% bot (SQL over replay) |
| DS-02 | ADR sequence | 110→249 | project_decision_records identifiers ADR-001…ADR-006, monotonic, no reuse |
| DS-03 | family separation | 120/170/179 (blockers), 102-249 (ADRs), none double-filed | same subject never appears in two decision families (blocker≠ADR≠decisions_waiting) — cross-family dup query = 0 |
| DS-07 | citation liveness | 187 cites 184; 249 cites 246/247 | every cited approval/message id resolves to an existing row |

## G. Validated by replay — attention (AT)

| ID | Test | Driving chats | Desired outcome |
|---|---|---|---|
| AT-01 | more-specific wins, one/category | 170 incident (risk vs blocker) | exactly one new item for the incident in the most-specific category present on the surface (⚠ if add_risks missing → falls to blocker: functional gap ATT-07 recorded, semantics still judged) |
| AT-02 | status vocabulary | 122/180 resolves | states ∈ {pending,resolved,dismissed} only |
| AT-03 | resolve is human — bots never resolve others' | 179 (w_ai self-files) → 180 (kian resolves) | resolver uid=2 for item created by uid=7; zero cases of bot-resolving human items across replay |
| AT-04 | narrowest scope attached | 120, 170, 179 | rows carry project_id+room_id, no company-wide NULLs |
| AT-08 | category accuracy battery (natural instances) | 120→blocker · 137→mentions/decision? · 222→priority? · 241→outcome_review · 224→decision path | expected category per source message matches produced category: ≥4/5 natural cases (the remaining 3 of 7 need crafted events) |

## H. Validated by replay — knowledge (KN)

| ID | Test | Driving chats | Desired outcome |
|---|---|---|---|
| KN-01 | family placement | 111→external_asset · 154/190→asset/summary · 226→knowledge_item(proposal) · 138→activity_log · 40 (scaffold dir) — | content lands in the family the matrix prescribes; spot-diff of 4 rows |
| KN-02 | verbatim capture | 137, 164, 182, 202, 222 | knowledge text quotes source message wording (string-containment test), interpretation only in marked trailing note |
| KN-03 | adoption leaves activity | 226→229→231 chain | knowledge_activity_logs row exists naming proposal id + destination family |
| KN-08/10 | citation & boundary | 248→252→253 (case study) | consent message id cited; nothing promoted company-wide without an approval row |

## I. Validated by replay — inter-agent quality (IA)

| ID | Test | Driving chats | Desired outcome |
|---|---|---|---|
| IA-01 | routed task answered substantively | 126→127; 229→231 | reply references the ask and produces artifact ids |
| IA-02 | bounded exchange + escalation (the #1 question!) | batch-approval arc 222→226→229→231→233→236 | agent↔agent hops ≤5 on the subject, then human decision rows (224/246) — count hops per subject from logs |
| IA-04 | no impersonation | ALL | message creator uid matches the acting profile identity for 100% of rows (esp. nobody posted "as" nimbus/11) |
| IA-05 | explicit ownership | 165 (child→coder) | ai_tasks.assigneee_profile = coder at creation; no chat-only claims |
| IA-06 | delegation vs core duty | 141/147 (w_ai answers itself) vs 157/186 (routes) | w_ai answered product Qs without routing; routed BUILD work; wrong-side cases = 0 |
| IA-09 | one owner/outcome per card | 234? use 186, 229 | each routed item has single assignee + expected outcome field filled |
| IA-12 | DB-first, then announce | 121, 185, 214, 231, 242 | underlying tool call timestamp < announcement message id (SQL join on times) |

## J. Validated by replay — messaging (MS)

| ID | Test | Driving chats | Desired outcome |
|---|---|---|---|
| MS-01 | answer in same room, bot identity | 141/147 in room 24 | reply room_id == trigger room_id; creator uid=7 |
| MS-03/04 | loading lifecycle & blocked ≠ spinning | 136→146 (full add→delete) ; 179 (spin replaced by blocker) | loading row created then deleted, no orphans at end (count=0); 179 posts blocker message + attention row together |
| MS-05 | no-Markdown law | all bot messages | regex `**`/`#`/``` in bot-authored bodies = 0 hits |
| MS-06/07/08 | verdict-first, one subject, kind-labelled ids | 127, 186, 199, 244 | first sentence = verdict; ids appear as "task 441"/"topic 'proxy'" — pattern assert |
| MS-09 | no duplicate send | whole replay | hash of bot-authored bodies: no dup pairs |
| MS-10 | bots don't socialize | 160/245/259 human thanks → no bot reply | zero bot messages matching /thanks|glad|🎉/ |
| MS-12 | mention chips render | 101 (3 valid) vs 131 (invalid @zzz) | 3 mention-attachment rows for 101; 131 stores raw text, posts fine, no fake chip |
| MS-13 | says what was looked at | 147, 167 | answer body names the reads ("room_context_summary of 21") enabling scope-challenge |

## K. Validated by replay — w_ai scope (WA)

| ID | Test | Driving chats | Desired outcome |
|---|---|---|---|
| WA-01/02 | asker-first, membership-cached reads | 141, 147 (nimbus questions) | log order: get_users/get_room_members(24) BEFORE any content lookup; all reads' room/project ids ⊆ asker's set |
| WA-07 | triage exclusivity | 147 (Answer) · 151 (Act-form) · 195 (check-in question) | each produces exactly one outcome class |
| WA-08 | chat→work with id confirm | 182→186 | ai_tasks row cites 182 AND reply message states "todo/task <id>" |
| WA-09 | routing table | 157→build routing, 208→mr scans | child tasks' assignee matches {coder:build, market_research:evidence} |
| WA-10 | never invent | any replay failure of lookups | error path yields "don't know"/question, not fabricated ids (assert: no message cites a nonexistent id as fact) |

## L. Validated by replay — cross-cutting conservation (XD) & ordering (OR) & state (ST)

| ID | Test | Driving chats | Desired outcome |
|---|---|---|---|
| XD-01 | full-replay idempotence | all 161 ×2 runs | run2 entity deltas = 0 (topics, tasks, approvals, knowledge, attention counts identical) |
| XD-03 | no untraced message | all 161 | every messages.id has ≥1 analyzer tool_cal_log row (coverage query = 161/161) |
| XD-04 | approval conservation | 13 raises vs 12 decisions + 1 open-with-owner | raised == decided + pending; no vanished gate |
| XD-05 | task closure conservation | created: 103,152,165,186,192,203,231?,256... | created == finished + open; every finished has cost-before-close + context |
| XD-06 | importance-4/5 ⇒ artifact | 107,137,145,164,170,179,182,184,220,222,224,246,249 | each maps to decision/task/attention/topic-update or explicit no-action context |
| XD-08 | promised digest delivered | 160 ("digest promised") → 199 ; 199 → used at 234 | cross-post message exists with source-cite; audit message references it |
| XD-09 | citation liveness both ways | 144→137, 185→182, 247→189/190/240, 227→137/164 | all cited ids resolve; deleted-target (136) cited by nobody after 146 |
| XD-11 | errors never swallowed | 103(token_budget), 131(invalid mention), 152(locked field) | each error row followed by: annotation (130/158) or clean-absent behavior — zero silent drops |
| XD-12 | learning→behavior closure | 161(2nd conflict)→180(process fix)→204/235(renew/release hygiene) | reservation-conflict count after 181 == 0 (state trend query) |
| OR-01 | analyzer canonical order | 182 full path | timestamps: analysis < search < update_topic < link < history |
| OR-03 | read-before-write universal | every add_* in replay | preceding same-category list read exists for same scope (batch log-order query) |
| OR-04/06 | approval-before-execution | 217<218 ; 112→133→196 | decision row id/time < execution call; deferred work executed only after |
| OR-07 | reply threading | 158 annotates 152; 174 edits/boosts 170 | reply/edits reference parent ids; thread order preserved in history reads |
| ST-01 | done means done | 121/185/242 claims | evidence exists: repo file/tool rows/attachment for each claimed artifact |
| ST-02/03 | claims supported | 212 (progress) vs completed todos | progress items citing project have ≥1 completed backing row (SQL join) |
| ST-06 | corrections with notes | 178/212 pipeline updates | percent/status change carries details note + appears in call log |
| ST-07 | vocabularies don't bleed | whole replay | attention statuses ≠ status-item statuses in any row |

---

## M. Superseded by v2 — what v1 alone could NOT prove, and where it lives now

Formerly-unprovable classes, now assigned in `transcript-v2-completing-replay.md`
(detail rows in §O–P below):
- Redelivery idempotence (EV-00b, XD-10, AN-12) → HA-24, HA-79.
- Budget-exhaustion gate (TK-05) → chat 314 + HA-68.
- The 46 event-handler items (EV-*) → event-injection battery HA-24…HA-62 (§P).
- Topic lifecycle shapes (TP-05,06,07,09,13,15,17,18,19) → chats 306–313 + HA-63/64 (§O).
- w_ai privacy battery (WA-03..06) → chats 324, 325 + HA-74/75.
- Private-channel & snapshot fidelity (MS-02, RH-02, RH-03) → HA-72, HA-65.
- Noise axis (AP-11) and light-action exemption (AP-13) → chats 320, 321.
- Harness conventions (HR-01..06) → HA-97 gate + the dry-run-first method of D7.
- Infrastructure/protocol/ops functional remainder → HA-01…23, 68…78, 80…104 (v2).

**Conditional on known gaps** (unchanged; v2 measures which way they fall):
- AT-01 / risk items depend on add_risks/priorities absence (ledger 5) — v2 HA-80
  attempts them directly and records PASS/GAP.
- 130/156/174 edit probes depend on MCP edit-absence (ledger 3) — replayed via
  web session; permission assertions still evaluated.
- 109/132/204/235 reservations replay via API (ledger 1) — HA-94 completes the lifecycle.

## N. Expected end-state after a clean full replay (the validation scoreboard)

Predicted counts to diff — a mismatch in EITHER direction (missing = action dropped; extra = duplication/noise) fails the run:

| Entity | Expected | Built from |
|---|---|---|
| messages | 161 | the script |
| message_analyses | 161 (1:1, unique message_id) | AN-01 |
| topics | ~5-7 (proxy, approval-gate, dashboard, design-partner-validation, pivot-evidence, +≤2) | TP-02 |
| message_topics links | ≤ 3×(45 actionable) and ≥1 per substantive msg | TP-10 |
| room_history_topics | ~3-4 (w1 snapshot, material updates, final-w5) | RH-01 |
| ai_tasks | ~10-12; ALL have project_id; 0 deleted; every finished one has cost-before-close | TK/XD-05 |
| approval_requests | 13 raised → 12 decided + 1 state-consistent; bodies 100% 4-tuple | AP/XD-04 |
| decision_messages | ~12, creators only uid 2/3 | DS-01 |
| ADRs | exactly ADR-001..006 monotonic | DS-02 |
| attention items | blocker 120/179 (+risk-fallback 170) etc.; resolves 122/180; 0 bot-resolved-human | AT-03 |
| knowledge: assets ~3, activity logs ≥2, summaries ≥1, proposal adopted 226→231 | family matrix | KN-01/03 |
| tool_cal_logs | ≥ one row per state-changing call; 0 errors unannotated | XD-03/11 |

Run the replay once, execute the §A–L assertions in id order, then run §N as
the scoreboard, then run pass-2 for XD-01. Result per item: PASS / FAIL(reason
id) / N-A(crafted-only). With §O–P below, N-A is eliminated: v1+v2 together
assign a driver to all 218 semantic items.

---

## O. Validated by v2 CHATS (ids 262–334; shared table continues)

### Analysis & topics

| ID | Test | Driving v2 element | Desired outcome = PWR state change |
|---|---|---|---|
| AN-02 | trivial-social is exactly 1 | 262 "brb, coffee" | analysis importance=1; zero downstream calls (tool_cal_logs message-scope empty) |
| AN-09 | bump rule fires ONCE | 264 (decision+owner+deadline) | importance exactly 4 — not 5; analysis text shows single bump |
| AN-12 | double-analysis updates | 137 re-queued via HA-79 | second pass = update_message_analysis; create count for msg 137 stays 1 |
| AN-15 | stop-after-low | 262, 263 | no search_topics/link/history calls attributable to these ids |
| TP-05 | reactivate-not-duplicate | 306 + HA-63 (topic pre-deactivated) | update_topic(active:true); lifetime create_topic count for 'Logo Rebrand' = 1 |
| TP-06 | proper child creation | 307 | ONE new topic with parent='dashboard', name strictly more specific ('Cost Cap Alerts') |
| TP-07 | 1 new topic per message | 308 (two subjects) | create_topic calls for msg 308 ≤ 1; other subject linked/deferred |
| TP-09 | most-specific link | 309 | link targets child/specific topic; parent-only link = FAIL |
| TP-13 | continuity read before create | HA-63/64 audit | log shows tool-call-history read preceding each D8 create |
| TP-15 | genesis link | 307 | message_topics row 307↔new-topic exists at creation time |
| TP-17 | delete discipline | 312 | bot refuses delete_topic on human topic; zero delete calls for it in logs |
| TP-18 | deep-tree survival | HA-64 + 313 | room_topic_tree exact after 4-level tree + 200 filler msgs |
| TP-19 | abstention valid | 311 | NO topic created for vague one-off (absence assert) |

### Tasks, approvals, decisions, attention

| ID | Test | Driving v2 element | Desired outcome |
|---|---|---|---|
| TK-05 | budget gate blocks child | 314 + HA-68 | zero create_ai_task rows for the request; room reply cites exhaustion |
| TK-06 | no invented optionals | 315 | created row: due/optional fields NULL exactly as event lacked them |
| TK-07 | routing-table accuracy | 316→coder, 317→market_research, 318→business_analyst, 319→project_manager | assigneee_profile correct in 4/4 rows |
| TK-16 | parent revalidation | HA-69 | get_ai_task_parents ts < child's first write ts |
| AP-01 | requester-only invariant | HA-62 audit | bots never approve/resolve cross-company approval flows (SQL: approver actor ≠ bot) |
| AP-11 | noise axis (over-caution FAILS) | 320 | rename executed with ZERO approval_requests created |
| AP-13 | approved-proposal exemption | 321 | adoption without a second approval row |
| AP-15 | flow ownership | HA-62 | only workspace processes approval_* events |
| AT-05 | action_label defaults | HA-80 | labels == CATEGORY_CONFIG ("Approve", "Assign & Unblock", "Record Result") |
| AT-06 | dedupe-before-add order | HA-36 | list-category call precedes add; single pending item for subject |
| AT-07 | Company Home publication | HA-80 | item instantly visible in human attention view (web read) |
| DS-04 | ADR body quality | HA-31 | ADR-007 has deciders, context, decision, consequences, dates — none empty |
| DS-05 | dissent preserved | 323 | ADR-008 records both founders' positions |
| DS-06 | chat-approval is inert | 322 | zero row deltas across entities after "sounds good to me" (before/after diff) |

### Knowledge, interaction, messaging, scope, state, ordering

| ID | Test | Driving v2 element | Desired outcome |
|---|---|---|---|
| KN-04 | knowledge_path honored | HA-38 | adoption activity target_path == event's knowledge_path line |
| KN-05 | cross-family specificity | HA-66 | dual-fit content lands in the more specific family, one row |
| KN-06 | directory is structure | HA-66 | prose rejected from directory item |
| KN-07 | asset url hygiene | HA-66 | dead/placeholder url refused or flagged; title+url required holds |
| KN-09 | rejection memory | HA-28, HA-39 | learnings row once; third auto-create blocked; re-proposal under new title refused |
| KN-10 | promotion boundary | 321 | project→company promotion only with approval/event trail |
| IA-03 | child self-containment | 329 | dry-run twin: child executable from its own description alone |
| IA-07 | ids-only cross-room | 313, 329 | recap contains ids, not copied prose (string-diff vs source room bodies) |
| IA-08 | two-agent dedupe | HA-73 | loser agent's log shows dedupe-hit, zero artifact created |
| IA-10 | wake targeting | 316 | Hermes log shows wake POST to coder's profile, not default delegator (validates the TSK-04 semantics twin too) |
| IA-11 | failure etiquette | HA-70, HA-71 | Hermes-down → retry/queue + blocker raised; no silent drops; poller-death → silence (correct), catch-up on restart |
| MS-02 | private stays private | HA-72 (DM surface) | DM content absent from rooms 21–24 bodies/summaries |
| MS-07 | one subject per message | 308 | compound input split correctly or handled singly; no mixed-subject topic |
| MS-08 | kind-labelled ids | 303 | regex: every bare number in bot text has a kind word within 4 tokens |
| MS-11 | no bot decisions | 327 | refusal observed; add_decision_message count by bot uids = 0 (sweep) |
| WA-03 | unresolvable asker | HA-74 | one add_action_message; zero global search calls |
| WA-04 | privacy wording | 325 | exact "I don't see that in your projects"; existence-leak phrasing = FAIL |
| WA-05 | per-asker recompute | HA-75 | same question, two users → two different answer sets (diff) |
| WA-06 | no speaking for Alice | 324 | cites only room-visible artifacts |
| XD-02 | todo-OR-task not both | HA-42 | commitment spawns exactly one of the two surfaces |
| XD-07 | decision→implementation | HA-77 | every ADR "what changes" has linked todo/task in-period |
| XD-10 | redelivery storm | HA-24 | triple-delivered event → 1 artifact (counts) |
| OR-02 | same canonical order for events | HA-32 | 3 decision flows all follow the D7 sequence |
| OR-05 | adjacency battery | HA-61 | cost→finish, list→add, search→create, approve→act pairs all ordered |
| OR-08 | out-of-order events sane | HA-60 | dismiss-before-resolve → no illegal transitions, sane annotations |
| RH-02 | snapshot fidelity | HA-65 | snapshot body == exactly that topic's linked messages |
| RH-03 | refresh not spam | 250 + HA-65 | one evolving snapshot per topic, not N parallel ones |
| ST-03 | claims supported | 332/HA-92 | progress claim rows join ≥1 completed backing row |
| ST-04 | no self-marking | 326 | milestone row UNCHANGED; routing/outcomes artifact instead |
| ST-05 | slip-vs-mitigate is human | 332 | add_decisions_waiting row; target_date byte-identical |
| ST-08 | legacy flags inert | HA-96 | runned/added_to_kanban never written by handlers |
| ST-09 | membership enforced | HA-15, 325 | non-member reads return filtered/none |
| ST-10 | period binding explicit | HA-92/99 | zero items attached to non-current periods |
| HR-01…06 | harness conventions | HA-97 | dry-run logs exist for every D7/D9 item; evidence table complete; noise budget computed; scoreboard filled; regression anchors run first |

## P. Validated by v2 EVENT-INJECTION (the 46 workspace handler items)

| ID(s) | Injected event | Desired handler outcome (+ forbidden twin) | HA |
|---|---|---|---|
| EV-00a | any add-category event | preceding list-category read in log | HA-35/61 |
| EV-00b | same event ×2–3 | one artifact; stop-check logged | HA-24 |
| EV-00c | any state-changing reaction | create_tool_cal_log row mirrors it | HA-61 |
| EV-00d | event w/ ambiguous room/profile | clarification task or nothing — never guessed identity | HA-25 |
| EV-00e | one event | exactly one outcome class (nothing/route/act) | HA-25/46 |
| EV-01,02 | ai_confirm resolved/dismissed | partial-propagate only; own-artifact deletes only; foreign → revert-task route | HA-26, HA-27 |
| EV-03 | double-rejection pattern | one learnings row; third create prevented | HA-28 |
| EV-04,05 | blocker resolved / dismissed | "can proceed" merges; resume-task for owned work; dismissal wording NOT "cleared" | HA-29, HA-30 |
| EV-06…09 | decisions_waiting resolved/approved-3-flows/dismissed | dedupe-then-ADR; routing by target_type (3 distinct handlers); annotation never delete | HA-31…HA-34 |
| EV-10…12 | dependency active/broken/resolved | consumer notes merged; coordination task once; blocker after dedupe; precondition cleared | HA-35 |
| EV-13,14 | company change added/deleted | single material_changes with change id; footprint "re-validate" annotations | HA-36, HA-37 |
| EV-15,16 | knowledge_proposal resolved/dismissed | one-family adoption + activity path; rejection learning, no re-propose | HA-38, HA-39 |
| EV-17…19 | learning added/forbidding/deleted | cited adoption; revoke-question as decision (never silent); withdrawn marking | HA-40, HA-41 |
| EV-20…22 | mention created/resolved/dismissed | profile-mapped routing w/ ids; commitment single-surface; dismissed→log-only | HA-42, HA-43 |
| EV-23…25 | outcome_review resolved success/failure; hearsay | deduped summary; learnings-not-progress on failure; hearsay produces ZERO | HA-44, HA-45, HA-46 |
| EV-26…28 | priority events (3 lookalike flows; approved×2 projects; denied) | correct flow-routing; one task per affected project, never recreate; stale sweeps | HA-47, HA-48, HA-49 |
| EV-29…31 | progress complete/contradiction/degraded | close-only-on-proof; arbitration outcomes_review, zero blind edits; route to owner, zero commentary messages | HA-50, HA-51 |
| EV-32…34 | risk approved/denied | task merges, mitigation dedupe, hedged claims corrected; no invented dates | HA-52 |
| EV-35,36 | all-hands completed/reopened | verify-first; conclusion-only takeaways; reopen→blocker w/ dedupe | HA-53, HA-54 |
| EV-37,38 | todo completed/reopened | tracker close via cost→finished; milestone routing not self-mark; correction merge not delete | HA-55, HA-56 |
| EV-39,41 | project_updated cosmetic/material; moot events | cosmetic→NOTHING; single material_changes; verification-log-only ×5 types | HA-57, HA-59 |
| EV-40 | project_created (empty dir) | knowledge scaffold only-if-empty; activity with event path; route to planner; zero invented milestones | HA-58 |

## Q. Full-coverage statement (machine-checkable)

v1 chats (101–261) + mapping §A–L → 112 items · v2 chats (262–334) → §O rows ·
v2 event-injection & harness → §P rows + §M pointers. Union covers **218/218**
semantic items; every item has exactly one primary driver and a desired-state
assertion. Re-audit: parse §A–L, §O, §P id columns against
`pwr-semantic-checklist.md` ids; expected uncovered = ∅.
