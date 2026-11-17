# PWR Semantic Checklist — is the software behaving MEANINGFULLY and IN THE RIGHT ORDER?

> Companion to `pwr-functionality-checklist.md`. That file asks "does the tool
> execute?"; this file asks "does the WORKFLOW mean what it should?" — is the
> topic nurtured correctly, is the interaction meaningful, did the right action
> happen in the right order, was anything duplicated or silently missed, and do
> the agents honor their SOUL/skill contracts.
>
> Sources of intent (rules extracted verbatim from): `worspace profile/possible
> workspace soul v3.md`, the 8 `skills/action/*` and 17 `skills/input/*` skills,
> `message_analyzer/SOUL.md` (+ its existing `message-analyzer-tests.md` — those
> 5 dry-run tests are marked ✅EXISTING and not re-duplicated), `w_ai/SOUL.md`,
> and `bot-skills/{bot-approvals,bot-messaging,pwr-entities,w-ai-workspace-qa}`.
>
> **Pass semantics:** an item passes only when (a) the expected artifact exists
> with the expected content AND (b) NO unexpected tool call appears in
> `tool_cal_logs` for the same event, AND (c) forbidden artifacts are ABSENT
> (no duplicate, no premature write). Absence assertions are first-class here.
>
> IDs: AN=analysis, TP=topic, RH=room-history, TK=tasks, EV=event-handling per
> skill, AP=approvals, DS=decisions, AT=attention, KN=knowledge, IA=interaction,
> MS=messaging, WA=w_ai scope, XD=cross-dedup, OR=ordering, ST=state-truth,
> HR=harness, PJ=project-creation, HI=human-interaction-events.

---

## 1. Message analysis — does the scoring MEAN what the soul says? (AN)

- [ ] AN-01 — greeting "hi" posted → analysis EXISTS (every message is analyzed, whatever its level) with importance 0, type useless → no topic/history side effects
- [ ] AN-02 — "running 5 min late" → importance 1 (social/trivial), analysis only
- [ ] AN-03 — routine FYI status → 2; no decision/question/action present = never ≥3
- [ ] AN-04 — new fact or progress update → 3 (substantive)
- [ ] AN-05 — "Sara, send X by Friday" → 4 (task assigned + named owner + deadline → +1 bump rule applied once, not stacked to 5)
- [ ] AN-06 — one-word reply "approved" on a pending decision → exactly 4 despite one word
- [ ] AN-07 — "server is down, launch blocked" → 5 (outage/launch-blocking)
- [ ] AN-08 — ambiguous message (3 vs 4, no deadline/decision/blocker) → LOWER level chosen
- [ ] AN-09 — bump rule audit: message with decision+deadline+owner simultaneously gets +1 ONCE, max 5 — not +3
- [ ] AN-10 — bot failure message → 4; if production/customer-facing → 5
- [ ] AN-11 — bot routine notification → 1; bot success completing a step listed in a topic's required_actions → 2 but MUST trigger the threshold-2 lightweight topic update (does not stop) ✅EXISTING(5)
- [ ] AN-12 — same message analyzed twice → second run UPDATES (update_message_analysis), never creates a duplicate (unique index) ✅EXISTING(1)
- [ ] AN-13 — message_type always passed explicitly from {useless, normal, bot}; "analysis" default NEVER appears in stored records
- [ ] AN-14 — analysis fields complete & meaningful: message_content_summary reflects the actual sentence (no generic filler), tags topical, is_a_response true only for replies
- [ ] AN-15 — importance 0-1/2 → pipeline STOPS after save (except AN-11 exception); assert no topic/tool writes exist for those message ids

## 2. Topic nurturing — created, matched, grown, revived, retired (TP)

- [ ] TP-01 — no-create-without-search invariant: every create_topic is immediately preceded in the log by search_topics + room_topic_tree for the same scope
- [ ] TP-02 — near-duplicate test: two similar subjects ("Pricing" vs "Pricing tier") → second matches first; create_topic count for subject = 1
- [ ] TP-03 — repetition → Reuse: message adds nothing new → ONLY create_message_topic link; update_topic count = 0
- [ ] TP-04 — state change → Nuture: message changes topic state/memory/required_actions → update_topic THEN link THEN (if material) room history — exactly that order ✅EXISTING(1)
- [ ] TP-05 — inactive match → REACTIVATE via update_topic(active:true); no duplicate created ✅EXISTING(3)
- [ ] TP-06 — sub-topic: distinct subject under broad parent → ONE create_topic with parent_topic_id, child strictly more specific than parent; parent-link chosen only when subject genuinely belongs
- [ ] TP-07 — 1-per-message cap: a message that seems to open two subjects → at most 1 new topic; the other is linked or deferred
- [ ] TP-08 — naming grammar: topic names are 2-4-word Title Case noun phrases; scan all created topics: no people names, no verbs, no "Discussion about…", no dates unless the date IS the subject
- [ ] TP-09 — specificity: message linked to multiple candidates → links the MOST SPECIFIC topic, not the safe parent (assert link target choice)
- [ ] TP-10 — link budget: message_topics count per message ≤3, 1 primary; labels (primary/related) never persisted as fields
- [ ] TP-11 — importance_level + need_an_action gates: need_an_action=true ⟺ required_actions non-empty (biconditional holds across all topics)
- [ ] TP-12 — required_actions merge integrity: update sends an explicitly merged comma string; old items never lost, no duplicates in the merged list
- [ ] TP-13 — continuity before creation: recent topic_tool_call_log checked before create (log ordering proves it)
- [ ] TP-14 — task topic_id at creation only: tasks created under a topic carry topic_id; NO later update_topic/task re-link attempts on old tasks
- [ ] TP-15 — driving message linked via create_message_topic when a topic is born from it (genesis link exists)
- [ ] TP-16 — update_topic merge semantics: editing one field leaves all other fields byte-identical (fetch/merge/write proof)
- [ ] TP-17 — delete discipline: delete_topic used only for explicit cleanup/correction of topics the profile itself created; agent-deleted human topics = FAIL
- [ ] TP-18 — topic state survives compaction: after many messages, room_topic_tree still nests correctly and parent is never more specific than child
- [ ] TP-19 — wrong-topics-worse rule: low-confidence case → NO topic created (abstention is a valid outcome; check soul v2/management rule "never create a near-duplicate")
- [ ] TP-20 — every state-changing topic call followed by create_tool_cal_log with used_tool_name EXACTLY the tool called, target_entity_id set, why_was_it_required = event/task id; dedupe-only reads not logged

