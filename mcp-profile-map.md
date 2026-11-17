# PWR MCP Servers → Profile Attachment Map

Analyzed from the PWR source (`W/pwr`, 2026-11-09) — routes in `config/routes.rb`, registration in `app/services/mcp.rb`, scopes confirmed by booting the real registry (`bin/rails runner Mcp.load_tools!`). This is the plan for which Hermes profile should attach which MCP server.

## The six endpoints (real tool counts, canonical names)

| Endpoint | Scope | Canonical tools | What's in it |
|---|---|---|---|
| `/mcp` | all | 163 | everything, including config discovery |
| `/action-mcp` | action | 142 | all state-changing tools + list/get lookups (attention, status, projects, knowledge items, messaging, approvals, topic writes, task writes) |
| `/read-mcp` | read | 78 | read-only views: attention items, status, project items, all-hands, knowledge, room lookups, room context, approvals, topics/analysis/logs reads, tasks reads, config reads |
| `/knowledge-mcp` | knowledge | 29 | topics, message_topics, message_analysis, room_history_topics, tool_cal_logs (full CRUD) + `search_messages_of_room` |
| `/config-mcp` | config | 16 | discovery only: list/get for AI profiles, AI settings, MCPs, tools, skills, profile-tool/skill/mcp links |
| `/task-mcp` | task | 8 | `ai_tasks`, `get_ai_task`, `create_ai_task`, `update_ai_task`, `delete_ai_task`, `get_ai_task_children`, `get_ai_task_parents`, `ai_task_cost` |

Domain sizes on action/read: attention 23, company status 10, project items 12, all-hands 12, project knowledge 28, messaging/rooms 19, approvals 6, topics/analysis 28, tasks 8, config 16, hello 1.

## Facts from the source that change the design

1. **`/mcp` is not privileged — it's the superset.** Attaching it gives a profile everything including config discovery; attaching scoped servers is strictly narrower. Prefer scoped endpoints per profile.
2. **Read-only is a naming fiction.** `ai_task_cost` (a write) is registered into the read scope due to a prefix-rule miss in `app/services/mcp.rb:231`; read tools are deliberately exposed on `/action-mcp` too (lookup-before-write). Don't rely on `/read-mcp` for hard sandboxing.
3. **`/config-mcp` is 16 read-only discovery tools** — safe to attach broadly; it changes nothing.
4. **All profiles share one `MCP_AUTH_TOKEN`** (`mcp_controller.rb:37`) — PWR does not distinguish which profile calls; identity comes from tool arguments (`user_name`/`bot_name`) and Hermes-side config. So least-privilege = choose endpoints per profile; per-profile API keys would require a server change (noted as future work).
5. **Auth headers interpolate per profile**: every profile that attaches a PWR server needs `MCP_...KEY` (or the token var your block uses) in **that profile's own `.env`**, not just the default profile's.

## Attachment map (target state)

| Profile | attach | do NOT attach | why |
|---|---|---|---|
| coder | `/action-mcp`, `/read-mcp`, `/task-mcp`, `/knowledge-mcp` | `/config-mcp` | implements (messaging/approval writes), works+routes tasks, logs & links topics |
| market_research | same 4 as coder | `/config-mcp` | evidence digests post to rooms, record to knowledge, log actions |
| business_analyst | same 4 | `/config-mcp` | defines/edits todos & records, routes children, logs |
| project_manager | same 4 | `/config-mcp` | plans (milestones/todos/bottlenecks writes), routes/sequences tasks |
| w_ai | 4 above + `/config-mcp` | `/mcp` | front door needs membership lookups + profile discovery ("which bot does X") |
| workspace | `/action-mcp`, `/read-mcp`, `/task-mcp`, `/knowledge-mcp`, `/config-mcp` | `/mcp` | router must see everything writable + verify profile attachments (its soul's precondition tool `list_ai_profile_mcps` lives on config-mcp) |
| ai_settings | `/config-mcp`, `/read-mcp`, `/task-mcp` | `/action-mcp`, `/mcp` | owns the config axis; reads registry, may receive/finish config tasks; its soul explicitly keeps PWR writes out — actual mutations are Hermes-side (`hermes mcp`/`hermes config`, file edits) |
| message_analyzer | `/knowledge-mcp`, `/task-mcp` (current state = correct) | `/action-mcp` | writes only topics/analyses/logs; no room posts |

`/mcp` is for humans/debugging only — no profile should need it once scoped servers are attached.

## Current state vs target (drift to fix)

| Profile | now | gap |
|---|---|---|
| coder / market_research / business_analyst / project_manager | W-space → `/mcp` only | **over-privileged** (config discovery + everything); switch to the 4 scoped servers |
| w_ai | W-space → `/mcp` only | same; switch to 4 + config |
| workspace | `Knowledge` → `/knowledge-mcp` only | **broken for its job**: no task-mcp (can't route/close), no action/read (can't act, can't dedupe via approvals/items) — add action, read, task, config |
| ai_settings | W-space → `/mcp` only | **over-privileged for a config auditor**: drop action surface, attach config + read + task |
| message_analyzer | knowledge + task | ✓ matches target |

## Target config blocks (copy per profile)

```yaml
# ~/.hermes/profiles/<bot>/config.yaml — mcp_servers:
  pwr-action:
    url: http://localhost:3000/action-mcp
    headers:
      Authorization: Bearer ${MCP_...KEY}
  pwr-read:
    url: http://localhost:3000/read-mcp
    headers:
      Authorization: Bearer ${MCP_...KEY}
  pwr-task:
    url: http://localhost:3000/task-mcp
    headers:
      Authorization: Bearer ${MCP_...KEY}
  pwr-knowledge:
    url: http://localhost:3000/knowledge-mcp
    headers:
      Authorization: Bearer ${MCP_...KEY}
  pwr-config:            # only: w_ai, workspace, ai_settings (read-mcp covers nothing here)
    url: http://localhost:3000/config-mcp
    headers:
      Authorization: Bearer ${MCP_...KEY}
```

ai_settings gets `pwr-config`, `pwr-read`, `pwr-task` only. message_analyzer keeps current two. Remove each profile's `W-space`/`/mcp` entry when its scoped set is in and verified (`hermes -p <profile> mcp test pwr-task` etc.).

## Follow-ups (server-side, not blocking)

- Fix the `ai_task_cost` scope leak (`mcp.rb:231` prefix list should include `ai_task_cost`).
- Per-profile tokens if we ever want real server-side authorization — one shared token means endpoint choice is hygiene, not enforcement.

## Token maintenance (verified 2026-11-09)

Server auth = `MCP_AUTH_TOKEN` in `pwr/.env` (currently the shared dev value `your-mcp-token`). Every profile's PWR servers use `${MCP_KNOWLEDGE_API_KEY}` (message_analyzer additionally `${MCP_TASK_MANAGEMENT_API_KEY}`); these live in **each profile's own .env** and must equal the server value. When PWR's token rotates, update `MCP_KNOWLEDGE_API_KEY` (+`MCP_TASK_MANAGEMENT_API_KEY`) in every `~/.hermes/profiles/*/.env` and re-run `hermes -p <profile> mcp test pwr-task`. The retired W-space blocks referenced a never-defined `MCP_W_SPACE_API_KEY` — that variable is now unused.

