# PWR API Reference v2 — endpoints, bearer tokens, inputs, outputs

> Repo: `~/Documents/codes/Pavel/W/pwr` (github.com/ValidatorAI/bonfire), branch
> `installation` @ **231bd9a** (2026-11-11). Base URL: `http://localhost:3000`.
> This version supersedes 2026-11-10 v1 and reflects the API-additions campaign
> (briefs A, C, D, B, T, GF, E — all merged): `ApprovalFlow`, `ProjectAdminService`,
> `FileReservationService`, `MessageUpdateService`, `UserAdminService`,
> `ProjectMembershipService`, `DirectRoomService`, `AiProfiles::Destroy`, and the
> `AiAdminEvents` concern now back BOTH web and API planes with identical
> semantics. Facts verified via `bin/rails routes`, controller source, and live
> probes on 2026-11-11. Token VALUES are never printed — only the env var names.

---

## 0. The three surfaces & access state (re-verified 2026-11-11)

| Surface | Protocol | Auth | State |
|---|---|---|---|
| `/api/*` REST JSON (ActionController::API) | REST | Bearer `OUTPUT_EVENTS_TOKEN` | **ENABLED + LIVE** (`DISABLE_API_ROUTES=false`, restarted): /api/health, /api/users, /api/projects, /api/reservations, /api/output_events, /api/tool_cal_logs, /api/messages?ids → 200 with token; 401 without |
| `/mcp`, `/action-mcp`, `/read-mcp`, `/knowledge-mcp`, `/task-mcp`, `/config-mcp` | JSON-RPC 2.0 (MCP) | Bearer `MCP_AUTH_TOKEN` + `Mcp-Session-Id` from `initialize` | LIVE — **171 / 150 / 79 / 29 / 8 / 16** tools |
| Web routes (`/rooms`, `/company/...`, approval member patches, ai-admin screens…) | HTML/Turbo | session cookie | LIVE (302 → sign-in) |

Health: `GET /up` (Rails) · `GET /api/health` → `{"status":"ok","app_version":…,"db":"up"}`.
The v1-era stale claim `GET /mcp/health` was removed from README (commit 2b800f2).

## 1. REST conventions (v2)

- Auth: `Authorization: Bearer <OUTPUT_EVENTS_TOKEN>`. Missing/wrong → 401
  `{"error":"Unauthorized"}` (identical shape, no oracle); token unset server-side
  → 500 `Server misconfigured`. ⚠ one shared secret for the whole plane — not
  per-user (see §1.4).
- **Actor attribution convention (new):** writes accept an optional
  `actor_user_id` / `user_id` / `user_name` (fuzzy-resolved), stamped into
  outbound events. NEVER defaults to `User.first`; absent → actor nil.
- Errors: `{error}` + status. Full set now in use: 400, 401, 403 (`not holder`,
  `profile not editable`, `tool sets not editable`), 404, 409 (`conflict` +
  `conflicting[]` for reservations; `open approvals exist`; `Email address is
  already in use`; `delivery not configured`), 410 (`expired`), 422 (validation
  sentences; `not author`; `system messages are admin-only`; `bots cannot be
  project members`; `Decision actor must be a human user`), 502 (transient
  delivery), 202 (typing; skills learn queued), 204 (deletes).
- Lists: `{count, page, per_page, <items>}` when paginated (default 40, cap
  200); flat messages batch cap 100 ids; output_events limit cap 500; rooms
  return bare arrays; tasks return `{count, tasks:[...]}`.
- Deletes → 204. `project_id` accepts **id OR slug** everywhere; message/task
  ids are globally unique (flat routes exist for exactly that).
- Nested duplication: rooms subtree exists flat (`/api/rooms/...`) and
  project-scoped (`/api/projects/:project_id/rooms/...`) — same handlers.
- **Redaction (new, tested):** `soul` → `soul_present`, mcp `bearer_token` →
  `bearer_token_present`, skill `skill_text` → `skill_text_present`; values
  never serialized. ⚠ Known open nuance: `ai_settings.setting_value` IS
  serialized (pre-existing read contract — the single flagged hardening item).

## 2. REST endpoint catalog (v2) — ★ marks new since v1

