# Message Analyzer SOUL — Dry-Run Tests

Five test messages to run against the message-analyzer profile.
The profile must NOT call any MCP tools. For each test it only shows, in order, the steps it would take and the exact tool calls (tool name + arguments) it would have issued, based on the hypothetical search results given in the test.

## Shared dry-run instruction (paste with each test)

> You are processing the message below under your SOUL. This is a DRY RUN: do not call any MCP tool, do not write anything. Output:
> 1. The ordered steps you will take, per the canonical workflow.
> 2. For each step, the exact tool call you would issue with all arguments, or "no call" with the reason.
> 3. Where the workflow stops early, say which rule caused the stop.
> Use only the hypothetical tool data provided; assume searches return exactly that.

---

## Test 1 — Duplicate analysis guard (importance 4, existing analysis)

Rules exercised: canonical step 2 (check `message_analysis` by `message_id` first; update, never create), processing threshold 3-5, additive required_actions read-merge-send.

Message payload:
```json
{
  "project": { "id": 1, "name": "Product Launch" },
  "room": { "id": 201, "name": "Marketing" },
  "sender": { "id": 77, "name": "Ava Chen", "is_bot": false },
  "message": {
    "id": 9050,
    "content": "We agreed: go with the competitor pricing review before Friday's launch briefing. Sara owns it."
  }
}
```

Hypothetical tool data:
- `message_analysis` filtered by `message_id: 9050` returns one existing record: `{ "id": 12, "importance_level": 3, "message_content_summary": "Pricing review needed before launch briefing.", "message_type": "normal", "tags": "pricing, launch", "is_a_response": false }`
- `search_topics` in room 201 returns: `{ id: 5, name: "Market Research", active: true, state: "pricing data under review", memory: "pricing above target", required_actions: "Compare Product A pricing with top competitors", need_an_action: true }`

Expected checklist:
- [ ] Step 1 analysis call is `update_message_analysis` with `message_analysis_id: 12` — NOT `create_message_analysis` (unique index on message_id).
- [ ] Updated importance_level = 4 (decision made + named owner), `message_type: "normal"` passed explicitly, summary/tags included.
- [ ] Proceeds to topic matching (importance 3-5 rule).
- [ ] Topic 5: `update_topic` with state/memory changed; required_actions sent as merged comma string containing the EXISTING action plus the new one(s) — no reliance on automatic merge.
- [ ] `create_message_topic` links message 9050 to topic 5 (primary).
- [ ] `create_room_history_topic` (or update) for room 201 + topic 5 because state meaningfully changed; passes both `room_id` and `topic_id`.

---

## Test 2 — Useless greeting stops after analysis

Rules exercised: importance scale 0, processing threshold "0-1: stop", message_type `useless`, dedupe check still performed.

Message payload:
```json
{
  "project": { "id": 3, "name": "Marketing Ops" },
  "room": { "id": 305, "name": "Daily Updates" },
  "sender": { "id": 88, "name": "Leah", "is_bot": false },
  "message": { "id": 9051, "content": "Hi team, good morning!" }
}
```

Hypothetical tool data:
- `message_analysis` by `message_id: 9051` returns empty (no prior record).

Expected checklist:
- [ ] Checks for an existing analysis first, sees none, then calls `create_message_analysis` with importance_level 0, `message_type: "useless"`, explicit (not defaulted) type.
- [ ] Explicitly states it STOPS: no `search_topics`, no topic update, no `create_message_topic`, no room history — citing the "importance 0-1: stop after saving the analysis" rule.
- [ ] Does not invent a topic for a greeting.

---

## Test 3 — Inactive topic must be reactivated, not duplicated

Rules exercised: create-vs-update table row "Matches an inactive topic", naming limits, room history on state change.

Message payload:
```json
{
  "project": { "id": 1, "name": "Product Launch" },
  "room": { "id": 201, "name": "Marketing" },
  "sender": { "id": 42, "name": "Omar", "is_bot": false },
  "message": {
    "id": 9052,
    "content": "Back to the logo rebrand question — design wants to kill the old mark next sprint. Need sign-off from brand."
  }
}
```

Hypothetical tool data:
- `message_analysis` by `message_id: 9052` returns empty.
- `search_topics` returns: `{ id: 8, name: "Logo Rebrand", active: false, state: "on hold since Q2", memory: "old mark kept for print", required_actions: "Decide fate of old logo mark", need_an_action: true }`
- `room_topic_tree` shows "Logo Rebrand" as a child of "Marketing".

