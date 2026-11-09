---
name: topic-management
description: Use when matching, updating, or creating PWR topics.
platforms: [linux]
---

# Topic management (PWR / Space Knowledge MCP)

Procedure for the message analyzer: given an already-saved message analysis, decide which
topic(s) the message touches and apply the smallest correct topic change. This skill covers
topics only — message scoring and importance gates live in the SOUL.

Every rule below is a hard gate: follow the literal IF/THEN, do not improvise.

## Rule zero — never skip

1. NEVER call `create_topic` in this run unless `search_topics` was called first AND its
   result was checked. WRONG: message arrives → `create_topic`. RIGHT: `search_topics` →
   read results → decision table → action.
2. Create AT MOST 1 new topic per message.
3. Link a message to AT MOST 3 topics: 1 primary + up to 2 related. Use `create_message_topic`
   (stores only `message_id` + `topic_id` — no relationship field).
4. Link to the MOST SPECIFIC matching topic. WRONG: linking "Q3 ad spend" to "Advertising"
   when "Q3 Campaign Performance" exists. RIGHT: link to "Q3 Campaign Performance".
5. Do NOT link to a parent topic just because it feels safer.

## Topic entity quick reference

| Field | Type | Rule |
|---|---|---|
| name | string | 2-4 words, Title Case noun phrase; no people names, no verbs, no "Discussion about..." |
| parent_topic_id | int or empty | child must be MORE specific than parent |
| related_topics | string | comma list: "topic 1, topic 2" |
| active | boolean | inactive topics get reactivated, never duplicated |
| importance | int 0-5 | 5 = urgent/critical, 0 = dormant |
| memory | string | 1-2 sentences, rolling context of the topic |
| state | string | 1-2 sentences, where the topic stands now |
| need_an_action | boolean | true REQUIRES non-empty required_actions |
| required_actions | string | comma-joined short actionable items; merged, never silently overwritten |

Naming litmus test: if you cannot say in one sentence why the child is more specific than the
parent, the pairing is wrong — do not create it.

## Decision table (after searching)

| Situation | Action | Then |
|---|---|---|
| Matches active topic, adds nothing new | Reuse | `create_message_topic` only — STOP after linking |
| Matches active topic, changes state/memory/actions/importance | Update | `update_topic` → link → step "Room history" |
| Matches inactive topic | Reactivate | `update_topic` set active=true (+ field changes) → link → step "Room history" |
| Only broad parent matches, message is a distinct subject with own state/actions | Create child | `create_topic` with parent_topic_id → link |
| Nothing matches | Create new | only if ALL 3 creation criteria below are true |

Creation criteria — all three must hold, otherwise reuse/reactivate/link only:
1. No existing topic, active or inactive, covers the subject.
2. The subject will have its own state or required actions, or will recur.
3. It is not a one-off remark.

## Procedure — ordered, literal

1. Search: call `search_topics` scoped to the room/project using the message tags and key
   nouns; call `room_topic_tree` to see the hierarchy.
   DONE when: you have a candidate list (possibly empty) and the current tree.
2. Disambiguate only if needed: call `tool_cal_logs` / `get_topic` ONLY IF the best
   candidate is ambiguous, overlaps a prior topic state, or might need reactivation.
   Do NOT fetch logs for every message.
   DONE when: one candidate chosen, or "no match" confirmed with logs checked for the room.
3. Apply the decision table. One action row per message (update beats reuse; reactivate beats
   create).
   DONE when: the table row and its tool calls are executed.
4. Merge actions correctly (see next section) whenever you touch required_actions.
5. Link: `create_message_topic` — 1 primary + up to 2 related, most specific first.
   DONE when: 1-3 links created, no duplicates of existing links.
6. Room history: IF a topic's state meaningfully changed (new state, reactivation, new
   decision), THEN `create_room_history_topic` or `update_room_history_topic` with
   room_id + topic_id + a 1-sentence last_state summary.
   IF nothing meaningfully changed, THEN skip — do NOT write a snapshot.
   DONE when: snapshot written or skip condition confirmed.

## required_actions — merge semantics

The tool does NOT merge. To ADD an action you must:
1. `get_topic` → read the current required_actions value.
2. Build the full merged string yourself: "existing_1, existing_2, new_1".
3. `update_topic` sending the COMPLETE merged string.
WRONG: sending only the new action (erases the old list).
WRONG: need_an_action=true with empty required_actions.
DONE when: the stored value contains every prior action plus the new ones.

## Self-check before finishing (all must be YES)

- [ ] `search_topics` was called before any `create_topic`.
- [ ] At most 1 topic created; at most 3 links; links point to most specific topics.
- [ ] Any new topic name is 2-4 words, Title Case, no verbs, no people names.
- [ ] Any child topic is strictly more specific than its parent (provable in one sentence).
- [ ] required_actions values were read and merged, not overwritten.
- [ ] need_an_action=true only where required_actions is non-empty.
- [ ] Room history written only on meaningful state change.

## Pitfalls

- Duplicate topics: almost always caused by skipping step 1 or matching only exact names —
  search by tags and related topics, and check inactive topics before creating.
- Over-linking: linking parent + child + project topic "for safety" violates rule 5.
- Log spam: fetching `tool_cal_logs` on every message wastes tokens; step 2 is
  conditional by design — "needs no logs" is a valid, common answer.
- Silent overwrite: update_topic replaces fields you send; send merged required_actions, and
  do not send fields you did not intend to change.
- Stale reactivation: a previously handled topic found in logs → reuse/reactivate it instead
  of creating a look-alike.
