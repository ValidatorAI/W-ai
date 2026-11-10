# PWR feature-probe conversations — Receipts project (test 1)

Fictional chat logs of the two employees (**kian** – founder/infra, **roya** –
founder/GTM) across the four project rooms, plus their bot teammates. Every
message is annotated with the PWR feature it exercises, and the sequence
intentionally includes **expected-fail probes** (locked fields, autonomous
external sends, agent self-decisions) so running this transcript against the
live app proves which features work and which don't.

## Shared tables (single global `messages.id` across all four rooms)

| Entity | id | kind |
|---|---|---|
| project `receipts` | 7 | project |
| room `receipts-build` | 21 | room |
| room `receipts-growth` | 22 | room |
| room `receipts-founders` | 23 | **decision_room** |
| room `receipts-partners` | 24 | room |
| user `kian` | 2 | human |
| user `roya` | 3 | human |
| user `main` | 4 | bot (Hermes) |
| user `coder` | 5 | bot (Hermes) |
| user `market_research` | 6 | bot (Hermes) |
| user `w_ai` | 7 | bot (Hermes) |
| guests nimbus/orbit/vector/flux/halo | 11–15 | human (external) |

- Message ids come from the shared `messages` table; **higher id = later send**.
- Bodies are shown as stored: ActionText HTML; `@name` = mention attachment
  (`application/vnd.campfire.mention`); 📎 = file attachment; `[tool: …]` = the
  MCP call that created/mutated the item behind the message.
- Counts: build 51, growth 32, founders 41, partners 37 — **161 messages**, ids
  101–260 + 261, unique across all four rooms.
- Days are narrative time; per-room counts below, 161 total.

---

## Room 21 — receipts-build