Expected checklist:
- [ ] `create_message_analysis` (no prior record) with importance_level 4 (sign-off requested = decision pending) and explicit `message_type: "normal"`.
- [ ] Chooses Update/Reactivate: `update_topic` on id 8 setting `active: true` plus new state/memory and merged required_actions. Does NOT call `create_topic` — no duplicate topic.
- [ ] `create_message_topic` links 9052 to topic 8.
- [ ] Room history snapshot created for room 201 + topic 8 (state materially changed).

---

## Test 4 — New child topic under a broad parent, link limits

Rules exercised: creation criteria, at most 1 new topic, at most 3 links (1 primary + up to 2 related), naming rules (2-4 words, Title Case, no verbs/people), child more specific than parent.

Message payload:
```json
{
  "project": { "id": 1, "name": "Product Launch" },
  "room": { "id": 201, "name": "Marketing" },
  "sender": { "id": 77, "name": "Ava Chen", "is_bot": false },
  "message": {
    "id": 9053,
    "content": "Let's start planning the booth and swag budget for the November expo. Deadline is end of next week."
  }
}
```

Hypothetical tool data:
- `message_analysis` by `message_id: 9053` returns empty.
- `search_topics` returns only broad matches: `{ id: 3, name: "Marketing", active: true }` and `{ id: 5, name: "Market Research", active: true, memory: "pricing work; nothing about events" }`.
- `room_topic_tree`: "Marketing" has children "Market Research", "Advertising". No event/expo topic exists anywhere.

Expected checklist:
- [ ] Analysis created with importance_level 4 (deadline within timeframe + task), explicit type.
- [ ] Creation criteria stated: no active/inactive topic covers it, subject will recur, not one-off → ONE `create_topic` call.
- [ ] New topic name is a 2-4 word Title Case noun phrase (e.g. "Expo Booth Planning"), `parent_topic_id: 3` (under Marketing), and it must be MORE specific than the parent.
- [ ] New topic carries state, memory, `need_an_action: true` with non-empty `required_actions` (paired rule).
- [ ] Links: primary = new topic; may add "Marketing"/"Product Launch" as related but TOTAL links ≤ 3. Should prefer the most specific level and not pad links.

---

## Test 5 — Bot failure vs bot success of a tracked step

Rules exercised: bot-message importance rules, threshold-2 exception, room history.

Message A payload:
```json
{
  "project": { "id": 1, "name": "Product Launch" },
  "room": { "id": 202, "name": "Release Readiness" },
  "sender": { "id": 11, "name": "Deploy Bot", "is_bot": true },
  "message": { "id": 9054, "content": "ERROR: deployment failed on step 3 (db migration). Rollback pending human confirmation." }
}
```

Message B payload:
```json
{
  "project": { "id": 1, "name": "Product Launch" },
  "room": { "id": 202, "name": "Release Readiness" },
  "sender": { "id": 11, "name": "Deploy Bot", "is_bot": true },
  "message": { "id": 9055, "content": "Deployment completed successfully. Health checks passed." }
}
```

Hypothetical tool data (applies to both):
- No prior `message_analysis` for 9054 or 9055.
- `search_topics` returns: `{ id: 9, name: "Deployment Plan", active: true, state: "migration step pending", required_actions: "Complete deployment checklist and confirm release readiness,Run db migration step 3", need_an_action: true }`

Expected checklist:
- [ ] Message A: importance_level 4 (bot failure), `message_type: "bot"`; proceeds to topic handling (3-5); updates topic 9 state (blocker/rollback), merged required_actions; links message; room history snapshot for room 202 + topic 9.
- [ ] Message B: importance_level 2, `message_type: "bot"` — but does NOT stop, because it completes a step tracked in topic 9's required_actions (threshold-2 exception): performs the lightweight `update_topic` (completed step removed/adjusted via merged value, state refreshed) and a room history update; still creates/links `message_topic` at most — must justify any link beyond the exception's "lightweight topic update".
- [ ] Neither test lets `message_type` default to "analysis"; both run the existing-analysis check before create.

---

Scoring note: a run passes a test when every checklist box is satisfied and no tool call outside the listed ones appears. Any `create_message_analysis` when a prior record exists (Test 1) is an automatic fail.
