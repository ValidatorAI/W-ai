# Copilot brief GF — Observability APIs (G) + Message plane upgrades (F) + 2 micro-fixes

Repo: /home/siavash/Documents/codes/Pavel/W/pwr (branch installation, HEAD 2b800f2)
After this PR, every remaining blocked test row becomes directly assertable:
OUT-01…08, HI-15, PJ-07 (observability), body-scan families AN-13/MS-05/09,
MSG-08 edit on MCP (gap-ledger #3 closed), plus project-tool attribution and
service duplication cleanups.

READ FIRST (source of truth for semantics — do not guess):
  app/services/output_events/recorder.rb, deduplicator.rb, delivery_client.rb
  (Transient/PermanentDeliveryError; how `synced` gets marked), content_builder.rb,
  knowledge_path_resolver.rb, message_emission_policy.rb; app/models/output_event.rb;
  app/models/tool_cal_log.rb (table tool_cal_logs; used_tool_name + created_date
  required; between_dates/ordered scopes); app/controllers/api/messages_controller.rb;
  app/services/mcp/tools/projects.rb + app/controllers/api/projects_controller.rb.
Auth plane: Api::BaseController Bearer OUTPUT_EVENTS_TOKEN; MCP tools use the repo
success/failure envelopes + Registry scopes; lookups find_by (never raise).

--- TASKS G ---

G1. Output-event read + manual redeliver (REST)
  routes: under namespace :api → resources :output_events, only: %i[index show] do
            post :redeliver, on: :member end
  GET /api/output_events filters: event_type, event_id, group_id, synced=true|false,
    since/until (created_at), limit (default 50, cap 500). Response:
    {"count":N,"output_events":[{id,event_type,event_id,group_id,event_data,
     synced,created_at,updated_at}]} — event_data included verbatim (it is the
     payload the tests assert: knowledge_path, room_name, member ids…).
  GET /api/output_events/:id → same object; 404 {error}.
  POST /api/output_events/:id/redeliver:
    - resolve OUTPUT_EVENTS_URL/config like DeliveryClient does; unset →
      409 {"error":"delivery not configured"}
    - invoke the SAME DeliveryClient.deliver path the reconcile flow uses (no
      re-record, no duplicated rows); success → return the event JSON with
      synced:true (whatever marks synced today must be reused); Transient → 502
      {"error":message}, Permanent → 422. Never mutate event_data.
  Tests: filter matrix sample; redeliver success/502/409; NO new output_event rows.

G2. Tool-call-log reads (REST mirror of the knowledge-mcp plane)
  routes: resources :tool_cal_logs, only: %i[index show]
  GET /api/tool_cal_logs filters: used_tool_name, project_id, room_id, topic_id,
    target_entity_id, created_by (whatever attribution columns exist — check the
    table; include them all in serialize), start_date/end_date via the existing
    between_dates scope, limit/order (ToolCalLog.ordered default). Response
    {"count":N,"tool_cal_logs":[full row as_json]} (as_json(only:) listing every
    real column — verify against schema, do not invent).
  READ-ONLY. Writes stay MCP (create/update/delete tools) so the agent logging
  discipline remains the single entry. 404 shape standard.
  Tests: create via MCP tool then read via REST (cross-plane parity); filters.

G3. Health route
  GET /api/health → {"status":"ok","app_version":ENV["APP_VERSION"],"db":"up"}
  (single Project.count-style query is fine; keep it dependency-safe).
  Update README to list BOTH /up (Rails) and /api/health (API plane). No
  /mcp/health route — settled earlier.

--- TASKS F ---

F1. Message list ergonomics (Api::MessagesController#index, both nested + new flat)
  - add flat index: GET /api/messages?ids=137,164,182 (cap 100; dedupe; unknown
    ids silently skipped — response notes skipped count).
  - include param: include=body adds "body": message.plain_text_body to each
    serialized message (check Message for the plain-text method the MCP tools
    use — reuse it; if body lives in action_text_rich_texts only, join
    preload it — no N+1).
  - filters (room-scoped): creator_id, system=true|false, since/until (created_at),
    q → case-insensitive LIKE against the same body text source, escaped like
    rooms#search does (reuse sanitize_like pattern — copy the method into a
    shared concern if both controllers need it).
  - response wrapper unchanged ({count,[page,per_page,]messages}).
  Tests: include=body shape; ids batch with one unknown → skipped count; q finds
  a phrase incl. unicode; creator filter.

F2. edit_message MCP tool (gap-ledger #3 closure)
  In app/services/mcp/tools/messaging.rb, mirroring AddMessageTool conventions:
    name "edit_message", aliases ["EditMessage"]
    args: message_id (required), body (required), user_id|user_name (required,
    one of; resolve via existing resolve_user)
    rules: resolved user MUST equal message.creator else failure("not author");
    system messages (creator = system user) editable only by admins → else
    failure("system messages are admin-only"); deleted/missing id → failure.
    Use the SAME update path REST PATCH uses (creator checks live in the model/
    controller — READ Api::MessagesController#update first; if REST lacks the
    author rule, implement the rule in a tiny MessageUpdateService used by BOTH
    so planes can't diverge — and say so in the commit message).
    Register scopes: all+action. Success envelope returns updated fields +
    edited_at/updated_at.
  Tests: author edit OK; non-author refused; system message by admin OK, by bot
  refused; REST and MCP produce identical stored rows for the same edit.

--- TASKS T7/T8 (micro-fixes from last review) ---

T7. add_project/edit_project/delete_project must attribute: resolve the already
  accepted user_name|actor_user_id and pass actor into OutputEvents::Recorder.record
  (currently nil). Same for Api::ProjectsController#create when those params are
  provided. Test: event row carries actor id.

T8. Extract ProjectAdminService (create/update/destroy incl. the 409 guard) used
  by BOTH Api::ProjectsController and the MCP tools (projects.rb re-implements
  logic today). Keep controller/tool responses byte-identical to current tests.

--- ACCEPTANCE ---
  Unblocks: OUT-01…OUT-08 (direct reads + redeliver), HI-15 (payload), PJ-07,
  XD-03/OR-* fast REST reads (no MCP coupling), AN-13/MS-05/09/16 body scans in
  one call, MSG-08/gap-ledger #3, T7 attribution (AUT-06 spirit), T8 drift-proof.
  Gates: bin/rails test green for touched controllers/services/tools.

--- NON-GOALS ---
  - No attempts/status columns on output_events (synced boolean stays; add
    nothing to its schema).
  - No full-text search engine; room-scoped LIKE is the contract.
  - No REST writes for tool_cal_logs; no admin auth model changes.
  - Do not touch MessageEmissionPolicy semantics or dedupe windows.
  - No per-endpoint rate limits (dev plane).