### 2.1 Projects, rooms, members, directs
| Endpoint | Inputs | Output / notes |
|---|---|---|
| `GET /api/projects` | – | array of `{id,name,slug,path,description,private,short_code,current_phase,progress_percent,roadmap,recently_completed,budget_total,budget_spent,created_at,updated_at,display_name}` |
| `POST /api/projects` ★ | `path` required; name?/description?/private?/short_code?; actor params | 201 `{…,created:true}`; duplicate path → **200 `created:false`** (idempotent via ProjectAdminService); project_created event carries slug+path ONLY (announce stays dumb) |
| `GET /api/projects/:id` · `PATCH/PUT/DELETE` ★(writes) | id or slug | 404 `Project not found`; DELETE → **409 `open approvals exist`** when the project's rooms hold pending approvals, else 204; PATCH fires project_updated with changed_fields |
| `GET /api/rooms` · `/:id` (flat + under projects) | – | `{id,name,type,description,private,parent_id,project_id,creator_id,archived_at,created_at,updated_at}` |
| `GET /api/rooms/:id/threads` | – | child rooms (`parent_id=room.id`), ordered |
| `GET /api/rooms/search?q=` | q required | name LIKE escaped, relevance-ranked; blank → 400 `Missing query param: q` |
| `GET /api/rooms/:id/members` ★ | – | `[{user_id,name,involvement}]` — parity with MCP get_room_members |
| `POST /api/rooms/:id/members` ★ | `user_id` OR `user_name` (fuzzy) | 201 `{already_member:false,user_id}` / 200 `already_member:true` no-op; room_member_added event (optional actor); **bots ALLOWED in rooms** |
| `DELETE /api/rooms/:room_id/members/:user_id` ★ | – | 204 idempotent |
| `GET /api/directs?with_user_id` ★ · `POST /api/directs` ★ | creator via `creator_user_id|actor_user_id`; `user_ids[]`; optional `message:{body}` | `{room:{…}, created:true|false}`; DirectRoomService = web transaction (find_or_create_for + grouped events room_created/direct_conversation_created/room_member_added×N under ONE group_id, only when new); repeat call → same room, created:false, ZERO new events |
| `GET/POST /api/projects/:pid/users` + `GET/POST /members`, `DELETE /members/:id` ★ | user ref | ProjectMembershipService: bots → 422 `bots cannot be project members`; existing → 200 already_member; events project_member_added (+ project_first_joined on first, shared group_id); DELETE 204 |

### 2.2 Messages, actions, decisions, approvals
| Endpoint | Inputs | Output / notes |
|---|---|---|
| `GET /api/rooms/:rid/messages` | page/per_page + ★ `include=body`, `creator_id`, `system=true|false`, `since`, `until`, `q` (body LIKE via joined rich_text, escaped) | `{count,[page,per_page,]messages:[{id,room_id,creator_id,creator_type,system,system_type,created_at,updated_at(,body when include=body)}]}` |
| `GET /api/messages?ids=1,2,…` ★ | cap 100, dedupe, unknown skipped | flat batch index (new) |
| `GET /api/messages/:id` (+nested) · `/:id/attachment` | disposition=attachment? | serialized message / raw bytes, 404 if none |
| `POST /api/rooms/:rid/messages` (+nested) | `user_id` must exist; ≥1 of body/attachment (400 if both blank) | 201; create_with_attachment!; auto client_message_id uuid |
| `PATCH/PUT /api/messages/:id` ★rule | body etc. | shared **MessageUpdateService**: `422 not author`; `system messages are admin-only` — REST ≡ MCP identical |
| `DELETE /api/messages/:id` | – | 204 |
| `POST /api/rooms/:rid/actions` | `user_id`, `action_type` ∈ typing_start/typing_stop | 202 `{status:"ok"}`; ActionCable; else 400 allowed-list |
| `POST /api/rooms/:rid/decisions` ★ | `user_id`, `approval_request_id`, `decision` ∈ approve/confirm/deny/cancel, note? | routes **ApprovalFlow**: transition + ApprovalRequestAction ledger + linked-attention resolution + auto-ADR (decision payloads) + output event + **room echo message**; response now includes `echo_message_id`; bot actor → 422 human-user error; already-resolved → idempotent (no double ledger/echo) |
| `GET/POST /api/rooms/:rid/approval_requests` (+nested) · `GET/PATCH/PUT/DELETE /api/approval_requests/:id` | create/PATCH: `message_id,request_type,status,requested_at,resolved_at,resolved_by_id,payload{}` | serialized incl. `decision_text` |

