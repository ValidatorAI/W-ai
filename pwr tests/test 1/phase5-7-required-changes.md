# Phase 5–7 — Required Changes

Repo: `W/pwr` @ `bbdcb73` · 2026-11-16. Owners: [COPILOT] code · [HERMES] souls/skills (mine) · [USER] approval.

## MUST

### F21 [HERMES, BLOCKED ON USER APPROVAL] — w_ai answered a non-member's questions with full project internals

Evidence: flux (user 13) has ZERO rows in memberships (never granted anywhere). Asked in room 2:
"which projects have open approvals / what is in the receipts project". w_ai replied (msgs 615, 616)
listing approval ids, counts, project internals. The SOUL rule exists ("answer only from what the
ASKER can see") but has an exploitable hole: the bot scoped by the ROOM the question sat in.

Drafted amendment (to `W-ai/w_ai/SOUL.md` §Privacy boundary — apply needs your go, protected file):
- ASKER scope, never room scope: before any project-content answer run `get_user_projects` for the
  asker's id; if target project not in set -> non-disclosure template ONLY, zero counts/names/ids.
- Loading/":spin:" progress messages obey the same gate.
- A non-member question gets the template reply; silence is never a valid answer.
- Counter-example recorded from this incident (613 -> 615/616).

Acceptance when applied+mirrored: re-post flux's exact two questions -> expect template-only reply
("I don't see that in your projects…"), zero project identifiers, and a tool_cal row citing the
membership check.

### F22 [COPILOT] — creation tools have no payload idempotence; *_created feedback loop observed

Evidence: 3 rapid `add_mentions` same title -> 3 rows + 3 events; agents then created 17 more
identical rows over 22 min (each row fires mention_created, a handler responds by creating rows).
Loop decayed only because room-less rows stopped matching. Cleanup by test-owner (17 rows deleted).

Paste for Copilot:

"Add creation-side idempotence to the attention pool item tools (add_blockers, add_mentions,
add_ai_confirm, add_knowledge_proposals, add_outcomes_review, and the REST create endpoints for the
same families): before insert, check for an EXISTING pending item with same category + normalized
title + project_id created within the last 10 minutes; if found, return the existing item id (with
a `deduped: true` marker in the response) and DO NOT create a row or fire a *_created event. Title
normalization: strip/casefold/trim. Also accept an optional `idempotency_key` argument — when
present, dedupe on that key instead of title (stored in meta or a new column). This closes a real
observed feedback loop: 3 MCP calls -> 20 rows because *_created consumers re-registered the same
subject. Tests: (1) two identical add_mentions within window -> one row, one event, deduped flag on
second response; (2) same idempotency_key twice -> same behavior; (3) distinct titles unaffected;
(4) after the window a new identical row is allowed (it's a recurrence, not a burst)."

### F23 [COPILOT, small] — attention_items has no creator attribution; agent writes are untraceable

Evidence: the 17 loop rows carried no tool_cal rows and no creator column — HR-05 audit impossible;
we cannot name the offending profile, which also blocks the S5-contract enforcement fix.

Paste for Copilot:

"Add `created_by_id` (users FK, nullable) + `created_channel` (varchar: 'mcp'|'api'|'web') to
attention_items, populated on creation in the shared model path (both planes). Backfill existing
rows as null/'unknown'. Include it in the REST/MCP serialization so audits can attribute pool-item
writes; require the MCP write tools to stamp the acting bot's user id (they already resolve bot
identity for messages). Spec: create blocker via MCP -> row exposes created_by_id + created_channel;
web create stamps the human."

## SHOULD
### O-8 [HERMES] — dedupe 'Answer:' tasks by (question-text, asker, room), not global title
2 twin Answer-tasks from replay pressure. Small wording addition to analyzer routing bullet + w_ai
task-dedupe check; my deploy once F23 gives attribution. 

### M9 — product decision still open (descope EV-35 vs build add_dependencies). Nothing gates on it.

## GOOD
- HA-96 INV battery (TZ read-back, trailing-space room duplicate, `<script>` render path, README
  route parity) — still deferred from Phase 2; belongs to an ops-night batch with the HA-78
  destructive fresh-DB double replay if you ever want the strict XD-01.

## Order
1. F21 — needs your approval word; then I deploy+mirror+acceptance-replay (15 min).
2. F22 + F23 in one Copilot PR (same tool family); F23 first makes any future loop attributable.
3. O-8 after F23 lands (need attribution to write the right rule).