| id | day | author (uid) | message | feature probed |
|---|---|---|---|---|
| 101 | D1 | kian (2) | Kickoff. @roya (3) you own dashboard, @main (4) coordinate, @coder (5) execute. | add_message + 3 mention attachments |
| 103 | D1 | roya (3) | `[tool: create_ai_task]` id=441 "proxy skeleton" usd_budget=25, **token_budget=10** | task create; ⚠️ token_budget expected-reject (not writable via MCP) |
| 104 | D1 | main (4) [bot] | woken by dispatcher → `[tool: get_ai_task(441)]` context pulled | dispatch loop wake + pull-model |
| 106 | D1 | coder (5) [bot] | Progress 1/3: policy hook wired `app.rb: <pre>guard?(call) { approve! }</pre>` | bot message + ActionText `<pre>` |
| 109 | D1 | kian (2) | Holding reservation on `proxy/*` — roya, your ledger edit will conflict; please wait | file_reservation: reserve → conflict inspect |
| 112 | D1 | roya (3) | Scope change: defer SSE to W5. @kian (2) `[tool: add_approve_request_with_message]` | cross-room approval raise |
| 115 | D1 | kian (2) | 📎 architecture.md — the proxy/ledger split | attachment → action_text_rich_texts/ActiveStorage |
| 117 | D1 | main (4) [bot] | `[tool: create_topic]` "proxy"; pinned msg 106 | topics + message pin |
| 119 | D1 | roya (3) | `[tool: create_room_history_topic]` snapshot "proxy-w1" | room history snapshots (topic-scoped) |
| 121 | D1 | coder (5) [bot] | Ledger CLI done → `[tool: update_ai_task(441, finished)]` | task lifecycle close |
| 124 | D1 | kian (2) | +1 | boost/reaction |
| 126 | D1 | roya (3) | @main (4) roll up cost for 441 | mention a bot (poll expectation) |
| 127 | D1 | main (4) [bot] | `[tool: ai_task_cost]` 441 → $8.40 / $25 | cost query |
| 130 | D1 | kian (2) | (edit of 103: "see #152 for locked-field result") | message edit |
| 132 | D1 | coder (5) [bot] | Reservation released on proxy/* | reservation release |
| 136 | D1 | main (4) [bot] | ⏳ … | add_loading_message probe |
| 139 | D1 | roya (3) | `[tool: search_messages_of_room("reservation")]` → 3 hits | room search |
| 142 | D2 | kian (2) | `[tool: room_topic_tree("proxy")]` shows topic + child 119 | topic tree |
| 146 | D2 | roya (3) | `[tool: delete_message(136)]` | delete own message |
| 149 | D2 | main (4) [bot] | Daily standup: 441 closed, 1 task open | client-poller digest |
| 152 | D2 | roya (3) | `[tool: create_ai_task]` 442 "approval gate" — then tried `update_ai_task(442, project_id=8)` | ⚠️ locked-field probe: expected no-op/reject |
| 155 | D2 | coder (5) [bot] | 442 2/3: egress verbs intercepted | progress convention |
| 158 | D2 | roya (3) | Retry of locked-field probe, second param set — same result | failure documentation |
| 161 | D3 | kian (2) | 2nd reservation conflict today — that's a process bug; @coder (5) add test | conflict discipline + follow-up task |
| 165 | D3 | main (4) [bot] | Split 442 → child 455 "integration docs" (`get_ai_task_children` reflects) | parent/child chains |
| 167 | D3 | roya (3) | `[tool: room_context_summary]` → correct summary of this room | context tool |
| 170 | D3 | coder (5) [bot] | Finding: fail-open mishandled egress verb; `[tool: add_risks]` | risk attention family |
| 174 | D3 | kian (2) | +1 on 170; edited 170 to add severity=high | boost + edit bot message? ⚠️ edit-by-non-author probe |
| 177 | D3 | main (4) [bot] | `[tool: add_project_milestone]` "dashboard v0" | milestones |
| 181 | D3 | roya (3) | `[tool: search_rooms("proxy")]` finds rooms 21, 23 | global search |
| 185 | D3 | coder (5) [bot] | Approval gate DONE → finished; evidence #182 linked | evidence-linked completion |
| 189 | D3 | kian (2) | mvp-proxy milestone hit → `[tool: room_evidence]` posted | evidence capture |
| 192 | D4 | main (4) [bot] | Tree: 442→455,456; all dispatched flags flipped | dispatch bookkeeping |
| 196 | D4 | coder (5) [bot] | SSE child closed (W5 deferred item from #112) | cross-room decision carried out |
| 200 | D4 | roya (3) | `[tool: get_users(user_name="kian")]` → resolved uid 2 | fuzzy name resolution |
| 204 | D4 | kian (2) | Reservation renewed mid-edit — lifecycle works | reserve→renew |
| 206 | D4 | main (4) [bot] | 📎 dashboard-first-view.png | bot attachment |
| 210 | D4 | roya (3) | Cleaned leftover loading messages (delete batch) | delete flow again |
| 214 | D4 | coder (5) [bot] | Regression for #170 passes → test added | risk closure |
| 218 | D4 | roya (3) | OSS announcement live: link (I pressed send, not an agent) | human-gated external send |
| 221 | D4 | roya (3) | `[tool: search_topics("dashboard")]` → 2 | topic search |
| 225 | D4 | kian (2) | `[tool: room_decision_context]` → decisions affecting this room: ADR-001..003 | decision context |
| 228 | D4 | main (4) [bot] | Children report: 455 done, 456 90% | hierarchy status |
| 231 | D5 | coder (5) [bot] | Batch-approval skeleton done (from #229) | cross-room request → build |
| 235 | D5 | roya (3) | Released all reservations; room quiet | reservation hygiene |
| 239 | D5 | main (4) [bot] | Week plan digest | scheduled digest |
| 242 | D5 | coder (5) [bot] | Cost view on dashboard done | feature progress |
| 247 | D5 | kian (2) | Verdict evidence: #189, #190, #240 | evidence links into decision flow |
| 250 | D5 | main (4) [bot] | Archived room-history snapshot "final-w5" | history archive |
| 254 | D5 | roya (3) | Final `ai_task_cost` rollup: $1,842 total | cost reporting |
| 258 | D5 | kian (2) | `[tool: add_project_todo]` retro, owner both, due Mon | todos |

---

## Room 22 — receipts-growth

| id | day | author (uid) | message | feature probed |
|---|---|---|---|---|
| 108 | D1 | roya (3) | @market_research (6) list 20 agent-using teams with horror stories | bot mention + poll model |
| 111 | D1 | market_research (6) [bot] | Candidate A: thread link → `[tool: add_external_knowledge_asset]` | sourced evidence asset |
| 114 | D1 | roya (3) | `[tool: add_project_todo]` "OSS README rewrite" owner=roya due=Fri | todos w/ owner+deadline |
| 118 | D1 | kian (2) | Plane added agent workflows — link | competitor intel |
| 123 | D1 | roya (3) | Outreach template draft `<pre>` full text — needs approval before ANY send | content + approval-gate awareness |
| 128 | D1 | market_research (6) [bot] | 5 candidates scored; `[tool: create_message_analysis]` importance per thread | message analysis |
| 134 | D2 | roya (3) | Sent batch-1 to 8 teams (human hands on keyboard) | external send by human only |
| 138 | D2 | roya (3) | `[tool: add_knowledge_activity_log]` contact #1 | knowledge activity |
| 143 | D2 | market_research (6) [bot] | Scan 2: community pain signals @roya (3) | recurring scan + mention |
| 150 | D2 | roya (3) | Todo "Product Hunt — W13" with deadline | planning todo |
| 156 | D2 | kian (2) | Edited 143 with corrected link | edit another's? ⚠️ permission probe |
| 162 | D3 | market_research (6) [bot] | LangSmith now shows policy hooks — table | competitor table |
| 168 | D3 | roya (3) | README hero copy `<pre># Your agents acted. Who approved?</pre>` | rich HTML |
| 172 | D3 | market_research (6) [bot] | Source: HN thread id 41… | citation rule |
| 178 | D3 | roya (3) | Pipeline: 20→8→2 | funnel status |
| 183 | D3 | kian (2) | `[tool: add_knowledge_proposals]` pricing-vs-competitors table (needs approval) | knowledge proposals flow |
| 188 | D3 | roya (3) | Thanks — +1 on the scan | boost |
| 193 | D4 | roya (3) | PH draft (title/tagline) `[tool: add_approve_request_with_message]` | launch-copy approval |
| 197 | D4 | market_research (6) [bot] | Churn-signal scan: 3 "guard fatigue" posts | signal scan |
| 203 | D4 | roya (3) | Todo "demo video script" owner=mr-agent reviewed by me | assignment |
| 208 | D4 | market_research (6) [bot] | Plane table refreshed | evidence update |
| 212 | D4 | roya (3) | Pipeline 20→12→5 | funnel |
| 216 | D5 | roya (3) | OSS announcement draft → approval → | gate before publish |
| 223 | D5 | market_research (6) [bot] | PH checklist 14 items | checklist |
| 227 | D5 | roya (3) | FAQ draft cites #137 #164 verbatim (partner words) | citation of partner room ids |
| 232 | D5 | market_research (6) [bot] | Competitor blog: "approvals are governance theatre" — response angle | reactive intel |
| 237 | D5 | roya (3) | Content freeze until verdict (#246) | process control |
| 241 | D5 | market_research (6) [bot] | Churn counter: 0 churned, 2 stalled | metrics |
| 245 | D5 | roya (3) | 35 teams on waitlist 🎉 | milestone |
| 251 | D5 | market_research (6) [bot] | Post-validation scan queued | scheduling |
| 255 | D5 | roya (3) | Waitlist triage started | ops |
| 259 | D5 | kian (2) | Growth retrospective folded into retro todo #258 | cross-link |

*(32 messages — growth kept lean on purpose; the validation load sits in partners.)*

---

## Room 23 — receipts-founders (decision_room)

| id | day | author (uid) | message | feature probed |
|---|---|---|---|---|
| 102 | D1 | kian (2) | Proposed standing thresholds (spend>$200, external-send=human, destructive=reservation+approval) → `[tool: add_approve_request_with_message]` | ADR-001 initiation |
| 105 | D1 | roya (3) | Approval req: domain purchase $120 | small spend (below gate → informational) |
| 107 | D1 | kian (2) | `[tool: add_decision_message]` YES, domain | decision by human |
| 110 | D1 | main (4) [bot] | `[tool: add_project_decision_record]` ADR-001 auto-captured after approval | auto-ADR |
| 113 | D1 | roya (3) | (decision on #112 SSE defer, see below) | — |
| 120 | D1 | roya (3) | `[tool: add_blockers]` CI flaky | blockers attention family |
| 122 | D1 | kian (2) | Resolved blocker 120 | resolve transition |
| 129 | D1 | roya (3) | Approval req: logo $180 + rationale msg | approval-with-message |
| 133 | D1 | roya (3) | `[tool: add_outcomes_review]` week-0 checklist | outcomes review |
| 135 | D1 | kian (2) | Decision: logo approved | decision |
| 140 | D2 | kian (2) | Weekly cost review: $8.40 of $25 on 441 | cost ritual |
| 145 | D2 | roya (3) | Approval req: Pro tier $29→$49 | pricing decision |
| 148 | D2 | kian (2) | Decision: hold until PH — reasoning `<pre>` 3 bullets | reasoned decision |
| 153 | D2 | roya (3) | `[tool: attention_items]` queue: 1 open | attention queue |
| 159 | D2 | kian (2) | ADR-002 recorded (pricing hold) | ADR |
| 163 | D3 | roya (3) | Proposal: 24h decision SLA | policy proposal |
| 166 | D3 | kian (2) | Decision: SLA yes → ADR-003 | decision+ADR |
| 171 | D3 | kian (2) | Approve hotfix policy for #170; regression task requested | cross-room approval |
| 175 | D3 | roya (3) | `[tool: outcomes_review]` week 1 | review |
| 180 | D4 | kian (2) | Resolved w_ai's self-filed blocker #179; process todo | resolution |
| 184 | D4 | roya (3) | Approval req: $400 ad budget | above-gate spend |
| 187 | D4 | kian (2) | Decision: $400 approved, condition: CAC report by W6 → ADR-004 | conditional decision |
| 191 | D4 | roya (3) | decisions_waiting queue: empty ✅ | queue state |
| 194 | D4 | kian (2) | Decision: PH date confirmed | decision |
| 198 | D4 | roya (3) | Review trigger: hire #3 at sustained 3 teams — recorded | policy |
| 201 | D4 | kian (2) | Burn: $11,480 / $42,100 — on plan | budget review |
| 205 | D4 | roya (3) | Approval req: DPA template | legal |
| 209 | D4 | kian (2) | Decision: DPA approved | decision |
| 213 | D5 | roya (3) | outcomes review wk2 | review |
| 217 | D5 | kian (2) | Decision: announcement ship today | decision |
| 220 | D5 | roya (3) | Approval req: conference booth $99 | spend |
| 224 | D5 | kian (2) | Decision: NO — cash to month-6 → ADR-005 | denial recorded |
| 230 | D5 | roya (3) | outcomes wk3 | review |
| 234 | D5 | kian (2) | Audit: all approvals this week had evidence ✅ | audit |
| 238 | D5 | roya (3) | Created decision topic "pivot-evidence" | decision topic |
| 243 | D5 | kian (2) | Pre-verdict memo (links #247) | memo |
| 246 | D5 | roya (3) | Approval req: VALIDATION VERDICT — proceed vs pivot | the big decision |
| 249 | D5 | kian (2) | `[tool: add_decision_message]` PROCEED — 5/5 met, dissent noted → ADR-006 | verdict + ADR |
| 253 | D5 | roya (3) | Decision: case study allowed | decision |
| 257 | D5 | kian (2) | outcomes recap → decision topic | recap |
| 260 | D5 | roya (3) | ADR index knowledge item closed | close-out |

*(41 messages. All decision messages authored by uid 2/3 only — bots never
called add_decision_message here, which is itself a behavior assertion.)*

---

## Room 24 — receipts-partners

| id | day | author (uid) | message | feature probed |
|---|---|---|---|---|
| 116 | D1 | kian (2) | Pinned welcome. One question: what did an agent do that you can't explain? | room creation + pin |
| 125 | D2 | roya (3) | Added guest nimbus (11) | membership add (scoped user) |
| 131 | D2 | kian (2) | Welcome @zzz (no such user) | ⚠️ invalid mention → fuzzy-fail probe |
| 137 | D2 | nimbus (11) | Story: agent dropped prod table, no one could say who allowed it | raw horror story |
| 141 | D2 | w_ai (7) [bot] | First-touch reply (scoped: product-only) | bot polling + scope discipline |
| 144 | D2 | roya (3) | Triaged 137 → `[tool: add_project_todo]` importance=4 cites #137 | evidence-linked todo |
| 147 | D3 | nimbus (11) | Install question; w_ai answered from knowledge items | knowledge-scoped answer |
| 151 | D3 | roya (3) | Install evidence form posted | intake |
| 154 | D3 | nimbus (11) | Installed! Guard on deploy verb | install event |
| 157 | D3 | w_ai (7) [bot] | Routed "per-run cost cap" → todo imp4 (cites 182 later) | routing rule |
| 160 | D3 | roya (3) | Thanks — weekly digest promised | SLA |
| 164 | D3 | nimbus (11) | Story 2: unapproved deploy last quarter | story |
| 169 | D4 | w_ai (7) [bot] | Validation counter: **1/5** wired | counter |
| 173 | D4 | roya (3) | We'll review cost-cap this week | commit (proposal only) |
| 176 | D4 | roya (3) | Added orbit (12) | membership |
| 179 | D4 | w_ai (7) [bot] | ⚠️ SLA miss on orbit's Q — self-filed `[tool: add_blockers]` | bot filing attention against itself |
| 182 | D4 | orbit (12) | $312 mystery agent run last week — approver unknown | cost story |
| 186 | D4 | w_ai (7) [bot] | "cost cap" todo formalized | routing |
| 190 | D4 | roya (3) | Orbit install evidence asset | evidence |
| 195 | D4 | roya (3) | Month-2 check-in Q sent to nimbus | cadence |
| 199 | D5 | w_ai (7) [bot] | Weekly unresolved digest → posted to founders (#234 audit used it) | cross-room digest |
| 202 | D5 | orbit (12) | "Almost didn't install because: proxy in prod path" | objection evidence |
| 207 | D5 | w_ai (7) [bot] | Counter: **2/5** | counter |
| 211 | D5 | w_ai (7) [bot] | Merged duplicate feature request via topic move | dedup discipline |
| 215 | D5 | roya (3) | vector (13) invited | membership |
| 219 | D5 | kian (2) | Repo stars +340 since announcement — external factor noted | signal |
| 222 | D5 | vector (13) | Story: approval fatigue after 40 low-risk prompts | story |
| 226 | D5 | w_ai (7) [bot] | Proposed batch-approval policy → `[tool: add_project_knowledge_item]` (proposal state) | knowledge proposal |
| 229 | D5 | roya (3) | Cross-room request to build (→ #231) | partners→build routing |
| 233 | D5 | nimbus (11) | Tried batch approval — works, one edge: renew timers | field feedback |
| 236 | D5 | w_ai (7) [bot] | Counter: **3/5** | counter |
| 240 | D5 | roya (3) | flux (14) wired their CI-agent deploys today | 4th install |
| 244 | D5 | w_ai (7) [bot] | halo (15) wired + flux confirmed → counter: **5/5** 🎯 | validation met |
| 248 | D5 | roya (3) | Case-study consent from nimbus | permission |
| 252 | D5 | roya (3) | Case study draft → approval req (→ #253) | gate |
| 256 | D5 | w_ai (7) [bot] | Scheduled monthly check-ins `[tool: create_ai_task]` | recurring task |
| 261 | D5 | partners | Team thanks thread 🎉 | social |

*(37 messages; partners room intentionally message-light per real customer chat.)*

---

## What running this transcript proves (pass/fail assertions)

**Expected PASS (features working):** mentions resolve to vnd.campfire.mention
attachments (101); ActionText `<pre>`/HTML bodies (106/168); file attachments
(115/206); dispatch wake → `get_ai_task` pull (103→104); task lifecycle +
children (121/165/196); `ai_task_cost` (127/254); approval-with-message →
decision → auto-ADR chain (184→187 → ADR-004); attention families
add/edit/resolve (120/122/170/179); room history + topic tools (117/119/142/221);
context/search tools (139/167/181/225); fuzzy user resolution (200); boosts
(124); deletes (146/210); knowledge proposals/assets/activity (111/183/138/226);
milestones/todos (177/114); membership adds (125/176).

**Expected FAIL (documented gaps, probed on purpose):**
- #103 `token_budget` rejected/ignored by `create_ai_task` (MCP surface gap)
- #152/#158 `update_ai_task` cannot move locked fields (`project_id`)
- #156 edit of another author's message → expect permission error
- #131 invalid mention `@zzz` → fuzzy resolution failure, message still posts
- Any autonomous external send (pattern after #134) → agents must be blocked;
  only humans post links (174 vs 218)
- No bot ever calls `add_decision_message` (23's invariant, assert by query)
- Silence when no poller runs (126 → 127 requires main's client attached)

**Replay recipe:** create project `receipts` + rooms 21–24 on the live app, then
POST messages in id order via `/action-mcp` (humans) and Hermes profiles (bots),
running each `[tool: …]` annotation for real and asserting the pass/fail column.
The shared-id table above is the test script.
