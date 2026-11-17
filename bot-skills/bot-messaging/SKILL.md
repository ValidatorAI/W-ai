---
name: bot-messaging
description: Use when posting to PWR rooms, threads, or private chats as a bot.
version: 0.1.0
author: siavash (drafted by Hermes)
license: MIT
metadata:
  hermes:
    tags: [pwr, bots, rooms, messaging]
    related_skills: [pwr-entities, bot-approvals]
---

# Bot room & private messaging

Purpose: the discipline of talking **as a bot** in PWR — routing, the loading-message lifecycle, formatting, and how your messages get consumed downstream. Procedures here are binding, not stylistic.

Source of quality: the same lifecycle coder/project-manager souls run in production; verified tool names: `add_loading_message`, `edit_loading_message`, `delete_loading_message`, `add_message`, `add_action_message`, `search_messages_of_room` (action/read surfaces per workspace soul's rooms row).

## Routing (where a reply belongs)

- A request from a room or thread gets its answer in that same room/thread, sent with `user_name: "<your-bot-profile>"`. Never reply only in logs.
- A private chat gets its answer in the private chat. Never paste private-chat content into a room; never carry another room's context into an answer (the room is the memory boundary — see pwr-entities).
- Questions the user must see, and status of in-flight work tied to a task/event, go through `add_action_message` (raised in the same room you received the input) — that is the platform's surfaced channel; free-floating prose gets missed.

## Loading-message lifecycle (required for any multi-step request)

1. **Start:** `add_loading_message` for the room; keep the returned loading message id.
2. **Every meaningful step:** `edit_loading_message` on that same loading message — what is being done now, what changed, what is next. Do NOT batch hidden operations without intermediate updates.
3. **Finish:** `delete_loading_message`, then `add_message` with the final result to the same room.
4. **Blocked:** immediately post a room update with the blocker details and the **exact** input/approval needed to unblock. Never leave a loading message spinning on a dead plan.

If the request came as an assigned AiTask with a `room_id`, the lifecycle runs in that room. No room at all (private chat or contextless task): skip loading messages there, but keep the same step-by-step visibility in the chat/task thread.

## Formatting (required)

- No Markdown. HTML tags only: `<ul>`, `<li>`, `<a>`, `<b>`.
- Always wrap code in `<pre>`.
- Verdict first, detail behind it. One subject per message; spell entity ids inline ("task 91", "milestone 12") so message analysis and topic linking can do their job — your messages are scored into `message_analysis` and attached to topics after the fact.

## What not to do

- Do not send the same content twice (dedupe via `tool_cal_logs` footprint + `search_messages_of_room` when unsure).
- Do not use `add_decision_message` yourself — it carries the human's decision, not yours (see bot-approvals).
- Do not chat socially; you are practical, precise, outcome-first.
- Do not mention ids without naming which kind ("37" is meaningless; "task 37" / "topic 37" is traceable).

## Worked example (room mention → result)

```
@coder fix the export
→ add_loading_message(room: Engineering)  [keep id 512]
→ edit_loading_message(512, "Reproduced: export crashes on empty date column")
→ edit_loading_message(512, "Patch written, running tests")
→ delete_loading_message(512)
→ add_message(room Engineering, user_name coder,
     "<b>Fixed.</b> Empty date column crashed export.py; guarded + test added.
      <pre>def month_export(d): ...</pre> Next: awaiting your run on staging.")
→ create_tool_cal_log(...) for each state-changing action
```
