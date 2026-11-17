---
name: pwr-entities
description: Use when interpreting any PWR entity, id, page, or status as a bot.
version: 0.1.0
author: siavash (drafted by Hermes)
license: MIT
metadata:
  hermes:
    tags: [pwr, bots, entities]
    related_skills: [task-management, topic-management]
---

# PWR entities — the bot's view

Purpose: know what the things around you **are** and what they mean for your work. This is the dictionary, not the procedure: you don't get write rules for company-home or status items here (that is workspace's job) — you get meaning, so an id, event, or page someone points you at resolves into a real thing.

Distilled from the workspace soul v3 (verified against live `Mcp::Registry` 2026-11-02), the message_analyzer soul, and the task-management skill (verified against `db/schema.rb` + `app/services/mcp/tools/tasks.rb`). Re-verify with `list_tools` on `/config-mcp` before trusting a tool name.

## The shape of PWR

Company → Projects → Rooms → Threads → Messages. Topics, tasks, approvals, status items, and knowledge all hang off project/room scope. PWR exposes all of it over six MCP endpoints (`/mcp` aggregate, `/action-mcp`, `/read-mcp`, `/knowledge-mcp`, `/task-mcp`, `/config-mcp`).

## Core entities

### User / Bot
People and agent profiles share the `User` space (`actor.type: "User"` in events). A bot acts under its own profile name (`user_name`/`bot_name` fuzzy fields). `get_users`, `get_room_members`, `get_project_users` tell you who is in scope. When a human @mentions you, the mention is also an attention item (`mentions` category).

### Room & Thread
The conversation surface; your memory boundary. Messages live in rooms and threads; each room has its decisions, evidence, and economics (read: `room_context_summary`, `room_decision_context`, `room_evidence`, `room_economics`, `search_messages_of_room`). Rule: knowledge you use is room + project + company only — never another room's.

### Message
Sent by a user or a bot. Every message you post is later scored by message_analyzer into a `message_analysis` record: `importance_level` 0–5, `message_type` ∈ {`useless`, `normal`, `bot`} (never rely on the literal `"analysis"` — invalid classification a helper may default to), `content_summary`, `tags`, `is_a_response`. Write one subject per message with ids spelled out — it makes your work traceable.

### Topic
The subject spine of a room: `name` (2–4 words), `parent_topic_id` (child strictly more specific than parent), `related_topics`, `importance_level` 0–5, `memory` (rolling 1–2-sentence context), `state` (where it stands now), `need_an_action` + `required_actions` (the boolean true REQUIRES the non-empty list), `active`. When a task or event carries a `topic_id`, that topic's `memory`/`state` is the current truth of the subject — read it before acting; link your outcome messages to the most specific matching topic (mechanics in the topic-management skill).

### AiTask (`task-mcp`, 8 tools)
The work order. Key fields, with the traps: `assigneee_profile` has three e's; there is no `title` and no `status` — `dispatched`/`finished` are the only flags; `parent_task_id`/`grand_parent_id`/`level` (root 0, max depth 3) are NOT named `parent_id`; scope links `project_id` (always set by convention) / `room_id` / `topic_id`; `input_event_entity_id` is your dedupe anchor; `proposed_task_context` = what was known at creation, `actual_task_context` = what you learned; costs move only via `ai_task_cost` (which rolls deltas to all ancestors). Full lifecycle in the task-management skill.

### ApprovalRequest
A human decision gate. Statuses: `pending` → `approved` / `confirmed` / `denied` / `canceled` (delivered to workspace as `approval_request_*` events). Payload carries `title` + decision text. As a bot you are the **requester**: see the bot-approvals skill.

### AttentionItem (company home)
The company's "needs eyes" queue. Categories (canonical plural keys): `decisions_waiting`, `blockers`, `outcomes_review`, `mentions`, `material_changes`, `ai_confirm`, `knowledge_proposals`; statuses `pending` / `resolved` / `dismissed`. Written via `add_<category>` / `edit_<category>`. For you: your raised blocker or question may surface here; treat company-home writes as workspace-owned unless a task explicitly assigns it.

### CompanyStatus (period + 7 categories)
A time-boxed org narrative: `CompanyStatusPeriod` with items `priorities`, `progress`, `risks`, `dependencies`, `changes`, `decisions`, `learnings`. Read it to know what the company is optimizing for this period; it is NOT the attention category `decisions_waiting` and NOT all-hands decisions — the word "decision" has three homes in PWR.

### Project items
`project_milestones` (dated goals), `project_todos` (work slices), `project_bottlenecks` (blockers at project level). Your task's success criteria often reference a milestone; report against them by id.

### All-hands
Meeting record per project: `takeaway` (what was learned), `decision` (what was decided), `action_item` (who does what; completion/reopening generates events). A task may originate from an action item — check `input_event_entity_id`.

### Project knowledge
Seven domains: knowledge items, decision records (ADRs), notes, directory items, external assets, activities, summary items. Events and tools speak of a `knowledge_path` (e.g. `/company/<id>/projects/<id>/knowledge`) — project-backed inputs carry one; preserve it when recording knowledge.

### tool_cal_log
The audit trail every state-changing call leaves: `used_tool_name`, scope ids (`project_id`/`room_id`/`topic_id`), `target_entity_id` (the dedupe anchor), `change_log` (one human line), `why_was_it_required`. For you it has two jobs: it is your obligation after each action (see task-management / your SOUL), and it is the first place to check whether you already handled a delivery.

### Kanban board
Hermes-side (not a PWR entity): one board per room; work the user explicitly approved or confirmed in the room goes onto that room's board. It complements AiTasks — kanban is room-visible progress, AiTask is the machine work order. Keep ids of both in `actual_task_context`.

## Status/lifecycle cheat sheet

| Entity | States | Notes |
|---|---|---|
| AttentionItem | pending → resolved / dismissed | dismissal is still a resolution |
| ApprovalRequest | pending → approved / confirmed / denied / canceled | confirmed usually finalizes after approved |
| AiTask | created → dispatched (when assignee starts) → finished | only the assignee flips dispatched; nobody "cancels" — erroneous dupes get deleted |
| Topic | active / inactive | inactive topics get reactivated, never duplicated |
| Topic action | need_an_action=true ⇒ required_actions non-empty | always together |

## Naming traps (never trip on these)

1. `decisions` (company status items) ≠ `decisions_waiting` (attention category) ≠ all-hands `decision` ≠ `add_decision_message` (the human's recorded decision).
2. `content` (human-readable text or null) vs `content_payload` (the structured part you should route/act on) in any event.
3. `message_type: "analysis"` is a helper artifact, not a valid classification.
4. `grand_parent_id` not `grandparent_id`; `assigneee_profile` not `assignee_profile`; `runned`/`added_to_kanban` are legacy flags, not state.
5. `delete_*` tools are for erroneous duplicates you created — closing work means finished+cost (tasks) or resolved/dismissed (items).
