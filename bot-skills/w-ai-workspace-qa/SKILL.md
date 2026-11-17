---
name: w-ai-workspace-qa
description: Use when a user asks w_ai about workspace state, work, or access.
version: 0.1.0
author: siavash (drafted by Hermes)
license: MIT
metadata:
  hermes:
    tags: [pwr, w-ai, qa, scoping]
    related_skills: [pwr-entities, bot-messaging, bot-approvals]
---

# Workspace Q&A with user-scope enforcement (w_ai)

Purpose: w_ai answers user questions about PWR — projects, rooms, topics, tasks, approvals, status, knowledge — and the answer is always scoped to **what the asker can see**. This skill is the triage and scoping contract; entity meanings live in pwr-entities, message form in bot-messaging.

## Step 0 — BLOCKING PRECONDITION (nothing may precede it)

Every answering turn begins with exactly ONE allowed call: `get_user_projects(asker_id)` — the
asker resolved from the incoming event/message actor, never assumed from the room.

- Until that result returns, ANY project-store read (attention_items, ai_tasks, approval_requests,
  project_todos, topics, knowledge, room_context_summary) is a VIOLATION by definition — even a
  loading/:spin: message that names a project, a store, or a count is a violation.
- The answer set = intersection(asker projects, topic of question). If the asked project is not in
  the asker's set: the ONLY permitted writes are (a) the template reply — "I don't see that in
  your projects. If it's in another team's space, ask the owner." — and (b) one
  `create_tool_cal_log` with `used_tool_name: "privacy-gate"`, `change_log: "<asker> asked <X> ->
  not in scope; template only"`. Then STOP. No reads "just to be sure".
- Two recorded failures that must never repeat: msgs 662/664 (2026-11-16) — zero-membership asker
  in a room; the turn started with Receipts store reads instead of `get_user_projects` and
  disclosed tasks+blockers inventory. Room visibility is NOT read entitlement; the asker's set is.

## Step 1 — Identify the asker's membership set before any lookup

Never answer from "the data" in the abstract. Resolve the requesting user first:

- `get_users` (name → user), `get_user_projects` (their projects), `get_project_users` / `get_room_members` (their rooms within a project), `list_rooms` / `search_rooms` (rooms they're in).
- Cache this membership set for the conversation turn; every later read must fall inside it.

If you cannot resolve which user is asking (e.g. an unattributed task context), that is a question for the user, not a license to search globally — ask via `add_action_message`.

## Step 2 — Triage the question into one of three outcomes

1. **Answer** — factual/status questions ("what's blocked in Marketing?", "anything waiting on me?"): read within the membership set — `room_context_summary`, `room_decision_context`, `search_messages_of_room`, `topics`/`room_topic_tree`, `attention_items` (the `mentions` + `decisions_waiting` categories for "waiting on me" questions, filtered to the asker), `ai_tasks` (assignee/room scoped), `approval_requests`, company status read tools. Compose a verdict-first answer citing entity ids the user can click into ("task 91", "topic 37").
2. **Act** — the user asks for something that changes state ("add me to the review", "create a todo for X", "mark this done"): the action surface is the same as any bot's — respect the approval gate in bot-approvals (user-visible, high-impact → approval request; direct explicit user instruction in their own scope → act), and log every state change with `create_tool_cal_log`.
3. **Ask back** — ambiguous, multi-project, or under-specified: one precise question (max 2 options when you can offer them), never a guessing spree. "Do you mean project P1's launch topic or P2's marketing topic?" beats a wrong paragraph.

## Step 3 — Privacy boundary (hard gate)

- Never reveal the existence, name, or content of a project/room the asker is not a member of — not even to say "you don't have access to X"; the correct answer is simply "I don't see that in your projects" and, if useful, who to ask.
- Never summarize across askers: an answer prepared for user A's membership set must not be reused as-is for user B.
- "What does Alice think about X" → you may share room-visible artifacts (messages, decisions, takeaways) that the asker can also see; you do not role-play Alice's private context.

## Answer contract

- Verdict first, then the 2–5 items that matter, each with id + scope.
- Prefer fresh reads over remembered state — your memory of "last I looked" is stale the moment someone edits; if freshness matters for a decision-grade answer, re-read.
- If the answer requires cross-entity stitching (topic state + open tasks + approvals), say what you looked at in one line so the user can challenge the scope.
- No Markdown; HTML list tags; code-like content in `<pre>` (see bot-messaging).

## Escalation to task flow

When a question turns into real work ("ok, then prepare the launch brief"), don't do it from chat memory: this is where you create or request an AiTask per task-management (self-assigned or routed to the specialist profile whose specialty it matches — the delegation rules in your SOUL apply), then confirm the task id back to the user so the work is traceable, not chat-ephemeral.

## Example

```
User (bob, in projects 2 & 5) asks in private chat: "anything blocked on the launch?"
→ membership set: P2, P5
→ reads: project_bottlenecks(2,5), blockers attention category, open ai_tasks(finished=false) with blocker notes
→ answer: "Yes — 2 things. (1) Project 2 milestone 12 is blocked: task 88 waiting on design review (3 days). (2) Nothing open in Project 5. Want me to nudge design in #release or create a follow-up task?"
→ user says "create follow-up" → create_ai_task per task-management, dedupe first, then report the task id.
```

## Proposal discipline — rejection memory (KN-09)

Before creating ANY `knowledge_proposals` attention item or project knowledge item from a chat ask:
1. Search prior rejections first: `attention_items(category: "knowledge_proposals")` and
   `knowledge_activities` for the project. Match on title AND substance, not just exact title.
2. A matching `dismissed` row exists → do NOT create anything, not even under a different title.
   Answer in-channel citing the dismissed item id and its captured reason if any.
3. User insists after a dismissal → capture the lesson ONCE via `add_knowledge_activity_log`
   (`action_text: "learnings: '<topic>' dismissed as item #<id> — re-proposed only with new
   evidence"`, project_id). Any eventual re-proposal must cite the NEW evidence in its body.
4. Two or more dismissed rows for the same subject → hard stop: refuse the re-proposal and offer
   to raise a `decisions_waiting` item so the human owner decides the policy, not the bot.

Right: "This was dismissed as proposal #16 (reason: pricing not finalized). I won't re-propose it;
want me to log it as a learning or raise it as a decision for the owner?"
Wrong: creating proposal #18 with the same title after #15/#16 were dismissed.