### 2.3 Topics, analysis, tasks, attention (unchanged unless ★)
| Endpoint | Inputs | Output |
|---|---|---|
| `GET/POST/PATCH/DELETE /api/topics[/:id]` | permit `project_id,parent_topic_id,name,related_topics,active,importance_level,memory,state,need_an_action,required_actions` | 422 validation |
| `GET/POST/PATCH/DELETE /api/message_analysis[/:id]` | `message_id,importance_level,message_content_summary,message_type,tags,is_a_response` | 1:1 unique per message_id |
| `GET/POST/PATCH/DELETE /api/room_history_topics[/:id]` (+ alias `/api/room_history`) | room/topic fields | snapshot objects |
| `GET/POST/PATCH/DELETE /api/message_topics[/:id]` | `message_id,topic_id` | link objects |
| `GET /api/tasks` (+ filters project/room/topic/dispatched/finished) · CRUD · `/:id/children` `/:parents` · `POST|PATCH /api/tasks/task_cost` (`task_id,token_used,usd_used`) | REST permit incl. `token_budget` + admin fields (`added_to_kanban`,`runned` legacy) | REST = admin-plane superset over MCP-locked update_ai_task |
| `GET/POST/PATCH/DELETE /api/attention_items[/:id]` | filters `category,status,project_id,room_id,user_id`; fields incl. status ∈ pending/resolved/dismissed | full row incl. `action_label,ai_confirm,resolved_at,resolved_by_id` (+ room-aware tagging from dbb95b8) |

### 2.4 Company status plane (unchanged + UI-side improvements only)
`company_status_periods` CRUD + `current`/`by_slug/:slug`/`by_name` (create
requires name; update requires period_id); `company_status_items` CRUD +
`by_period`/`advanced_filter`; permit list incl. percent/status/severity/impact/
evidence. e7dcce9 prioritization changes affect web views, not API payloads.

### 2.5 File reservations ★ (new — brief C)
| Endpoint | Inputs | Output |
|---|---|---|
| `GET /api/reservations` | `project_id`, `include_expired` | active scope hides expired (expiry honored even without the queue worker); rows: patterns, exclusive, holder{id,name}, expires_at, time_remaining |
| `POST /api/reservations` | project (id|slug), `patterns[]` globs, `holder_user_id`, exclusive?(true), reason?, ttl_seconds? | 201 · **409 `{"error":"conflict","conflicting":[…]}`** · 422 invalid patterns (blank/".."/absolute) · 422 unknown holder |
| `PATCH /api/reservations/:id` | holder_user_id | renew → 200 extended · **403 `not holder`** · **410 `expired`** · 404 |
| `DELETE /api/reservations/:id` | – | 204 always (idempotent release) |

### 2.6 Output events, audit, health ★ (new — brief GF)
| Endpoint | Inputs | Output / notes |
|---|---|---|
| `GET /api/output_events` | `event_type,event_id,group_id,synced,since,until,limit`(≤500) | `{count, output_events:[{id,event_type,event_id,group_id,event_data,synced,created_at,updated_at}]}` — event_data verbatim (assert knowledge_path/room_name/payloads) |
| `GET /api/output_events/:id` | – | 404 standard |
| `POST /api/output_events/:id/redeliver` | – | reuses DeliveryClient: OUTPUT_EVENTS_URL unset → **409 `delivery not configured`**; delivered → JSON `synced:true`; transient → **502**; permanent → **422**; never mutates event_data, never duplicates rows |
| `GET /api/tool_cal_logs` · `/:id` | `used_tool_name,project_id,room_id,topic_id,target_entity_id,attribution cols,start_date,end_date,limit` (between_dates/ordered scopes) | **READ-ONLY**; writes stay MCP (`create_tool_cal_log`) |
| `GET /api/health` | – | `{status:"ok",app_version,db:"up"}` |

### 2.7 Users ★ (new — brief B)
| Endpoint | Inputs | Output |
|---|---|---|
| `GET /api/users` | `include_bots` | active, ordered, without-bots default (web index parity) |
| `POST /api/users` | name, email_address, password?, role?, display_name? | 201 (display_name defaults to name; user_activated event + optional actor) · 422 validation · **409 `Email address is already in use`** |
| `GET/PATCH/PUT/DELETE /api/users/:id` · `POST|PATCH /api/users/:id/activate` | role/status updates mirror web | 200/204; UserAdminService shared with web |