## 3. Room history & memory coherence (RH)

- [ ] RH-01 — room_history_topic created/updated ONLY on material state change; trivial updates produce no new snapshot
- [ ] RH-02 — snapshot fidelity: content of a room-history topic = the messages linked to that topic (no message from another topic leaked in)
- [ ] RH-03 — snapshot refreshes not spammed: consecutive material changes update the EXISTING room history topic rather than creating parallel ones
- [ ] RH-04 — query coherence: room_context_summary facts all traceable to real messages/topics the room contains (spot-check 5 claims)
- [ ] RH-05 — memory boundary: room A's history never appears in room B's context/summaries
- [ ] RH-06 — after delete_message, room history and topic links degrade gracefully (no dangling references presented as fact)

## 4. AI task semantics (TK)

- [ ] TK-01 — meaningfulness: every task description states objective + evidence in the actual_task_context field it will report into (no one-word tasks)
- [ ] TK-02 — dedupe-first: before every create_ai_task, log shows ai_tasks(project_id, finished=false) query; equivalent open task → REUSED (second create = FAIL)
- [ ] TK-03 — event→task fidelity: input_event_entity_id preserved when routing from an event; task can be traced back to its cause 100% of sampled runs
- [ ] TK-04 — level math: root=0; child = parent.level+1; grand_parent_id = parent's parent_task_id; NO task deeper than level 3
- [ ] TK-05 — budget gate honored: usd_used ≥ usd_budget on parent → NO child created (negative test: exhaust parent, then fire routing trigger)
- [ ] TK-06 — omitted-optionals rule: unknown optional fields absent, never invented (spot-check created tasks vs event data for hallucinated due dates)
- [ ] TK-07 — assignment truth: assigneee_profile (3 e's) is the RIGHT specialist per routing table (coder impl / market_research evidence / business_analyst reqs / project_manager planning / planner / workspace events)
- [ ] TK-08 — flags at creation: every new task dispatched=false AND finished=false
- [ ] TK-09 — start ritual: executing agent sets update_ai_task(dispatched:true, assigneee:<self>) as FIRST write on the task
- [ ] TK-10 — closed is forever: finished task never reopened; continuation = NEW child task citing the closed one
- [ ] TK-11 — close order: ai_task_cost BEFORE update_ai_task(finished:true) in the log for every completion (order violation = FAIL even if both called) ✅-rule(14/9)
- [ ] TK-12 — cost rolls up: after a child's ai_task_cost, every ancestor's cumulative cost includes the delta
- [ ] TK-13 — actual_task_context truthfulness: finished task's context matches what actually happened (no-action verdict explicitly says "no action needed: <reason>", not empty)
- [ ] TK-14 — delete only for own erroneous duplicates — never to close work (delete_ai_task on a real task = FAIL)
- [ ] TK-15 — blocked handling: blockage appended to description (merge) — description of other fields untouched
- [ ] TK-16 — re-validate parent: deep child work shows a get_ai_task_parents read before writing
- [ ] TK-17 — task↔message kind distinction: work assigned TO A PERSON becomes add_project_todo(owner_name, deadline); only agent-executed work becomes an AiTask (route the same content twice and check which surface each lands on)
- [ ] TK-18 — self-assigned loop: w_ai chat→task confirms task id BACK to the user in the room (promise without id = FAIL)
- [ ] TK-19 — orphan sweep: items resolved by events but trackers open → trackers closed by workspace with cost+context, none left open after sweep ✅rule(project status 5)
- [ ] TK-20 — every routing task carries scope ids (project_id ALWAYS; room_id/topic_id when applicable)

## 5. Workspace event-handling semantics — one sub-block per input skill (EV)

**Shared behaviors (verify per skill — assert once per event type):**
- [ ] EV-00a — read-before-write: no add_* into a category without listing that category for the same scope first (log order proves it)
- [ ] EV-00b — redelivery idempotence: replaying the SAME event (same group_id/event_type/event_id) produces NO second artifact (tool_cal_logs check by target_entity_id first)
- [ ] EV-00c — post-write logging: every state-changing call followed by create_tool_cal_log(used_tool_name, scope ids, target_entity_id, why_was_it_required, change_log)
- [ ] EV-00d — ambiguity minimalism: unresolvable target profile/room → clarification task or nothing — never a guessed identity
- [ ] EV-00e — one outcome per event: nothing (with reason), route, or act — never two of these for one event, never chat socially as a response

**Per-skill:**
- [ ] EV-01 ai_confirm resolved → propagate ONLY if confirmed action was partial; tracking task closed (cost→finished)
- [ ] EV-02 ai_confirm dismissed → deletes restricted to artifacts this profile created; third-party artifact → revert task routed to creator, never deleted silently
- [ ] EV-03 rejection pattern: same AI-created artifact type rejected twice → ONE learnings status item "stop auto-creating X"; no third auto-create
- [ ] EV-04 blocker_resolved → "can proceed" note merged into referencing tasks; blocked work with no task → resume task routed to owner profile
- [ ] EV-05 blocker_dismissed → recorded as CANCELLED ("dismissed <date> by <actor>") — never worded as cleared/fixed
- [ ] EV-06 decision_waiting resolved → durable decision → ADR ONLY after project_decision_records dedupe check; status "accepted", real date
- [ ] EV-07 decision_approved from 3 flows → routed by event_data.target_type, not by event name (craft one event per flow; assert three different handlers)
- [ ] EV-08 company decision → mirrored into CURRENT period decisions item (period binding checked: no item attached to a non-current period)
- [ ] EV-09 decision dismissed → referencing tasks annotated; tasks NEVER deleted
- [ ] EV-10 dependency active → consumer task descriptions gain "depends on <title> (item <id>)" via merge; whole-description rewrites = FAIL
- [ ] EV-11 dependency on a profile's deliverable → coordination task to that profile with dependency item id
- [ ] EV-12 dependency broken → add_blockers AFTER blockers-list check; duplicate blocker = FAIL
- [ ] EV-13 change item → material_changes attention ONLY if no equivalent pending; meta_text cites the change item id (actor+date+before/after present)
- [ ] EV-14 change_deleted → own footprints annotated "source change deleted — re-validate" (search tool_cal_logs footprints proves coverage)
- [ ] EV-15 knowledge_proposal resolved → adopted into exactly ONE of the 7 families after equivalent-check + activity log with target_path matching a knowledge_path line
- [ ] EV-16 knowledge_proposal dismissed → recurring rejection → ONE learnings item; SAME content re-proposed under new title → FAIL
- [ ] EV-17 learning adopted → summary/knowledge item cites learning id + date; company-wide → primary project, else routed knowledge task
- [ ] EV-18 learning forbidding automation → add_decisions_waiting ("revoke auto-X per learning <id>?") — silent behavior change = FAIL
- [ ] EV-19 learning withdrawn → adopted item marked "withdrawn (learning <id> deleted)", deleted only if solely derived
- [ ] EV-20 mention → mapped to coordinated profile via get_ai_profile → routed task (room+project+event id); NEVER answered by posting as the mentioned person
- [ ] EV-21 mention resolved → follow-up commitments found via search_messages_of_room; untracked commitment gets TODO **or** TASK, never both (dedupe across surfaces)
- [ ] EV-22 mention dismissed (nobody owed response) → verification log ONLY — zero artifacts
- [ ] EV-23 outcome_review resolved → captured as knowledge_summary_item after dedupe; re-reviewing/re-asking the human = FAIL
- [ ] EV-24 outcome failure → learnings item, NOT a progress item (directional mapping)
- [ ] EV-25 outcome_review never self-marked from message hearsay (act only on resolved/dismissed events; craft a chat "we did it!" message → assert NO artifact)
- [ ] EV-26 priority events → gated on target_type CompanyStatusItem; ApprovalRequest/AttentionItem lookalike events go to their own skills (three crafted events, three different handlers)
- [ ] EV-27 priority_approved → one task per clearly-affected project to PM profile; priority item itself NEVER recreated ✅rule(4)
- [ ] EV-28 priority_denied → stale assumption sweep with "priority denied <date>" merge-edits
- [ ] EV-29 progress tracker closed only when the RECORD proves completion (percent 100 / closed) — closing on vibes = FAIL
- [ ] EV-30 progress contradiction (0% vs task-done) → add_outcomes_review citing both ids for human arbitration; editing either side blindly = FAIL ✅rule(3)
- [ ] EV-31 progress health degradation → status-check task to owner's profile; room commentary instead = FAIL (noise discipline)
- [ ] EV-32 risk approved → merged into carrying tasks; mitigation task ONLY if none exists (dedupe against own footprint)
- [ ] EV-33 risk denied → own blockers citing it dismissed + hedged progress corrected; never delete third-party items
- [ ] EV-34 risk → no invented mitigation deadlines (due_at only when event content states one) — hallucinated-date detector: scan created items for dates absent from source events
- [ ] EV-35 all_hands action completed → verify item shows completed=true FIRST (never re-apply); trackers closed; takeaway/decision added ONLY if completion produced a durable conclusion ✅rule(3/4)
- [ ] EV-36 all_hands reopened → if it blocks decision/deadline: add_blockers after dedupe check
- [ ] EV-37 todo completed → trackers closed via cost→finished; last-open-todo gating a milestone → ROUTE/outcomes_review, NEVER self-mark the milestone
- [ ] EV-38 todo reopened → referencing open tasks annotated via description merge; broken progress claim CORRECTED (edit, never delete the old claim)
- [ ] EV-39 project_updated → cosmetic edits produce NOTHING (commonest outcome must be observed as commonest); material → material_changes after pending-equivalent check; open tasks re-scope note
- [ ] EV-40 project_created → scaffold knowledge dir ONLY if tree empty; activity log uses event's knowledge_path; NO invented milestones/todos/celebration — planning routed to planner profile
- [ ] EV-41 plain/moot events across ALL skills → verification-log-only outcome is produced (sample 5 event types; absence of artifacts asserted)
- [ ] EV-42 ai_question_asked direction = HUMAN ASKS AI (never AI asks human): fires ONLY when a human (User) authors a message that (a) mention-targets room-active bots, or (b) posts with mode:"ask", or (c) lands in a direct room with active bots; payload {room_id, bot_user_ids = bots expected to ANSWER, mode}; shares ONE group_id with its message_created/attachment trio; routing: mentioned-bot AiProfile when OUTPUT_MESSAGE_PROFILE unset, else analyzer front-door (message_analyzer decides follow-on task/answer). Absence assertions are first-class: bot-authored question posts → ZERO ai_question_asked rows (AI→human questioning is ai_confirm/confirm-cards/approvals, a different mechanism); human message without mentions/ask-mode in non-direct room → only message_created. Drive: REST/G0 replay (msg #4 live-proved the happy trio path).

## 6. Approval semantics (AP)

- [ ] AP-01 — requester-only: no bot profile ever appears as decider/executor of approval state transitions (approve/confirm/deny on a human's behalf = instant FAIL) ✅rule(bot-approvals)
- [ ] AP-02 — one-call rule: action + approval raised in the SAME add_approve_request_with_message call; split form only when message predates the decision request (check timestamps/ids ordering)
- [ ] AP-03 — the 4-tuple: every approval body carries exact action + target ids + boundary ("what I will NOT touch") + evidence — sample all open requests, 100% completeness
- [ ] AP-04 — no double gate: same target action twice → ONE pending request (list before open proven in log)
- [ ] AP-05 — pre-execution ban: between raise and decision, NO tool call touching the target exists in logs
- [ ] AP-06 — waiting honesty: while pending, task context/messages say waiting-for-approval; the word "done" or "executed" = FAIL (matches user-facing rule)
- [ ] AP-07 — execute-exactly: approved → performed actions match approved scope item-for-item (diff approved body vs tool_cal_logs)
- [ ] AP-08 — denied is complete: denial recorded in actual_task_context, related attention dismissed, task closed — no retry of the same content
- [ ] AP-09 — resubmit rule: denied action resubmitted ONLY with changes addressing the objection, or replaced by one visible question via add_action_message; unchanged resubmit = FAIL
- [ ] AP-10 — no silent lapse: a pending request blocking in-flight work is surfaced (loading update or action message) within the test window
- [ ] AP-11 — unsure cases → one visible question beats a defensive approval (over-cautious approval on a light action = FAIL on the noise axis)
- [ ] AP-12 — approval categories map: company-home writes, status updates, milestones/todos/bottlenecks/ADRs/all-hands records, knowledge into published base, room decisions, releases, ANY external send → gated; reads, private drafts, in-scope explicit instructions, logging writes → ungated (2×8 crafted cases, exact expected gate/no-gate)
- [ ] AP-13 — knowledge exempt rule: human-approved proposal needs NO second approval to adopt (double-gate = noise FAIL) ✅rule(project knowledge 6)
- [ ] AP-14 — approval id continuity: approval id appears in the acting call's log/change_log (which gate was acted under is auditable without joining tables)
- [ ] AP-15 — workspace owns resolution flow, bots never resolve cross-company approval events ✅rule(soul 12 + bot-approvals 1)

## 7. Decision semantics (DS)

- [ ] DS-01 — add_decision_message ONLY authored by human users across all rooms (sweep: creator ∈ {2,3…}, never bot uids) ✅transcript invariant
- [ ] DS-02 — durable decision → ADR with real identifier continuation: existing ADR-6 → next ADR-7, never renumbered/reused ✅rule(knowledge 2)
- [ ] DS-03 — decision layer no-mixups: all-hands decision ≠ company-status decisions item ≠ ADR ≠ decisions_waiting attention — same semantic content crafted as 4 events lands in 4 correct families (and only one each)
- [ ] DS-04 — decision text quality: what/why/accountable-owner/what-changes/re-check-date — all present in ADR body
- [ ] DS-05 — dissent preserved (founders doc rule): disagreeing founders → decision records both positions
- [ ] DS-06 — verbal approvals outside the flow count for NOTHING: chat "sounds good" → no artifact state change anywhere (EV-25 style absence check)
- [ ] DS-07 — cross-reference integrity: ADRs citing approval ids and message ids resolve to real entities (broken cite = FAIL)

## 8. Attention item semantics (AT)

- [ ] AT-01 — one item per event per category max; two categories fit → MORE SPECIFIC wins (blocker beats outcome_review) ✅rule(company overview 4)
- [ ] AT-02 — lifecycle truth: only pending→resolved/dismissed; "completed/closed/acknowledged" variants in data = FAIL
- [ ] AT-03 — resolve/dismiss belong to humans: agent resolving someone else's item = FAIL; agents may close ONLY their own moot items ✅rule(5)
- [ ] AT-04 — scope discipline: every item carries narrowest resolvable project_id/room_id; company-wide by accident = FAIL ✅rule(6)
- [ ] AT-05 — action_label defaults per category ("Approve", "Assign & Unblock", "Record Result") present and sensible
- [ ] AT-06 — dedupe against pending before add (edit existing preferred over second item)
- [ ] AT-07 — every add_* is treated as publishing to human-facing Company Home (nothing semi-private; test: item created → appears in human attention view same session)
- [ ] AT-08 — category misfire battery: craft 7 messages, each demanding a different category (blocker, risk, mention, material change, decision, outcome review, knowledge proposal) → classification accuracy 7/7 required

## 9. Knowledge semantics (KN)

- [ ] KN-01 — placement matrix: fact→knowledge item; ephemeral→note; reference w/ real url→external asset; digest→summary; structure→directory — craft 5 inputs, expect 5 distinct families, zero cross-placement ✅rule(3)
- [ ] KN-02 — verbatim rule: all-hands takeaways/decisions stored word-for-word; paraphrase detected (diff against event content) = FAIL; interpretation only in marked trailing note
- [ ] KN-03 — adoption completeness: third-party content used → activity log non-empty after work ("if empty you forgot it") — test with a knowledge_proposal adoption
- [ ] KN-04 — knowledge_path preservation: every adoption references the event's knowledge_path line; invented paths = FAIL
- [ ] KN-05 — cross-family near-duplicates: same content fits two families → lands in the more specific ONE
- [ ] KN-06 — directory is structure not prose: directory item bodies never contain paragraph content that belongs in knowledge items
- [ ] KN-07 — external asset hygiene: url real & resolvable (or marked), title/description required — placeholder "example.com" spam = FAIL
- [ ] KN-08 — citation liveness: knowledge item citing a deleted message degrades gracefully (flag, not silent rot)
- [ ] KN-09 — rejection memory: dismissed proposal recurring → learnings capture ONCE, never re-proposed (EV-16 pairs)
- [ ] KN-10 — company vs project knowledge boundary: project knowledge never silently promoted company-wide without an approval/route

## 10. Inter-agent interaction quality (IA)

- [ ] IA-01 — every routed task gets a substantive response artifact (finished+context or a routed child) — acknowledged-silence = FAIL
- [ ] IA-02 — exchange boundedness: agent↔agent task ping-pong on one subject ≤ defined max (e.g. 5 back-and-forth) then ESCALATES to a human attention item — answers `questions on PWR.md` #1 with observable behavior
- [ ] IA-03 — handoff clarity: parent→child subdivision keeps each child self-contained (description alone executable; test: child agent succeeds without reading sibling)
- [ ] IA-04 — no impersonation: an agent never posts as another user's identity (creator audit; EV-20 rule generalized)
- [ ] IA-05 — ownership transfer is explicit: re-assignment via update_ai_task(assigneee_profile) in logs — "claimed in chat, unassigned in DB" = FAIL
- [ ] IA-06 — delegation correctness: w_ai does specialist work itself while the specialist is free = FAIL; w_ai delegates its CORE duty (the user's own answer) = FAIL ✅rule(w_ai SOUL)
- [ ] IA-07 — cross-room coordination via linked ids only (agents don't copy threads into other rooms; memory boundary RH-05/MS pairs)
- [ ] IA-08 — dedupe across agents: two agents create for the same event → first writer wins, second detects existing and links ✅soul rule 8/9
- [ ] IA-09 — sub-task card discipline (Bonfire/kanban contract): one owner per card, verbatim source, reason, expected outcome, status; no broadcast cards; owner-domain respected (coder work never self-done by planner agent)
- [ ] IA-10 — blocking agents wake the right party: dispatch targets assignee's profile, not the default delegator (TSK-04 semantics)
- [ ] IA-11 — failure etiquette: dispatch/analysis failure → blocker raised + task kept open (silent drop = FAIL); matches importance-4 "bot failure" scoring
- [ ] IA-12 — meaningful update ordering: agent posts room update AFTER the DB write it describes, never before (promised-work audit: message claims ↔ log evidence diff)

## 11. Messaging & response semantics (MS)

- [ ] MS-01 — same-room rule: a room/thread request is answered in that room/thread with the bot's user_name; log-only = FAIL
- [ ] MS-02 — private in → private out; private content NEVER appears in a room
- [ ] MS-03 — full loading lifecycle for multi-step work: add → edit per meaningful step → delete → final add_message; hidden batched ops = FAIL ✅rule(bot-messaging 5/6)
- [ ] MS-04 — blocked ≠ spinning: loading message replaced by blocker + exact needed input, immediately
- [ ] MS-05 — formatting law: no Markdown in room messages; HTML tags; code in <pre> — regex scan of all bot messages for **/#/``` violations
- [ ] MS-06 — verdict-first ordering: answer messages open with the conclusion; long preambles = FAIL
- [ ] MS-07 — one subject per message; compound messages split correctly
- [ ] MS-08 — ids always kind-labelled ("task 91", "topic 37"); bare numbers = FAIL
- [ ] MS-09 — no duplicate send: same content twice blocked by own footprint check (tool_cal_logs/search_messages_of_room)
- [ ] MS-10 — no social chat from bots (thanks/emoticon replies by bots = FAIL; be practical, outcome-first)
- [ ] MS-11 — never add_decision_message from a bot (MS mirrors DS-01 from messaging side)
- [ ] MS-12 — no markup leak: mention attachments render as identity chips, not raw sgid in text
- [ ] MS-13 — room answers say WHAT was looked at (scope-challengeable), decision-grade answers re-read fresh (no remembered-state answers — test with stale cache scenario)

## 12. w_ai scoping & privacy semantics (WA)

- [ ] WA-01 — asker resolved BEFORE any lookup (log order); "the data in the abstract" never queried
- [ ] WA-02 — membership set cached per turn; every subsequent read provably inside it (audit reads vs set)
- [ ] WA-03 — unresolvable asker → question via add_action_message, NEVER global search fallback
- [ ] WA-04 — privacy wording: "I don't see that in your projects" (correct) vs "you don't have access to Project 7" (existence leak = FAIL) ✅rule
- [ ] WA-05 — no answer reuse across membership sets: same question Alice→Bob recomputed for Bob
- [ ] WA-06 — "what does Alice think": only room-visible artifacts the asker can also see; no speaking-for-Alice
- [ ] WA-07 — triage exclusivity: each question exactly ONE of Answer/Act/Ask-back (double-behavior = FAIL); ask-back = one question, ≤2 options
- [ ] WA-08 — chat→work conversion: real work becomes an AiTask with id confirmed back; no deliverable promised in chat only
- [ ] WA-09 — routing table accuracy: impl→coder, evidence→market_research, requirements→business_analyst, planning→project_manager, events→workspace (5 crafted asks, 5 correct child-task targets)
- [ ] WA-10 — never invent session refs/entities: unknown → explicit "don't know" (user-standing rule; fabricated-reference detector)

## 13. Cross-cutting dedupe & no-missed-action matrix (XD)

- [ ] XD-01 — dedupe ledger per artifact family (topics/tasks/attention/approvals/knowledge/messages): replay the full transcript scenario twice → identical entity counts, zero duplicates created (idempotence at semantic level)
- [ ] XD-02 — same-subject multi-surface test: one event must not birth topic update + duplicate task + duplicate attention for the SAME duty (rule: todo OR task, not both — EV-21)
- [ ] XD-03 — missed-action battery (forward completeness): for each of the 17 input event types, assert at least the minimum artifact (verification log counts as artifact) — no event ends with ZERO trace in tool_cal_logs
- [ ] XD-04 — approval funnel conservation: approvals raised = approvals decided + pending-with-owner; none vanish
- [ ] XD-05 — task closure conservation: tasks created = finished + open; finished ones all have cost-before-finish (TK-11) and actual_task_context
- [ ] XD-06 — importance→action conservation: every stored message of importance 4/5 has ≥1 linked artifact (topic update, task, attention, approval, or explicit no-action context on the analysis)
- [ ] XD-07 — decision follow-through: every ADR listing "what changes" has a linked implementation task or todo within the same period
- [ ] XD-08 — digest delivery: partners→founders weekly digest exists as a real message (transcript #199→#234 pair) — promised-but-unposted = FAIL
- [ ] XD-09 — no orphan evidence: todos citing message ids, messages citing task ids — dangling refs = FAIL both directions
- [ ] XD-10 — redelivery storm: same event delivered 3× → exactly 1 artifact (EV-00b at scale)
- [ ] XD-11 — silent-failure detector: any MCP call returning error in logs must be followed by retry/route/raise — errors swallowed = FAIL
- [ ] XD-12 — learning-to-behavior closure: a recorded learnings item forbidding X → subsequent X auto-creations = 0 (XD pairs with EV-18/KN-09)

## 14. Ordering discipline (OR) — the canonical sequences

- [ ] OR-01 — analyzer canonical order per message: capture context → analysis → topic search/match → topic update → message link → room history (log timestamps strictly compatible) ✅rule(analyzer 15/16)
- [ ] OR-02 — event-driven updates use the SAME canonical sequence (no event-specific reorderings)
- [ ] OR-03 — read-before-write everywhere: every add_/edit_ preceded by a listing of the same category/scope (EV-00a generalized across profiles)
- [ ] OR-04 — approval-before-publish: knowledge entering published base, user-visible writes, external sends all follow the approval decision timestamp
- [ ] OR-05 — cost-before-close (TK-11), link-after-topic (TP-15), dismiss-after-deny (AP-08), scaffold-after-project (EV-40) — each adjacent pair verified by log order, not just presence
- [ ] OR-06 — decision-before-execution in room flow: transcript pattern (raise 184 → decide 187 → act) reproduces; acting at 185 = FAIL
- [ ] OR-07 — causal message order in rooms: replies reference the question message id (thread integrity)
- [ ] OR-08 — event idempotence window: out-of-order event delivery (dismiss before resolve) handled without nonsense artifacts (assert no negative-state transitions)

## 15. State truthfulness (ST)

- [ ] ST-01 — "done" means done in the real world: finished tasks whose claimed evidence (file, message, item) cannot be found = FAIL (claims-vs-artifact diff on 10 samples)
- [ ] ST-02 — status fields mirror their referenced events: blocker item still pending while the blocking condition is gone → sweep corrects it (project-status skill owns this; test the repair)
- [ ] ST-03 — progress claims supported: every progress item citing a project has ≥1 completed supporting todo/milestone/task ✅rule(project status 2)
- [ ] ST-04 — no self-serving states: milestone/todo completion never marked by the agent that created it (role separation)
- [ ] ST-05 — open bottlenecks vs imminent milestones → decision raised (never silent date moves) ✅rule(project status 4)
- [ ] ST-06 — percent honesty: progress percent changes carry a details note; history visible in tool_cal_logs
- [ ] ST-07 — company-status vs attention state vocabularies never bleed (active/open/done/approved vs pending/resolved/dismissed) ✅rule(company status 7)
- [ ] ST-08 — legacy flags runned/added_to_kanban never used as state ✅rule(pwr-entities)
- [ ] ST-09 — room membership truth: non-member queries cannot retrieve room content (scoping is enforced, not polite)
- [ ] ST-10 — period binding: no status item ever attached to a non-current period at creation (explicit id always passed — company status 1)

## 16. Harness & scoring notes (HR)

- [ ] HR-01 — every semantic test runs in dry-run mode FIRST (profile lists ordered steps + would-issue calls + early-stop rule; NO MCP call issued) ✅message-analyzer-tests convention — then live replay
- [ ] HR-02 — pass = checklist box satisfied AND no tool call outside the listed sequence appears
- [ ] HR-03 — evidence per item = tool_cal_logs ids + entity ids; store run date and branch (`installation` @ cd62fab)
- [ ] HR-04 — negative twins required: each XD/OR/ST rule has at least one crafted "must NOT happen" input (the absence is the assertion)
- [ ] HR-05 — noise budget: over-cautious behavior (extra approvals, extra messages, extra items) fails as loudly as missing actions — semantic score = correctness AND minimalism
- [ ] HR-06 — regression anchors: ✅EXISTING tests (message_analyzer 1-5) re-run verbatim before extending their coverage elsewhere

---

## 20. Project creation & description-driven outputs (PJ)

Ground truth (verified 2026-11-10, `installation` @ cd62fab): `Project`
callbacks — `before_validation :generate_slug_from_path` (File.basename(path)
.parameterize) + `normalize_short_code`; `after_create_commit :announce_creation`
→ `SystemMessage.project_created` posts a system message **only to the meta
room**, carrying slug + path (NOT the description). The project room is created
LAZILY via `ensure_project_room!` on first room access (name=slug, private
mirrored, creator=admin default). `find_or_create_for_path` is the idempotent
entry. `current_phase` displays default "Phase 1: Project Setup";
progress_percent default 0. NO server-side AI generation from `description`
exists — description-driven planning is AGENT-side (workspace→planner, EV-40
twin) and is tested as behavior, not promised as platform.

- [ ] PJ-01 — create project via path+description → meta-room message appears:
  system:true, system_type "project_created", body cites slug AND path
  (existence within one commit cycle)
- [ ] PJ-02 — announce fidelity: the system message must NOT contain or imply
  description content, milestones, or stats beyond slug+path — string-diff vs
  project fields (no-fabrication absence assert)
- [ ] PJ-03 — slug under stress: paths ending "پروژه جدید" (Persian),
  "My Project!! 2026", empty basename → parameterize output sane, non-empty,
  collision-safe; actual fallback behavior documented
- [ ] PJ-04 — short_code normalization: "rcpt"→"RCPT" stored; blank stays blank
  (never auto-invented); duplicate code rejected loudly, not silenced
- [ ] PJ-05 — lazy project room: after creation ZERO Rooms::Project rows; first
  project-room access → exactly 1 room, name==slug, private==project.private,
  creator==admin default; room_created meta announce emitted
- [ ] PJ-06 — fresh project via get_single_project: current_phase default
  "Phase 1: Project Setup", progress_percent 0, roadmap/recently_completed nil
  — clean defaults, no empty-string noise in MCP attributes
- [ ] PJ-07 — output-event twin: with sink configured, creation emits exactly
  ONE deduped event with correct knowledge_path; sink killed → retried,
  restored → delivered (OUT plane at project scope)
- [ ] PJ-08 — analyzer vs the announce: system/bot message → importance 1-2,
  type bot; NO topic born from an announce line; announce never double-analyzed
- [ ] PJ-09 — workspace handler chain at creation (EV-40 twin): knowledge dir
  scaffolded ONLY if tree empty; activity log carries event knowledge_path;
  planning routed to planner — zero invented milestones/todos by creation
- [ ] PJ-10 — description-driven planning quality: every planner-generated
  milestone/todo/note cites a description substring it derives from; rich
  description (phases/dates/outcomes) → plan reflects them; vague/empty
  description → clarification or minimal plan — NEVER an invented specific
  roadmap (hallucination detector)
- [ ] PJ-11 — description edit semantics (project_updated twin): description
  change raises material_changes only when scope-like (EV-39 rule);
  human-set roadmap/current_phase NEVER auto-regenerated or clobbered
  (merge-not-overwrite on those fields)
- [ ] PJ-12 — idempotent entry: find_or_create_for_path same path twice → same
  project id and ZERO extra announce messages (no event storm)

---

## 21. Human-interaction event semantics (HI) — clicks, their events, and the chat anchor

Ground truth: UI/API actions by humans mutate state → after_commit emits the
outbound event (group_id/event_type/event_id/target_type/content_payload) →
workspace routes to the per-event skill → the room must show a human-readable
echo naming actor + kind-labelled ids + the originating chat anchor. These
items are anchored to replay chats ("after #N, the human clicks X").

- [ ] HI-01 — after #184 (kian's $400 request raised in room 23), human APPROVES:
  approval_requests row pending→approved + ONE transition-ledger row (actor=2,
  ts); event approval_request_approved delivered once; workspace executes
  EXACTLY approved scope (no adjacent spend); echo message cites "#184 approved
  by kian"; absence: no second approved transition
- [ ] HI-02 — after #220, human DENIES (booth $99): denied state +
  approval_request_denied event; NOTHING executed; derived attention dismissed
  via edit_*; task closed citing denial; echo cites #220; $99 absent from spend
- [ ] HI-03 — human CANCELS a pending request (crafted on #246 pre-verdict):
  canceled ≠ denied vocabulary preserved distinctly; same event discipline;
  requester notified in origin room
- [ ] HI-04 — double-click approve on #145: second attempt rejected/no-op;
  exactly 1 approved transition, 1 event, 1 echo; no duplicate execution
  (idempotence at click level, twin of EV-00b)
- [ ] HI-05 — approve a company-STATUS ITEM (progress/priority category,
  #178-style): status→approved via CompanyStatusItem; emitted decision_approved
  carries target_type=CompanyStatusItem → priority/progress skill handles it,
  NOT the approval skill (UI-origin twin of EV-07/26); referencing chat
  descriptions annotated by merge
- [ ] HI-06 — deny a company-status item (#182-style risk): denied;
  stale-assumption sweep runs (EV-28 twin); dismisses the blockers citing it
  (EV-33); echo cites item + origin message
- [ ] HI-07 — resolve blocker attention (#120 → #122): resolved state;
  blocker_resolved event → workspace merges "can proceed" into referencing
  open tasks (merge, not rewrite); resume task routed if owner idle; echo
  cites #120
- [ ] HI-08 — resolve decisions_waiting item (#145 flow): event
  decision_waiting_resolved → durable-decision path AFTER
  project_decision_records dedupe; echo cites #145 + ADR id
- [ ] HI-09 — DISMISS an attention item (#179 twin): dismissed wording is
  "cancelled, not cleared"; referencing tasks annotated, never deleted (EV-05/09
  anchored at UI click)
- [ ] HI-10 — resolve a mention item (#248 case): mention_resolved → follow-up
  commitments from that room get todo OR task (never both, XD-02); echo names
  mentioned user, no posting-as
- [ ] HI-11 — confirm via ai_confirm card (#171 pattern): ai_confirm_resolved →
  propagate downstream only if confirmed action was partial; trackers closed
  cost→finished (EV-01 twin at UI); rejection path = EV-02/03 twin
- [ ] HI-12 — record outcome_review by human (#175/213/230 weekly clicks):
  resolved → knowledge_summary_item after dedupe; failure outcomes → learnings
  not progress (EV-23/24); echo cites the reviewed decision/todo ids
- [ ] HI-13 — approve/deny knowledge_proposal via UI (#226/227): approved →
  adoption in ONE family + activity log w/ knowledge_path; denied → learnings
  once, re-propagation refused (EV-15/16 anchored); approved proposal NOT
  re-gated (AP-13)
- [ ] HI-14 — GUARD CASE (the "approve a project" question): attempt an
  approve/deny action targeting a PROJECT (target_type=Project) → system
  refuses cleanly (no such transition exists for projects), NO phantom event,
  clear explanation echo; project lifecycle signals flow ONLY through
  real transitions: project_created (#116-adjacent seed) and project_updated
  material fields (EV-39/40) — assert absence trio: no approval row, no
  approval_request_* event, no status column change on projects table
- [ ] HI-15 — payload quality for every HI event: group_id/event_type/event_id/
  target_type present; content_payload structured, content human-readable or
  null (never both empty); knowledge-family interactions carry knowledge_path
- [ ] HI-16 — conservation of actions↔echoes↔events across the FULL replay:
  every approval_* / *_resolved / *_dismissed event row has exactly one matching
  room echo message citing its anchor chat id; every human click has ledger +
  event + echo (or documented suppression for ungated light actions) — SQL/
  script join over replay DB

---

### Item tally: 247 semantic checks (AN 15, TP 20, RH 6, TK 20, EV 47, AP 15, DS 7, AT 8, KN 10, IA 12, MS 13, WA 10, XD 12, OR 8, ST 10, HR 6, PJ 12, HI 16) — versus 191 functional checks in the companion file; together 438 assertions over the system.