### 2.8 AI-admin plane ★ (new mutations — brief E)
Mirror web ai_admin semantics 1:1 (shared AiAdminEvents; same guards; same
transactions; read-side allowlists — no secret values).
| Endpoint | Notes |
|---|---|
| `ai_profiles` CRUD + `POST /api/ai_profiles/:id/reset_ai_config` | create/update run the web transaction (normalize bot name → save! → `AiProfiles::BotSync(previous_bot…)`); **403 `profile not editable`**; toolset guard **403**; destroy via `AiProfiles::Destroy`; ai_profile_* events w/ optional actor; `soul` redacted |
| `ai_settings` CRUD | permit `label,setting_value` (⚠ value serialized — open item) |
| `mcps` CRUD | `bearer_token` → `bearer_token_present` |
| `tools` index/show + `PATCH /api/tools/:id/toggle` | web parity toggle |
| `skills` CRUD + `PATCH /:id/toggle_default` + `POST /api/skills/learn` | learn → 202 `{status:"queued"}`; `skill_text` → `skill_text_present` |
| `ai_profile_tools|ai_profile_skills|ai_profile_mcps` index/show (parent-filterable) + `PATCH /:id/toggle_enabled` | find-or-initialize then flip (web semantics) |
| `PATCH /api/ai_profiles/:profile_id/{tools|skills|mcps}/:tool_id/enabled` | flat aliases, same handlers |
| `POST /api/ai_admin/restart_w_bridge` | same `hermes gateway restart` op → 200 `{triggered:true}` / 500 `{triggered:false}` |
| `POST /api/ai_admin/reset_ai_config` | ConfigError/RecordInvalid/KeyError → 422 |

### 2.9 Per-project entities (v1, paths unchanged)
Long + short paths under `/api/projects/:project_id/…`: `todos`, `milestones`,
`bottlenecks`, `notes`, `adrs`, `knowledge_items`, `external_assets`,
`knowledge_activities`, `directory_items`, `all_hands_action_items|decisions|takeaways`,
`users`. Notable permits: todos `title,meta_text,completed,completed_at,position`;
adrs `identifier,title,status,decision_date,file_path`; assets `title,url,description`;
activities `actor_name,action_text,target_path`; directory `name,item_type,parent`.

### 1.4 Attribution caveat (updated)
REST is a shared-secret server plane: the "user" is whatever `user_id`/
`actor_user_id` you declare — treat it as a trusted-backend interface, not an
identity boundary. Trustworthy per-agent attribution remains on MCP, where the
acting client is the authenticated consumer (and human-only rules like
decisions are enforced by role checks, not by trust).

## 3. MCP surface (v2)

Transport unchanged: JSON-RPC 2.0 POST; headers
`Content-Type: application/json`, `Accept: application/json, text/event-stream`,
`Authorization: Bearer <MCP_AUTH_TOKEN>`, `Mcp-Session-Id` (from initialize;
serverInfo `space-mcp` 1.0.0, protocolVersion 2024-11-05). `tools/list` =
canonical names only (aliases callable but unlisted); domain errors come back as
`isError:true` text; scope/auth failures at HTTP/registry level. Fuzzy inputs
via `Mcp::FuzzyMatcher` (project-scoped user matching; ambiguity → candidate
error). Project/room/user name resolution extended (2b800f2: exact name/slug
matching).

Counts now: **/mcp 171 · /action-mcp 150 · /read-mcp 79 · /knowledge-mcp 29 ·
/task-mcp 8 · /config-mcp 16** (live recount 2026-11-11).

New tools (present + scope-verified):
| Tool | Scope | Contract |
|---|---|---|
| add_project / edit_project / delete_project | action | share ProjectAdminService with REST (no logic duplication); path idempotence; actor params STAMPED into events (T7); delete respects open-approvals guard |
| check_file_conflicts | action + read | `{conflicts:[…]}`; success even when empty |
| reserve_file / renew_file_reservation / release_file_reservation | action | bots ALLOWED (agents are this feature's users); ownership enforced server-side; conflict failure names holders + time remaining |
| edit_message | action | `message_id`, `body`, actor required; author-only; system msgs admin-only; shared MessageUpdateService ≡ REST (closes gap-ledger #3) |

Behavior changes to know:
- `add_message` / `add_action_message`: **room required** — the `|| Room.first`
  fallback is removed; missing room → `failure("Room not found: provide
  room_id or room_name")`. Sender rules unchanged: `user_id|user_name|
  bot_id|bot_name` (id wins; project-scoped fuzzy; only `body` required).
- `add_decision_message`: `user_id or user_name required` (contractual), bot →
  `Only human users can decide approval requests`, routes ApprovalFlow,
  response carries `echo_message_id`; DS-01/APP-07 invariants now
  server-enforced on every plane.
- `ai_question_asked` direction: the event means a HUMAN asked the AI a
  question — recorded only for human-authored messages that mention bots, land
  in a direct room with bots, or post with `mode:"ask"`; `bot_user_ids` = bots
  expected to answer. Bot-authored messages never emit it (AI→human questioning
  is the ai_confirm/confirm-card/approval mechanism instead). REST replay:
  plain-text `@name` does NOT count as a mention (rich-text attachables only) —
  use `mode:"ask"` or directs to trigger the human→AI wake.

Minimal probe:
```bash
TOK=$(grep '^MCP_AUTH_TOKEN' .env | cut -d= -f2- | tr -d '"')
curl -s -X POST http://localhost:3000/read-mcp \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOK" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## 4. Web routes (session cookie) — as v1, with one upgrade

Approval member patches (`/approval_requests/:id/{approve,confirm,deny,cancel}`)
now run the SAME ApprovalFlow as the API — meaning the HI click family and the
API decision path produce identical ledger + event + echo; equivalence is a
test target, not an assumption. Rest unchanged: attention resolve/dismiss,
pooling_messages long-poll, per-bot-key posting (`/rooms/:id/:bot_key/messages`),
boosts/searches/ask/clear, unfurl, rooms settings/involvement/clear,
opens/closeds/directs, company pages, ai-admin screens (thin wrappers over the
new services), qr/join, PWA + push, first-run.

## 5. REST ↔ MCP parity (v2 refreshed)

Covered on BOTH planes: projects CRUD (+409 guard), users, room/project
members, directs create/read, messages incl. EDIT (shared service), decisions
with echo + human-only enforcement, approvals, file reservations (REST + MCP;
MCP adds the read-side conflict check), topics/tasks/attention/company/all-hands/
knowledge families, output-event reads (REST; event writes remain server-side),
tool_cal_logs (REST read / MCP write — by design), AI-config (REST = full
mutations by design; MCP = read-only introspection by design).

Still **MCP-only**: room analytics (room_context_summary, room_decision_context,
room_evidence, room_economics), room_topic_tree, search_topics,
search_messages_of_room, loading messages, ai_confirm family, add_action_message,
knowledge_summary_items, knowledge_proposals semantics, tool_cal_log WRITES,
hello.
Still **web-only**: boosts, presence, unfurl render, PWA/push, first-run wizard.

## 6. Verification log

- 2026-11-11 (this doc): `bin/rails routes` expansion → all §2 rows; live 200s
  for /api/health, /api/users, /api/projects, /api/output_events,
  /api/tool_cal_logs, /api/messages?ids; 401 no-token; redeliver exercised
  (404 path); MCP recount 171/150/79/29/8/16 with all 8 new tool names
  confirmed on their scopes; scope-leak spot check: reserve_file via
  /read-mcp → refusal.
- Commit trail for this revision: 934dd45 (A projects) · 3650aab (D ApprovalFlow) ·
  a3cec12 (C reservations) · 17a2610 (B users/members/directs) · 2b800f2 (T tails) ·
  f52a72b (GF observability+messages) · 231bd9a (E ai-admin).
- Ops notes: reservation sweeper declared in `config/recurring.yml` requires a
  solid_queue worker (dev currently runs default :async — expiry semantics still
  hold via the model's `active` scope; sweeper is housekeeping); redeliver happy
  path needs `OUTPUT_EVENTS_URL` + a live sink.
- Open hardening item (only one): `ai_settings.setting_value` serialization.
- v1 preserved at `pwr-api-reference.v1.bak` beside this file.
